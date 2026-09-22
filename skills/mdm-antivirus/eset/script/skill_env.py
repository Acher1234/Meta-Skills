"""ESET skill credentials."""

from __future__ import annotations

from pathlib import Path

from common.skill_env_export import SkillEnv


class EsetSkillEnv(SkillEnv):
    required_keys = ("ESET_URL", "ESET_USERNAME", "ESET_PASSWORD")

    def __init__(self) -> None:
        super().__init__("eset", Path(__file__))

    def verify(self, values: dict[str, str]) -> dict[str, str]:
        return self.verify_required_keys(values)


ENV = EsetSkillEnv()
