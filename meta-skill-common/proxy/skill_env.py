"""Proxy settings loaded from a skill ``.env``."""

from __future__ import annotations

import os
from collections.abc import Iterable

from common.proxy.proxy import PROXY_ENV_KEYS, Proxy, resolve_proxy
from common.skill_env import SkillEnv


class ProxySkillEnv(SkillEnv):
    """Optional proxy keys, the root of the shared ``SkillEnv`` mixins.

    :class:`~common.http.skill_env.HttpSkillEnv` and
    :class:`~common.browser.skill_env.BrowserSkillEnv` inherit from it, and a skill
    can inherit from both (``class MySkillEnv(HttpSkillEnv, BrowserSkillEnv)``).
    Each ``verify()`` calls ``super().verify(values)`` and merges, so every
    helper keeps its keys exactly once. A skill subclass does the same::

        def verify(self, values):
            return {**super().verify(values), **my_verified_keys}
    """

    def verify(self, values: dict[str, str]) -> dict[str, str]:
        verified = self.keep_keys(values, PROXY_ENV_KEYS)
        try:
            resolve_proxy(verified)
        except (RuntimeError, ValueError) as exc:
            raise SystemExit(f"{exc} — edit {self.env_path()}") from exc
        return verified

    @staticmethod
    def keep_keys(values: dict[str, str], keys: Iterable[str]) -> dict[str, str]:
        return {key: values[key].strip() for key in keys if key in values}

    def env_values(self, keys: Iterable[str]) -> dict[str, str]:
        """Skill ``.env`` values over the process environment, for *keys*."""
        values: dict[str, str] = {}
        for key in keys:
            if key in os.environ:
                values[key] = os.environ[key]
            if key in self.env:
                values[key] = self.env[key]
        return values

    def proxy_values(self) -> dict[str, str]:
        return self.env_values(PROXY_ENV_KEYS)

    def proxy(self) -> Proxy | None:
        return resolve_proxy(self.proxy_values())

    def proxy_env(self) -> dict[str, str]:
        """Proxy variables to export before running an external CLI or SDK."""
        proxy = self.proxy()
        return {} if proxy is None else proxy.env()
