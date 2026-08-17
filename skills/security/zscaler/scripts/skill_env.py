"""Zscaler skill credentials — nested JSON keys as SECTION__FIELD."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping
from pathlib import Path

from common.skill_env_export import SkillEnv, env_load_main

KEYS = (
    "ZPA__CLIENT_ID",
    "ZPA__CLIENT_SECRET",
    "ZPA__CUSTOMER_ID",
    "ZPA__CLOUD",
    "ZPA__MICROTENANT_ID",
    "ZIA__USERNAME",
    "ZIA__PASSWORD",
    "ZIA__API_KEY",
    "ZIA__CLOUD",
    "ZIDENTITY__CLIENT_ID",
    "ZIDENTITY__CLIENT_SECRET",
    "ZIDENTITY__VANITY_DOMAIN",
    "ZIDENTITY__CLOUD",
    "ZIDENTITY__CUSTOMER_ID",
)


def _mask(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 4:
        return "…"
    return value[:2] + "…"


class ZscalerSkillEnv(SkillEnv):
    def __init__(self) -> None:
        super().__init__("zscaler", Path(__file__))

    def apply_defaults(self, values: Mapping[str, str]) -> dict[str, str]:
        out = dict(values)
        if not out.get("ZPA__CLOUD", "").strip():
            out["ZPA__CLOUD"] = "PRODUCTION"
        if not out.get("ZIA__CLOUD", "").strip():
            out["ZIA__CLOUD"] = "zscaler"
        return out

    def verify(self, values: dict[str, str]) -> dict[str, str]:
        return {key: values.get(key, "").strip() for key in KEYS}

    def as_config(self) -> dict:
        return {
            "zpa": {
                "client_id": self.env.get("ZPA__CLIENT_ID", ""),
                "client_secret": self.env.get("ZPA__CLIENT_SECRET", ""),
                "customer_id": self.env.get("ZPA__CUSTOMER_ID", ""),
                "cloud": self.env.get("ZPA__CLOUD", ""),
                "microtenant_id": self.env.get("ZPA__MICROTENANT_ID", ""),
            },
            "zia": {
                "username": self.env.get("ZIA__USERNAME", ""),
                "password": self.env.get("ZIA__PASSWORD", ""),
                "api_key": self.env.get("ZIA__API_KEY", ""),
                "cloud": self.env.get("ZIA__CLOUD", ""),
            },
            "zidentity": {
                "client_id": self.env.get("ZIDENTITY__CLIENT_ID", ""),
                "client_secret": self.env.get("ZIDENTITY__CLIENT_SECRET", ""),
                "vanity_domain": self.env.get("ZIDENTITY__VANITY_DOMAIN", ""),
                "cloud": self.env.get("ZIDENTITY__CLOUD", ""),
                "customer_id": self.env.get("ZIDENTITY__CUSTOMER_ID", ""),
            },
        }

    def masked_config(self) -> dict:
        cfg = self.as_config()
        cfg["zpa"]["client_secret"] = _mask(cfg["zpa"]["client_secret"])
        cfg["zia"]["password"] = _mask(cfg["zia"]["password"])
        cfg["zia"]["api_key"] = _mask(cfg["zia"]["api_key"])
        cfg["zidentity"]["client_secret"] = _mask(cfg["zidentity"]["client_secret"])
        return cfg

    @staticmethod
    def env(_: argparse.Namespace) -> int:
        print(
            json.dumps(
                {
                    "env_path": str(ENV.env_path()),
                    "CURRENT_SKILL_DIRECTORY": str(ENV.env_cred().workspace),
                    "config": ENV.masked_config(),
                },
                indent=2,
                default=str,
            )
        )
        return 0

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        sub.add_parser("env", help="Validate SkillCred .env (no network)").set_defaults(
            func=ZscalerSkillEnv.env
        )


ENV = ZscalerSkillEnv()


if __name__ == "__main__":
    raise SystemExit(env_load_main(ENV, sys.argv[1:]))
