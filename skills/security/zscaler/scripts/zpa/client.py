"""ZPA legacy client — LegacyZPAClient from SkillCred .env, optional overrides."""

from __future__ import annotations

import argparse
import json
from typing import Any

from zscaler.oneapi_client import LegacyZPAClient

from skill_env import ENV

_REQUIRED = ("client_id", "client_secret", "customer_id", "cloud")


def _merge(override: dict[str, Any] | None) -> dict[str, str]:
    merged = {**ENV.as_config()["zpa"], **(override or {})}
    return {key: (merged.get(key) or "").strip() for key in _REQUIRED}


def get_client(cfg: dict[str, Any] | None = None) -> LegacyZPAClient:
    merged = _merge(cfg)
    missing = [key for key in _REQUIRED if not merged[key]]
    if missing:
        raise SystemExit(f"Missing ZPA credentials: {', '.join(missing)}")
    return LegacyZPAClient(
        {
            "clientId": merged["client_id"],
            "clientSecret": merged["client_secret"],
            "customerId": merged["customer_id"],
            "cloud": merged["cloud"],
            "logging": {"enabled": False, "verbose": False},
        }
    )


def cfg_from_args(args: argparse.Namespace) -> dict[str, str]:
    cfg: dict[str, str] = {}
    for key in _REQUIRED:
        value = getattr(args, key, None)
        if value:
            cfg[key] = value
    return cfg


def add_overrides(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--client-id", help="Override ZPA__CLIENT_ID")
    parser.add_argument("--client-secret", help="Override ZPA__CLIENT_SECRET")
    parser.add_argument("--customer-id", help="Override ZPA__CUSTOMER_ID")
    parser.add_argument("--cloud", help="Override ZPA__CLOUD")


def dump(data: Any) -> None:
    print(json.dumps(data, indent=2, default=str))
