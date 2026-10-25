"""Browser settings loaded from a skill ``.env``."""

from __future__ import annotations

from common.browser.browser import BROWSER_ENV_KEYS, Browser, debug_enabled
from common.proxy.skill_env import ProxySkillEnv


class BrowserSkillEnv(ProxySkillEnv):
    """Optional browser and proxy keys shared by skills that launch :class:`Browser`."""

    def verify(self, values: dict[str, str]) -> dict[str, str]:
        return {**super().verify(values), **self.keep_keys(values, BROWSER_ENV_KEYS)}

    def browser_values(self) -> dict[str, str]:
        """Skill ``.env`` values over the process environment."""
        return self.env_values(BROWSER_ENV_KEYS)

    def debug(self) -> bool:
        return debug_enabled(self.browser_values())

    def need_remote_port(self) -> str | None:
        """Chromium remote debugging port when both env vars are set."""
        return Browser.remote_debug_port(self.browser_values())

    def get_proxy(self) -> dict[str, str] | None:
        return Browser.get_proxy(self.browser_values())

    def dataimpulse_proxy_configuration(self) -> dict[str, str]:
        return Browser.dataimpulse_proxy_configuration(self.browser_values())
