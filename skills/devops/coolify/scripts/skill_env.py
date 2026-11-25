"""Coolify skill credentials."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from common.skill_env import SkillEnv, env_load_main

CONTEXT_NAME = re.compile(r"[A-Za-z0-9._-]+")


class CoolifySkillEnv(SkillEnv):
    required_keys = ("COOLIFY_URL", "COOLIFY_TOKEN", "COOLIFY_CONTEXT")

    def __init__(self) -> None:
        super().__init__("coolify", Path(__file__))

    def verify(self, values: dict[str, str]) -> dict[str, str]:
        verified = self.verify_required_keys(values)
        url = verified["COOLIFY_URL"].rstrip("/")
        if not url.startswith(("http://", "https://")):
            raise SystemExit(
                f"COOLIFY_URL must start with http:// or https:// — edit {self.env_path()}"
            )
        if "coolify.example.com" in url:
            raise SystemExit(
                f"COOLIFY_URL still has placeholder — edit {self.env_path()}"
            )
        if not CONTEXT_NAME.fullmatch(verified["COOLIFY_CONTEXT"]):
            raise SystemExit(
                "COOLIFY_CONTEXT may only contain letters, digits, '.', '_' and '-' "
                f"— edit {self.env_path()}"
            )
        verified["COOLIFY_URL"] = url
        return verified

    def url(self) -> str:
        return self.env["COOLIFY_URL"]

    def token(self) -> str:
        return self.env["COOLIFY_TOKEN"]

    def context(self) -> str:
        return self.env["COOLIFY_CONTEXT"]


ENV = CoolifySkillEnv()

if __name__ == "__main__":
    raise SystemExit(env_load_main(ENV, sys.argv[1:]))
