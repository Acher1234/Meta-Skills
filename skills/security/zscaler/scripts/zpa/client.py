"""ZPA legacy client — LegacyZPAClient from SkillCred .env."""

from __future__ import annotations

import argparse
import json
from typing import Any

from zscaler.oneapi_client import LegacyZPAClient

from skill_env import ENV


class ZpaClient:
    required = ("client_id", "client_secret", "customer_id", "cloud")
    client: LegacyZPAClient | None = None

    def get_client(self) -> LegacyZPAClient:
        if self.client is None:
            merged = {**ENV.as_config()["zpa"]}
            config = {key: (merged.get(key) or "").strip() for key in self.required}
            missing = [key for key in self.required if not config[key]]
            if missing:
                raise SystemExit(f"Missing ZPA credentials: {', '.join(missing)}")
            payload: dict[str, Any] = {
                "clientId": config["client_id"],
                "clientSecret": config["client_secret"],
                "customerId": config["customer_id"],
                "cloud": config["cloud"],
                "logging": {"enabled": False, "verbose": False},
            }
            microtenant = (merged.get("microtenant_id") or "").strip()
            if microtenant:
                payload["microtenantId"] = microtenant
            self.client = LegacyZPAClient(payload)
        return self.client

    @staticmethod
    def dump(data: Any) -> None:
        print(json.dumps(data, indent=2, default=str))

    @staticmethod
    def records(items: Any) -> list[dict[str, Any]]:
        return [
            item.as_dict() if hasattr(item, "as_dict") else dict(item)
            for item in (items or [])
        ]

    @staticmethod
    def _to_dict(item: Any) -> dict[str, Any]:
        if item is None:
            return {}
        if hasattr(item, "as_dict"):
            return item.as_dict()
        if isinstance(item, dict):
            return dict(item)
        return dict(item)
