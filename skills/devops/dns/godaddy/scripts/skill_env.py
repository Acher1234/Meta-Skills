"""GoDaddy skill credentials."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from common.skill_env_export import SkillEnv


class GodaddySkillEnv(SkillEnv):
    DEFAULT_BASE_URL = "https://api.godaddy.com"
    required_keys = ("GODADDY_PAT",)

    def __init__(self) -> None:
        super().__init__("godaddy", Path(__file__))


    def apply_defaults(self, values: Mapping[str, str]) -> dict[str, str]:
        out = dict(values)
        out.setdefault("BASE_URL", self.DEFAULT_BASE_URL)
        return out

    def verify(self, values: dict[str, str]) -> dict[str, str]:
        verified = self.verify_required_keys(values)
        verified["BASE_URL"] = values.get("BASE_URL", self.DEFAULT_BASE_URL).rstrip("/")
        return verified

    def pat(self) -> str:
        return self.env["GODADDY_PAT"]

    def base_url(self) -> str:
        return self.env["BASE_URL"]


ENV = GodaddySkillEnv()
