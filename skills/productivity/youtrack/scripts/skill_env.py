"""YouTrack skill credentials."""

from __future__ import annotations

import sys
from pathlib import Path

from common.skill_env_export import SkillEnv, env_load_main


class YoutrackSkillEnv(SkillEnv):
    required_keys = ("URL", "API_TOKEN")

    def __init__(self) -> None:
        super().__init__("youtrack", Path(__file__))

    def verify(self, values: dict[str, str]) -> dict[str, str]:
        verified = self.verify_required_keys(values)
        verified["URL"] = verified["URL"].rstrip("/")
        return verified

    def url(self) -> str:
        return self.env["URL"]

    def api_token(self) -> str:
        return self.env["API_TOKEN"]


ENV = YoutrackSkillEnv()

if __name__ == "__main__":
    raise SystemExit(env_load_main(ENV, sys.argv[1:]))
