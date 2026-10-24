"""Playwright browser session. Default engine is Camoufox.

Subclass and override :meth:`Browser.start` to launch Chromium (or another
Playwright browser). :meth:`Browser.shutdown` runs after the window closes,
which is where a Chromium subclass stops the Playwright driver.

``DEBUG_WITH_UI_DISPLAYED=1`` (also ``true``, ``yes``, ``on``) shows the browser
window. Otherwise the session stays headless.

``ENABLE_REMOTE_DEBUG_PORT`` and ``REMOTE_DEBUG_PORT`` together add
``--remote-debugging-port`` on the Chromium launch.

The proxy comes from :mod:`common.proxy`: filling in ``DATAIMPULSE_USERNAME`` /
``DATAIMPULSE_PASSWORD`` or ``PROXY_URL`` turns it on, ``PROXY_TYPE`` forces a
provider or disables it (``none``). :meth:`Browser.get_proxy`
builds the dict passed to Camoufox and Chromium.

Skills that open a browser subclass :class:`common.browser.skill_env.BrowserSkillEnv`
so those variables are read from the skill ``.env``.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Mapping
from typing import Any

from common.proxy import PROXY_ENV_KEYS, dataimpulse_proxy, resolve_proxy

_DEBUG_ON = {"1", "true", "yes", "on"}
BROWSER_ENV_KEYS = (
    "DEBUG_WITH_UI_DISPLAYED",
    "ENABLE_REMOTE_DEBUG_PORT",
    "REMOTE_DEBUG_PORT",
    *PROXY_ENV_KEYS,
)


def debug_enabled(environ: Mapping[str, str] | None = None) -> bool:
    source = os.environ if environ is None else environ
    return source.get("DEBUG_WITH_UI_DISPLAYED", "").strip().lower() in _DEBUG_ON


class Browser:
    """Context manager around a Playwright browser.

    Default launch uses Camoufox. A Chromium subclass replaces :meth:`start`
    and stops its driver in :meth:`shutdown`::

        class ChromiumBrowser(Browser):
            def start(self):
                from playwright.sync_api import sync_playwright

                self._playwright = sync_playwright().start()
                return self._playwright.chromium.launch(**self.chromium_launch_options())

            def shutdown(self):
                playwright = getattr(self, "_playwright", None)
                self._playwright = None
                if playwright is not None:
                    playwright.stop()
    """

    def __init__(
        self,
        *,
        debug: bool | None = None,
        environ: Mapping[str, str] | None = None,
        **launch_options: Any,
    ) -> None:
        source = os.environ if environ is None else environ
        self.debug = debug_enabled(source) if debug is None else debug
        self.launch_options = launch_options
        self.proxy = self.get_proxy(source)
        self._remote_debug_port = self.remote_debug_port(source)
        self.browser: Any = None
        self._engine: Any = None

    @staticmethod
    def get_proxy(environ: Mapping[str, str] | None = None) -> dict[str, str] | None:
        """Proxy dict for the current ``PROXY_TYPE``, or ``None`` when unset."""
        proxy = resolve_proxy(environ)
        return None if proxy is None else proxy.playwright()

    @staticmethod
    def remote_debug_port(environ: Mapping[str, str] | None = None) -> str | None:
        """Chromium remote debugging port when both env vars are enabled."""
        source = os.environ if environ is None else environ
        enabled = source.get("ENABLE_REMOTE_DEBUG_PORT", "").strip().lower() in _DEBUG_ON
        port = source.get("REMOTE_DEBUG_PORT", "").strip()
        if not enabled or not port:
            return None
        if not port.isdigit():
            raise RuntimeError("REMOTE_DEBUG_PORT must be a port number")
        return port

    @staticmethod
    def dataimpulse_proxy_configuration(
        environ: Mapping[str, str] | None = None,
    ) -> dict[str, str]:
        """Playwright proxy dict from the DataImpulse environment variables."""
        source = os.environ if environ is None else environ
        return dataimpulse_proxy(source).playwright()

    @property
    def headless(self) -> bool:
        return not self.debug

    def chromium_launch_options(self) -> dict[str, Any]:
        """Launch kwargs for ``playwright.chromium.launch``, including the proxy."""
        options: dict[str, Any] = {"headless": self.headless}
        if self.proxy is not None:
            options["proxy"] = self.proxy
        port = self._remote_debug_port
        if port is not None:
            options["args"] = [f"--remote-debugging-port={port}"]
        return options

    def __enter__(self) -> Browser:
        try:
            self.browser = self.start()
        except Exception:
            self.stop()
            raise
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.stop()

    def start(self) -> Any:
        """Launch Camoufox and return its Playwright browser."""
        try:
            from camoufox.sync_api import Camoufox
        except ImportError as exc:
            raise ImportError(
                "camoufox is required for Browser. Install it in the shared venv."
            ) from exc

        options = dict(self.launch_options)
        options.setdefault("headless", self.headless)
        if self.proxy is not None:
            options.setdefault("proxy", self.proxy)
        engine = Camoufox(**options)
        try:
            browser = engine.__enter__()
        except Exception:
            engine.__exit__(*sys.exc_info())
            raise
        self._engine = engine
        return browser

    def new_page(self, **kwargs: Any) -> Any:
        if self.browser is None:
            raise RuntimeError("browser is not started")
        return self.browser.new_page(**kwargs)

    def stop(self) -> None:
        engine = self._engine
        browser = self.browser
        self._engine = None
        self.browser = None
        try:
            if engine is not None:
                engine.__exit__(None, None, None)
            elif browser is not None:
                browser.close()
        finally:
            self.shutdown()

    def shutdown(self) -> None:
        """Extra teardown for subclasses (Playwright driver, etc.)."""
