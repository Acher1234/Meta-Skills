"""HTTP client shared by skills that call a REST API directly.

:class:`HttpClient` wraps a ``requests.Session``:

- ``base_url`` joined with relative paths; absolute URLs pass through.
- ``None`` / ``""`` query params are dropped.
- JSON is decoded when the body parses, text otherwise, ``None`` when empty.
  ``expect_json=True`` raises :class:`HttpError` on an HTML page (WAF,
  Cloudflare challenge) instead of returning it.
- ``throttle`` spaces requests by a minimum delay (polite public APIs).
- Network errors and 502 / 503 / 504 are retried for idempotent methods,
  429 for every method, honouring ``Retry-After``.
- Status ``>= 400`` raises :class:`HttpError`.
- :meth:`HttpClient.download` streams to a file and can gunzip.
- :meth:`HttpClient.load_browser_cookies` reuses a Playwright session.
- ``impersonate="chrome"`` swaps the session for a ``curl_cffi`` one that copies
  a real browser TLS fingerprint, for sites whose WAF (Radware, Cloudflare bot
  management) blocks ``requests`` even with a browser User-Agent. Needs
  ``curl_cffi`` in the skill requirements.txt.

Settings come from the environment (or a skill ``.env`` through
:class:`common.http.skill_env.HttpSkillEnv`):

``HTTP_TIMEOUT`` (seconds, default 30; wins over ``timeout=``), ``HTTP_RETRIES`` (default 2),
``HTTP_IMPERSONATE`` (``curl_cffi`` browser target such as ``chrome``; wins over ``impersonate=``),
``HTTP_USER_AGENT`` (default: a desktop Chrome; wins over ``user_agent=``), ``HTTP_VERIFY_SSL`` (``0`` disables verification),
``HTTP_CA_BUNDLE`` (custom CA file), ``HTTP_DEBUG`` (log each request on
stderr), and the proxy variables of :mod:`common.proxy`.
"""

from __future__ import annotations

import os
import sys
import time
import zlib
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from common.proxy import PROXY_ENV_KEYS, resolve_proxy

try:
    import requests
except ImportError as exc:  # pragma: no cover - depends on the skill venv
    raise ImportError(
        "requests is required for common.http. Add it to the skill requirements.txt."
    ) from exc

HTTP_ENV_KEYS = (
    "HTTP_TIMEOUT",
    "HTTP_RETRIES",
    "HTTP_USER_AGENT",
    "HTTP_IMPERSONATE",
    "HTTP_VERIFY_SSL",
    "HTTP_CA_BUNDLE",
    "HTTP_DEBUG",
    *PROXY_ENV_KEYS,
)
# A common desktop browser, so sites do not single out scripts. HTTP_USER_AGENT overrides it.
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
)
DEFAULT_TIMEOUT = 30.0
DEFAULT_RETRIES = 2

_TRUE = {"1", "true", "yes", "on"}
_FALSE = {"0", "false", "no", "off"}
_IDEMPOTENT = {"GET", "HEAD", "OPTIONS", "PUT", "DELETE"}
_RETRY_STATUS = {502, 503, 504}
_MAX_RETRY_AFTER = 60.0
_GZIP_MAGIC = b"\x1f\x8b"


class HttpError(RuntimeError):
    """HTTP status ``>= 400``, or a body that is not what the caller expected."""

    def __init__(
        self,
        status: int,
        body: Any,
        url: str,
        method: str = "GET",
        reason: str = "",
        response: requests.Response | None = None,
    ):
        self.status = status
        self.response = response
        self.body = body
        self.url = url
        self.method = method
        snippet = body if isinstance(body, str) else repr(body)
        snippet = " ".join(snippet.split())[:300]
        detail = reason or f"HTTP {status}"
        super().__init__(f"{method} {url} -> {detail}: {snippet}")


def _setting(source: Mapping[str, str], key: str) -> str:
    return source.get(key, "").strip()


def _number(source: Mapping[str, str], key: str, default: float) -> float:
    raw = _setting(source, key)
    if not raw:
        return default
    try:
        value = float(raw)
    except ValueError as exc:
        raise RuntimeError(f"{key} must be a number") from exc
    if value < 0:
        raise RuntimeError(f"{key} must be >= 0")
    return value


def _flag(source: Mapping[str, str], key: str, default: bool) -> bool:
    raw = _setting(source, key).lower()
    if not raw:
        return default
    if raw in _TRUE:
        return True
    if raw in _FALSE:
        return False
    raise RuntimeError(f"{key} must be 1 or 0")


def clean_params(params: Mapping[str, Any] | None) -> dict[str, Any] | None:
    """Drop ``None`` and ``""`` values so optional CLI flags are not sent."""
    if not params:
        return None
    return {key: value for key, value in params.items() if value is not None and value != ""}


def cookies_from_browser(cookies: Iterable[Mapping[str, Any]]) -> requests.cookies.RequestsCookieJar:
    """Cookie jar from Playwright ``context.cookies()`` dicts."""
    jar = requests.cookies.RequestsCookieJar()
    for cookie in cookies:
        expires = cookie.get("expires")
        jar.set(
            cookie["name"],
            cookie["value"],
            domain=cookie.get("domain", ""),
            path=cookie.get("path", "/"),
            secure=bool(cookie.get("secure", False)),
            expires=int(expires) if expires and expires > 0 else None,
            rest={"HttpOnly": None} if cookie.get("httpOnly") else {},
        )
    return jar


class HttpClient:
    """``requests.Session`` with proxy, retries, throttle, and JSON decoding."""

    def __init__(
        self,
        base_url: str = "",
        *,
        environ: Mapping[str, str] | None = None,
        user_agent: str | None = None,
        headers: Mapping[str, str] | None = None,
        timeout: float | None = None,
        retries: int | None = None,
        throttle: float = 0.0,
        verify: bool | str | None = None,
        impersonate: str | None = None,
        session: requests.Session | None = None,
    ) -> None:
        source = os.environ if environ is None else environ
        self.base_url = base_url.rstrip("/")
        # timeout= is the caller default; HTTP_TIMEOUT wins over it.
        self.timeout = _number(source, "HTTP_TIMEOUT", DEFAULT_TIMEOUT if timeout is None else timeout)
        self.retries = int(_number(source, "HTTP_RETRIES", DEFAULT_RETRIES)) if retries is None else retries
        self.throttle = throttle
        self.debug = _flag(source, "HTTP_DEBUG", False)
        self._last_request = 0.0

        self.impersonate = _setting(source, "HTTP_IMPERSONATE") or impersonate or None
        self._network_errors: tuple[type[BaseException], ...] = (requests.ConnectionError, requests.Timeout)
        if session is None and self.impersonate:
            session = self._impersonated_session(self.impersonate)
        self.session = session or requests.Session()
        # An impersonated session already sends the User-Agent matching its fingerprint.
        agent = _setting(source, "HTTP_USER_AGENT") or user_agent
        if agent or not self.impersonate:
            self.session.headers["User-Agent"] = agent or DEFAULT_USER_AGENT
        if headers:
            self.session.headers.update(headers)
        self.session.verify = self._verify(source) if verify is None else verify

        self.proxy = resolve_proxy(source)
        if self.proxy is not None:
            self.session.proxies.update(self.proxy.requests())

    def _impersonated_session(self, target: str) -> Any:
        try:
            from curl_cffi import requests as curl_requests
        except ImportError as exc:
            raise ImportError(
                "curl_cffi is required for impersonate=. Add it to the skill requirements.txt."
            ) from exc
        self._network_errors += (curl_requests.exceptions.ConnectionError, curl_requests.exceptions.Timeout)
        return curl_requests.Session(impersonate=target)

    @staticmethod
    def _verify(source: Mapping[str, str]) -> bool | str:
        bundle = _setting(source, "HTTP_CA_BUNDLE")
        if bundle:
            path = Path(bundle).expanduser()
            if not path.is_file():
                raise RuntimeError(f"HTTP_CA_BUNDLE not found: {path}")
            return str(path)
        if not _flag(source, "HTTP_VERIFY_SSL", True):
            return False
        try:
            import certifi
        except ImportError:
            return True
        return certifi.where()

    def __enter__(self) -> HttpClient:
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()

    def close(self) -> None:
        self.session.close()

    def url(self, path: str) -> str:
        if path.startswith(("http://", "https://")) or not self.base_url:
            return path
        return f"{self.base_url}/{path.lstrip('/')}"

    def load_browser_cookies(self, source: Any) -> None:
        """Copy cookies from a Playwright context (or its ``cookies()`` list)."""
        cookies = source.cookies() if callable(getattr(source, "cookies", None)) else source
        self.session.cookies.update(cookies_from_browser(cookies))

    # Requests

    def get(self, path: str, **kwargs: Any) -> Any:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> Any:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> Any:
        return self.request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> Any:
        return self.request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> Any:
        return self.request("DELETE", path, **kwargs)

    def request(self, method: str, path: str, *, expect_json: bool = False, **kwargs: Any) -> Any:
        """Send and decode. Keyword arguments are those of :meth:`send`."""
        return self.decode(self.send(method, path, **kwargs), expect_json=expect_json)

    def send(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json: Any = None,
        data: Any = None,
        headers: Mapping[str, str] | None = None,
        timeout: float | None = None,
        stream: bool = False,
    ) -> requests.Response:
        """Send with throttle and retries; raise :class:`HttpError` on ``>= 400``."""
        method = method.upper()
        url = self.url(path)
        attempt = 0
        while True:
            self._wait_throttle()
            started = time.monotonic()
            try:
                response = self.session.request(
                    method,
                    url,
                    params=clean_params(params),
                    json=json,
                    data=data,
                    headers=dict(headers) if headers else None,
                    timeout=self.timeout if timeout is None else timeout,
                    stream=stream,
                )
            except self._network_errors as exc:
                self._log(method, url, type(exc).__name__, started)
                if attempt < self.retries and method in _IDEMPOTENT:
                    attempt += 1
                    time.sleep(self._backoff(attempt))
                    continue
                raise
            self._log(method, url, response.status_code, started)
            if attempt < self.retries and self._should_retry(method, response.status_code):
                attempt += 1
                delay = self._retry_after(response)
                if delay is None:
                    delay = self._backoff(attempt)
                response.close()
                time.sleep(delay)
                continue
            if response.status_code >= 400:
                raise HttpError(response.status_code, self._body(response), url, method, response=response)
            return response

    def decode(self, response: requests.Response, *, expect_json: bool = False) -> Any:
        """JSON when it parses, text otherwise, ``None`` for an empty body."""
        if response.status_code == 204 or not response.content:
            return None
        content_type = response.headers.get("Content-Type", "").lower()
        try:
            return response.json()
        except ValueError:
            if expect_json:
                reason = f"expected JSON, got {content_type or 'unknown content type'}"
                raise HttpError(
                    response.status_code, response.text, response.url, response.request.method, reason
                ) from None
            return response.text

    def download(
        self,
        path: str,
        dest: str | Path,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        gunzip: bool = False,
        max_bytes: int | None = None,
        chunk_size: int = 1 << 16,
    ) -> Path:
        """Stream *path* to *dest*. ``gunzip`` inflates a gzip body (``.gz`` file)."""
        target = Path(dest).expanduser()
        target.parent.mkdir(parents=True, exist_ok=True)
        partial = target.with_name(target.name + ".part")
        response = self.send("GET", path, params=params, headers=headers, stream=True)
        written = 0
        inflater = None
        try:
            with response, partial.open("wb") as handle:
                for chunk in response.iter_content(chunk_size):
                    if not chunk:
                        continue
                    if gunzip and inflater is None and written == 0:
                        if chunk.startswith(_GZIP_MAGIC):
                            inflater = zlib.decompressobj(16 + zlib.MAX_WBITS)
                    out = inflater.decompress(chunk) if inflater is not None else chunk
                    written += len(out)
                    if max_bytes is not None and written > max_bytes:
                        raise HttpError(
                            response.status_code, "", response.url, "GET",
                            f"download larger than {max_bytes} bytes",
                        )
                    handle.write(out)
                if inflater is not None:
                    handle.write(inflater.flush())
            partial.replace(target)
        except BaseException:
            partial.unlink(missing_ok=True)
            raise
        return target

    # Internals

    def _wait_throttle(self) -> None:
        if self.throttle <= 0:
            return
        delay = self._last_request + self.throttle - time.monotonic()
        if delay > 0:
            time.sleep(delay)
        self._last_request = time.monotonic()

    @staticmethod
    def _should_retry(method: str, status: int) -> bool:
        if status == 429:
            return True
        return status in _RETRY_STATUS and method in _IDEMPOTENT

    @staticmethod
    def _retry_after(response: requests.Response) -> float | None:
        raw = response.headers.get("Retry-After", "").strip()
        if not raw:
            return None
        try:
            return min(max(float(raw), 0.0), _MAX_RETRY_AFTER)
        except ValueError:
            return None

    @staticmethod
    def _backoff(attempt: int) -> float:
        return min(0.5 * 2 ** (attempt - 1), _MAX_RETRY_AFTER)

    @staticmethod
    def _body(response: requests.Response) -> Any:
        try:
            return response.json()
        except ValueError:
            return response.text

    def _log(self, method: str, url: str, status: Any, started: float) -> None:
        if not self.debug:
            return
        elapsed = (time.monotonic() - started) * 1000
        print(f"[http] {method} {url} -> {status} ({elapsed:.0f} ms)", file=sys.stderr)
