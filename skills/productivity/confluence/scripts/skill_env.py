"""Confluence skill credentials."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

from common.skill_cred import WORKSPACE_ENV
from common.skill_env_export import SkillEnv, emit_env_load, env_load_main

OPTIONAL_EXPORT_KEYS = (
    "CONFLUENCE_EMAIL",
    "CONFLUENCE_PROFILE",
    "CONFLUENCE_READ_ONLY",
    "CONFLUENCE_FORCE_CLOUD",
    "CONFLUENCE_LINK_STYLE",
)


class ConfluenceSkillEnv(SkillEnv):
    required_keys = (
        "CONFLUENCE_DOMAIN",
        "CONFLUENCE_API_PATH",
        "CONFLUENCE_AUTH_TYPE",
        "CONFLUENCE_API_TOKEN",
    )

    def __init__(self) -> None:
        super().__init__("confluence", Path(__file__))

    def verify(self, values: dict[str, str]) -> dict[str, str]:
        verified = self.verify_required_keys(values)
        auth = values.get("CONFLUENCE_AUTH_TYPE", "").strip().lower()
        if auth == "basic":
            email = values.get("CONFLUENCE_EMAIL", "").strip()
            if not email:
                raise SystemExit(
                    f"Missing CONFLUENCE_EMAIL — edit {self.env_path()} "
                    f"(CURRENT_SKILL_DIRECTORY={os.environ.get(WORKSPACE_ENV, '')!r})"
                )
            verified["CONFLUENCE_EMAIL"] = email
        return verified

    def emit_shell_exports(self, *, shell: str = "auto") -> str:
        values = self.read_env()
        exports = dict(self.verify(values))
        for key in OPTIONAL_EXPORT_KEYS:
            raw = values.get(key, "").strip()
            if raw and key not in exports:
                exports[key] = raw
        exports["CURRENT_SKILL_DIRECTORY"] = str(self.env_cred().workspace)
        return emit_env_load(exports, shell=shell)


ENV = ConfluenceSkillEnv()


def confluence_cli_path() -> str | None:
    return shutil.which("confluence")


if __name__ == "__main__":
    raise SystemExit(env_load_main(ENV, sys.argv[1:]))
