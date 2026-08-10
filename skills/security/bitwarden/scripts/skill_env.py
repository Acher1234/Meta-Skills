"""Bitwarden skill credentials."""

from __future__ import annotations

import sys
from pathlib import Path

from common.skill_env_export import SkillEnv, env_load_main


class BitwardenSkillEnv(SkillEnv):
    required_keys = ("BW_SERVER", "BW_CLIENTID", "BW_CLIENTSECRET", "BW_PASSWORD")

    def __init__(self) -> None:
        super().__init__("bitwarden", Path(__file__))

    def verify(self, values: dict[str, str]) -> dict[str, str]:
        verified = self.verify_required_keys(values)
        server = verified["BW_SERVER"].rstrip("/")
        if "vault.example.com" in server:
            raise SystemExit(
                f"BW_SERVER still has placeholder — edit {self.env_path()}"
            )
        verified["BW_SERVER"] = server
        extra_ca = values.get("NODE_EXTRA_CA_CERTS", "").strip()
        if extra_ca:
            verified["NODE_EXTRA_CA_CERTS"] = extra_ca
        return verified

    def server(self) -> str:
        return self.env["BW_SERVER"]

    def client_id(self) -> str:
        return self.env["BW_CLIENTID"]

    def client_secret(self) -> str:
        return self.env["BW_CLIENTSECRET"]

    def password(self) -> str:
        return self.env["BW_PASSWORD"]


ENV = BitwardenSkillEnv()

if __name__ == "__main__":
    raise SystemExit(env_load_main(ENV, sys.argv[1:]))
