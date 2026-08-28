"""Elasticsearch skill credentials."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from common.skill_env_export import SkillEnv, env_load_main


class ElasticSkillEnv(SkillEnv):
    required_keys = ("URL", "USERNAME", "PASSWORD")

    def __init__(self) -> None:
        super().__init__("elastic", Path(__file__))

    def verify(self, values: dict[str, str]) -> dict[str, str]:
        verified = self.verify_required_keys(values)
        verified["URL"] = verified["URL"].rstrip("/")
        return verified

    def url(self) -> str:
        return self.env["URL"]

    def username(self) -> str:
        return self.env["USERNAME"]

    def password(self) -> str:
        return self.env["PASSWORD"]


ENV = ElasticSkillEnv()


def env(_: argparse.Namespace) -> int:
    print(
        json.dumps(
            {
                "env_path": str(ENV.env_path()),
                "exists": ENV.env_path().is_file(),
                "CURRENT_SKILL_DIRECTORY": str(ENV.env_cred().workspace),
                "URL": ENV.url(),
                "USERNAME": ENV.username(),
            },
            indent=2,
            default=str,
        )
    )
    return 0


def register(sub: argparse._SubParsersAction) -> None:
    sub.add_parser("env", help="Validate .env (no network)").set_defaults(func=env)


if __name__ == "__main__":
    raise SystemExit(env_load_main(ENV, sys.argv[1:]))
