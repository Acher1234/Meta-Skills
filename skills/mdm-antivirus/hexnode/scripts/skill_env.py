"""Hexnode skill credentials."""

from __future__ import annotations

import sys
from collections.abc import Mapping
from pathlib import Path

from common.skill_env_export import SkillEnv, env_load_main


class HexnodeSkillEnv(SkillEnv):
    required_keys = ("HEXNODE_API_KEY", "HEXNODE_BASE_URL")

    def __init__(self) -> None:
        super().__init__("hexnode", Path(__file__))

    def apply_defaults(self, values: Mapping[str, str]) -> dict[str, str]:
        out = dict(values)
        base = out.get("HEXNODE_BASE_URL", "").strip()
        portal = out.get("HEXNODE_PORTAL", "").strip()
        if not base and portal:
            out["HEXNODE_BASE_URL"] = f"https://{portal}.hexnodemdm.com/api/v1"
        return out

    def verify(self, values: dict[str, str]) -> dict[str, str]:
        verified = self.verify_required_keys(values)
        base = verified["HEXNODE_BASE_URL"].rstrip("/")
        if "yourportal" in base:
            raise SystemExit(
                f"HEXNODE_BASE_URL still has placeholder — edit {self.env_path()}"
            )
        verified["HEXNODE_BASE_URL"] = base
        return verified

    def api_key(self) -> str:
        return self.env["HEXNODE_API_KEY"]

    def base_url(self) -> str:
        return self.env["HEXNODE_BASE_URL"]


ENV = HexnodeSkillEnv()

if __name__ == "__main__":
    raise SystemExit(env_load_main(ENV, sys.argv[1:]))
