"""logo.dev skill credentials."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from common.skill_env_export import SkillEnv, env_load_main


class LogoDevSkillEnv(SkillEnv):
    required_keys = ("API_KEY",)

    def __init__(self) -> None:
        super().__init__("logo-dev-finder", Path(__file__))

    def verify(self, values: dict[str, str]) -> dict[str, str]:
        return self.verify_required_keys(values)

    def api_key(self) -> str:
        return self.env["API_KEY"]

    @staticmethod
    def env(_: argparse.Namespace) -> int:
        key = ENV.api_key()
        print(
            json.dumps(
                {
                    "env_path": str(ENV.env_path()),
                    "CURRENT_SKILL_DIRECTORY": str(ENV.env_cred().workspace),
                    "API_KEY": key[:4] + "…" if len(key) > 4 else "…",
                },
                indent=2,
                default=str,
            )
        )
        return 0

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        sub.add_parser("env", help="Validate SkillCred .env (no network)").set_defaults(
            func=LogoDevSkillEnv.env
        )


ENV = LogoDevSkillEnv()


if __name__ == "__main__":
    raise SystemExit(env_load_main(ENV, sys.argv[1:]))
