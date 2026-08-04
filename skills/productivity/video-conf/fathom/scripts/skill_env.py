"""Fathom skill credentials."""

from __future__ import annotations

import sys
from pathlib import Path

from common.skill_env_export import SkillEnv, env_load_main


class FathomSkillEnv(SkillEnv):
    required_keys = ("FATHOM_API_KEY",)

    def __init__(self) -> None:
        super().__init__("fathom", Path(__file__))

    def verify(self, values: dict[str, str]) -> dict[str, str]:
        return self.verify_required_keys(values)


ENV = FathomSkillEnv()

if __name__ == "__main__":
    raise SystemExit(env_load_main(ENV, sys.argv[1:]))
