"""Proxy settings shared by :mod:`common.browser` and :mod:`common.http`.

``PROXY_TYPE`` selects the provider. When it is empty, the proxy is turned on
from the keys that are filled in (see :func:`detect_proxy_type`):

- ``DATAIMPULSE_USERNAME`` or ``DATAIMPULSE_PASSWORD`` set: ``dataimpulse``.
- ``PROXY_URL`` set: ``socks5`` for a ``socks5://`` URL, ``http`` otherwise.
- nothing set: no proxy.

``PROXY_TYPE=none`` (also ``off``, ``direct``) keeps the keys but disables the proxy.

Providers:

- ``dataimpulse``: ``DATAIMPULSE_USERNAME``, ``DATAIMPULSE_PASSWORD``,
  ``DATAIMPULSE_GW``, and ``DATAIMPULSE_PROXY_PORT`` must all be set.
  ``PROXY_COUNTRY`` (e.g. ``il``) appends DataImpulse's ``__cr.<country>``
  suffix to the login.
- ``http`` / ``socks5``: ``PROXY_URL`` (``host:port`` or ``scheme://host:port``),
  with optional ``PROXY_USERNAME`` / ``PROXY_PASSWORD``.
- ``system``: the proxy of the machine (``HTTPS_PROXY`` / ``HTTP_PROXY`` /
  ``ALL_PROXY``, or the macOS / Windows network settings).

``NO_PROXY`` lists hosts that bypass the proxy (comma-separated).

:func:`resolve_proxy` returns a :class:`Proxy` that renders itself for each
consumer: :meth:`Proxy.playwright` (Camoufox / Chromium), :meth:`Proxy.requests`
(``requests.Session.proxies``), and :meth:`Proxy.env` (variables to export
before running an external CLI or SDK).
"""

from __future__ import annotations

import os
import urllib.request
from collections.abc import Mapping
from dataclasses import dataclass
from urllib.parse import quote, unquote, urlsplit

DATAIMPULSE = "dataimpulse"
DATAIMPULSE_ENV_KEYS = (
    "DATAIMPULSE_USERNAME",
    "DATAIMPULSE_PASSWORD",
    "DATAIMPULSE_GW",
    "DATAIMPULSE_PROXY_PORT",
)
PROXY_ENV_KEYS = (
    "PROXY_TYPE",
    "PROXY_URL",
    "PROXY_USERNAME",
    "PROXY_PASSWORD",
    "PROXY_COUNTRY",
    "NO_PROXY",
    *DATAIMPULSE_ENV_KEYS,
)
_URL_TYPES = {"http": ("http", "https"), "socks5": ("socks5", "socks5h")}
_DISABLED = {"none", "off", "direct", "0", "false", "no"}


@dataclass(frozen=True)
class Proxy:
    """One proxy server. ``server`` is ``scheme://host:port`` without credentials."""

    server: str
    username: str = ""
    password: str = ""
    no_proxy: str = ""

    @property
    def scheme(self) -> str:
        return urlsplit(self.server).scheme

    def url(self, *, socks_remote_dns: bool = False) -> str:
        """Server URL with percent-encoded credentials.

        ``socks_remote_dns`` turns ``socks5://`` into ``socks5h://`` so DNS is
        resolved by the proxy (what ``requests`` needs for geo-located exits).
        """
        scheme, _, host = self.server.partition("://")
        if socks_remote_dns and scheme == "socks5":
            scheme = "socks5h"
        if not self.username:
            return f"{scheme}://{host}"
        credentials = quote(self.username, safe="")
        if self.password:
            credentials += ":" + quote(self.password, safe="")
        return f"{scheme}://{credentials}@{host}"

    def playwright(self) -> dict[str, str]:
        """Proxy dict for Camoufox / ``playwright.chromium.launch``."""
        options = {"server": self.server}
        if self.username:
            options["username"] = self.username
            options["password"] = self.password
        if self.no_proxy:
            options["bypass"] = self.no_proxy
        return options

    def requests(self) -> dict[str, str]:
        """Mapping for ``requests.Session.proxies``."""
        url = self.url(socks_remote_dns=True)
        return {"http": url, "https": url}

    def env(self) -> dict[str, str]:
        """Proxy variables for an external CLI or SDK (upper and lower case)."""
        url = self.url()
        values: dict[str, str] = {}
        for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"):
            values[key] = url
            values[key.lower()] = url
        if self.no_proxy:
            values["NO_PROXY"] = self.no_proxy
            values["no_proxy"] = self.no_proxy
        return values


def resolve_proxy(environ: Mapping[str, str] | None = None) -> Proxy | None:
    """Proxy for the current ``PROXY_TYPE``, or ``None`` when unset."""
    source = os.environ if environ is None else environ
    proxy_type = source.get("PROXY_TYPE", "").strip().lower() or detect_proxy_type(source)
    no_proxy = source.get("NO_PROXY", "").strip()
    if not proxy_type or proxy_type in _DISABLED:
        return None
    if proxy_type == DATAIMPULSE:
        return dataimpulse_proxy(source, no_proxy=no_proxy)
    if proxy_type in _URL_TYPES:
        return url_proxy(proxy_type, source, no_proxy=no_proxy)
    if proxy_type == "system":
        return system_proxy(no_proxy=no_proxy)
    raise ValueError(f"unsupported PROXY_TYPE: {proxy_type}")


def detect_proxy_type(source: Mapping[str, str]) -> str:
    """Provider implied by the filled-in keys when ``PROXY_TYPE`` is empty.

    ``DATAIMPULSE_GW`` and ``DATAIMPULSE_PROXY_PORT`` have defaults in the
    ``.env.example`` files, so only the login or password turns DataImpulse on.
    """
    dataimpulse = any(
        source.get(key, "").strip() for key in ("DATAIMPULSE_USERNAME", "DATAIMPULSE_PASSWORD")
    )
    url = source.get("PROXY_URL", "").strip()
    if dataimpulse and url:
        raise RuntimeError(
            "Both PROXY_URL and DATAIMPULSE_* are set: choose one with PROXY_TYPE"
        )
    if dataimpulse:
        return DATAIMPULSE
    if url:
        return "socks5" if url.lower().startswith(("socks5://", "socks5h://")) else "http"
    return ""


def dataimpulse_proxy(source: Mapping[str, str], *, no_proxy: str = "") -> Proxy:
    values = {key: source.get(key, "").strip() for key in DATAIMPULSE_ENV_KEYS}
    missing = [key for key, value in values.items() if not value]
    if missing:
        raise RuntimeError("PROXY_TYPE=dataimpulse requires " + ", ".join(missing))

    port = values["DATAIMPULSE_PROXY_PORT"]
    if not port.isdigit():
        raise RuntimeError("DATAIMPULSE_PROXY_PORT must be a port number")

    gateway = values["DATAIMPULSE_GW"]
    if "://" in gateway:
        scheme, _, host = gateway.partition("://")
    else:
        scheme, host = "http", gateway
    host = host.rstrip("/")
    if ":" not in host:
        host = f"{host}:{port}"

    username = values["DATAIMPULSE_USERNAME"]
    country = source.get("PROXY_COUNTRY", "").strip().lower()
    if country and "__cr." not in username:
        username = f"{username}__cr.{country}"
    return Proxy(
        server=f"{scheme}://{host}",
        username=username,
        password=values["DATAIMPULSE_PASSWORD"],
        no_proxy=no_proxy,
    )


def url_proxy(proxy_type: str, source: Mapping[str, str], *, no_proxy: str = "") -> Proxy:
    raw = source.get("PROXY_URL", "").strip()
    if not raw:
        raise RuntimeError(f"PROXY_TYPE={proxy_type} requires PROXY_URL")
    if "://" not in raw:
        raw = f"{proxy_type}://{raw}"
    proxy = _parse_proxy_url(raw, no_proxy=no_proxy)
    if proxy.scheme not in _URL_TYPES[proxy_type]:
        raise RuntimeError(
            f"PROXY_URL scheme {proxy.scheme!r} does not match PROXY_TYPE={proxy_type}"
        )
    username = source.get("PROXY_USERNAME", "").strip() or proxy.username
    password = source.get("PROXY_PASSWORD", "").strip() or proxy.password
    return Proxy(proxy.server, username, password, no_proxy)


def system_proxy(*, no_proxy: str = "") -> Proxy:
    """Machine proxy from the environment or the OS network settings."""
    proxies = urllib.request.getproxies()
    for key in ("https", "http", "all"):
        if proxies.get(key):
            raw = proxies[key]
            if "://" not in raw:
                raw = f"http://{raw}"
            no_proxy = no_proxy or proxies.get("no", "")
            return _parse_proxy_url(raw, no_proxy=no_proxy)
    raise RuntimeError("PROXY_TYPE=system but no system proxy is configured")


def _parse_proxy_url(raw: str, *, no_proxy: str = "") -> Proxy:
    parts = urlsplit(raw)
    if not parts.hostname:
        raise RuntimeError(f"invalid proxy URL: {raw!r}")
    host = parts.hostname
    if ":" in host:
        host = f"[{host}]"
    if parts.port is not None:
        host = f"{host}:{parts.port}"
    return Proxy(
        server=f"{parts.scheme}://{host}",
        username=unquote(parts.username or ""),
        password=unquote(parts.password or ""),
        no_proxy=no_proxy,
    )
