"""Hexnode skill credentials."""

from __future__ import annotations

from pathlib import Path

from common.skill_env_export import SkillEnv


class HexnodeSkillEnv(SkillEnv):
    required_keys = ("HEXNODE_API_KEY", "HEXNODE_BASE_URL")

    def __init__(self) -> None:
        super().__init__("hexnode", Path(__file__))

    def verify(self, values: dict[str, str]) -> dict[str, str]:
        return self.verify_required_keys(values)


ENV = HexnodeSkillEnv()
