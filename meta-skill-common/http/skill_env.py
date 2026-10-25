"""HTTP settings loaded from a skill ``.env``."""

from __future__ import annotations

from common.http.client import HTTP_ENV_KEYS
from common.proxy.skill_env import ProxySkillEnv


class HttpSkillEnv(ProxySkillEnv):
    """Optional ``HTTP_*`` and proxy keys shared by skills that use :class:`HttpClient`.

    The env only provides settings; the skill builds its client::

        HttpClient(base_url, environ=ENV.http_values(), headers=…, timeout=…)
    """

    def verify(self, values: dict[str, str]) -> dict[str, str]:
        return {**super().verify(values), **self.keep_keys(values, HTTP_ENV_KEYS)}

    def http_values(self) -> dict[str, str]:
        """Skill ``.env`` values over the process environment."""
        return self.env_values(HTTP_ENV_KEYS)
