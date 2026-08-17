"""ZIA legacy client — LegacyZIAClient from SkillCred .env, optional overrides."""

from __future__ import annotations

import argparse
import json
from typing import Any

from zscaler.oneapi_client import LegacyZIAClient

from skill_env import ENV


class ZiaClient:
    required = ("username", "password", "api_key", "cloud")

    def __init__(self, cfg: dict[str, Any] | None = None):
        self.cfg = cfg or {}

    def get_client(self, cfg: dict[str, Any] | None = None) -> LegacyZIAClient:
        merged = {**ENV.as_config()["zia"], **self.cfg, **(cfg or {})}
        config = {key: (merged.get(key) or "").strip() for key in self.required}
        missing = [key for key in self.required if not config[key]]
        if missing:
            raise SystemExit(f"Missing ZIA credentials: {', '.join(missing)}")
        return LegacyZIAClient(
            {**config, "logging": {"enabled": False, "verbose": False}}
        )

    @staticmethod
    def cfg_from_args(args: argparse.Namespace) -> dict[str, str]:
        cfg: dict[str, str] = {}
        for key in ZiaClient.required:
            value = getattr(args, key, None)
            if value:
                cfg[key] = value
        return cfg

    @staticmethod
    def add_overrides(parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--username", help="Override ZIA__USERNAME")
        parser.add_argument("--password", help="Override ZIA__PASSWORD")
        parser.add_argument("--api-key", help="Override ZIA__API_KEY")
        parser.add_argument("--cloud", help="Override ZIA__CLOUD")

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

    @staticmethod
    def _activate_api(client: Any) -> Any:
        api = getattr(client.zia, "activate", None)
        if api is not None:
            return api
        from zscaler.zia.activate import ActivationAPI

        return ActivationAPI(client.zia.request_executor)

    def activation_status(self) -> dict[str, Any]:
        with self.get_client() as client:
            result, _, err = self._activate_api(client).status()
            if err:
                raise RuntimeError(f"Failed to get ZIA activation status: {err}")
            return self._to_dict(result)

    def activate_changes(self) -> dict[str, Any]:
        with self.get_client() as client:
            result, _, err = self._activate_api(client).activate()
            if err:
                raise RuntimeError(f"Failed to activate ZIA changes: {err}")
            return self._to_dict(result)

    def with_activation(self, result: dict[str, Any]) -> dict[str, Any]:
        self.activate_changes()
        return result

    def cmd_activation_status(self, args: argparse.Namespace) -> None:
        self.cfg.update(self.cfg_from_args(args))
        self.dump(self.activation_status())
        return None

    def cmd_activate(self, args: argparse.Namespace) -> None:
        self.cfg.update(self.cfg_from_args(args))
        self.dump(self.activate_changes())
        return None

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = ZiaClient()
        overrides = argparse.ArgumentParser(add_help=False)
        ZiaClient.add_overrides(overrides)
        p = sub.add_parser("activate", help="ZIA configuration activation")
        cmds = p.add_subparsers(required=True)
        cmds.add_parser(
            "status", parents=[overrides], help="Get activation status"
        ).set_defaults(func=client.cmd_activation_status)
        cmds.add_parser(
            "run", parents=[overrides], help="Activate pending changes"
        ).set_defaults(func=client.cmd_activate)
