"""Elastic Security detection rules — create, get, update, delete."""

from __future__ import annotations

import argparse
from typing import Any

from base_kibana import BaseKibana

RULES_PATH = "/api/detection_engine/rules"


class SecurityRule(BaseKibana):
    def get_rule(
        self,
        *,
        rule_id: str | None = None,
        saved_id: str | None = None,
    ) -> Any:
        params = self._ref_params(saved_id=saved_id, rule_id=rule_id)
        return self._kibana_request("GET", RULES_PATH, params=params)

    def create_rule(self, body: dict[str, Any]) -> Any:
        return self._kibana_request("POST", RULES_PATH, json_body=body)

    def update_rule(
        self,
        body: dict[str, Any],
        *,
        rule_id: str | None = None,
        saved_id: str | None = None,
    ) -> Any:
        payload = dict(body)
        if saved_id:
            payload["id"] = saved_id
        if rule_id:
            payload["rule_id"] = rule_id
        if not payload.get("id") and not payload.get("rule_id"):
            raise ValueError("id or rule_id is required")
        return self._kibana_request("PUT", RULES_PATH, json_body=payload)

    def delete_rule(
        self,
        *,
        rule_id: str | None = None,
        saved_id: str | None = None,
    ) -> Any:
        params = self._ref_params(saved_id=saved_id, rule_id=rule_id)
        return self._kibana_request("DELETE", RULES_PATH, params=params)

    @staticmethod
    def _ref_params(
        *,
        saved_id: str | None = None,
        rule_id: str | None = None,
    ) -> dict[str, str]:
        params: dict[str, str] = {}
        if saved_id:
            params["id"] = saved_id
        if rule_id:
            params["rule_id"] = rule_id
        if not params:
            raise ValueError("--id or --rule-id is required")
        return params

    def cmd_get(self, args: argparse.Namespace) -> None:
        self._dump_write(
            lambda: self.get_rule(
                saved_id=args.id or None, rule_id=args.rule_id or None
            )
        )
        return None

    def cmd_create(self, args: argparse.Namespace) -> None:
        self._dump_write(lambda: self.create_rule(self._parse_json(args.json)))
        return None

    def cmd_update(self, args: argparse.Namespace) -> None:
        self._dump_write(
            lambda: self.update_rule(
                self._parse_json(args.json),
                saved_id=args.id or None,
                rule_id=args.rule_id or None,
            )
        )
        return None

    def cmd_delete(self, args: argparse.Namespace) -> None:
        self._dump_write(
            lambda: self.delete_rule(
                saved_id=args.id or None, rule_id=args.rule_id or None
            )
        )
        return None

    @staticmethod
    def _add_rule_ref(parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--id", help="Saved object id (UUID)")
        parser.add_argument("--rule-id", help="Stable rule_id")

    @staticmethod
    def register_cmds(cmds: argparse._SubParsersAction) -> None:
        client = SecurityRule()
        p = cmds.add_parser("security-rule", help="Detection engine rules")
        rule_cmds = p.add_subparsers(required=True)

        u_get = rule_cmds.add_parser("get", help="GET /api/detection_engine/rules")
        SecurityRule._add_rule_ref(u_get)
        u_get.set_defaults(func=client.cmd_get)

        u_create = rule_cmds.add_parser(
            "create", help="POST /api/detection_engine/rules"
        )
        u_create.add_argument("--json", required=True, help="Rule JSON body")
        u_create.set_defaults(func=client.cmd_create)

        u_update = rule_cmds.add_parser(
            "update", help="PUT /api/detection_engine/rules (full replace)"
        )
        SecurityRule._add_rule_ref(u_update)
        u_update.add_argument("--json", required=True, help="Rule JSON body")
        u_update.set_defaults(func=client.cmd_update)

        u_del = rule_cmds.add_parser(
            "delete", help="DELETE /api/detection_engine/rules"
        )
        SecurityRule._add_rule_ref(u_del)
        u_del.set_defaults(func=client.cmd_delete)
