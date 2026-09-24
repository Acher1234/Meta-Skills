"""ZPA client forwarding policy — list, get."""

from __future__ import annotations

import argparse
from typing import Any

from zpa.client import ZpaClient
from zscaler.zpa.policies import PolicySetControllerAPI

POLICY_TYPE = "client_forwarding"


class ForwardingPolicyClient(ZpaClient):
    @staticmethod
    def _api(client: Any) -> Any:
        zpa_svc = client.zpa
        api = getattr(zpa_svc, "policies", None)
        if api is not None:
            return api
        return PolicySetControllerAPI(zpa_svc.request_executor, zpa_svc.config)

    def list_rules(self, search: str | None = None) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        page = 1
        page_size = 500
        with self.get_client() as client:
            api = self._api(client)
            while True:
                query_params: dict[str, Any] = {
                    "page": str(page),
                    "page_size": str(page_size),
                }
                if search and search.strip():
                    query_params["search"] = search.strip()
                rules, _, err = api.list_rules(POLICY_TYPE, query_params=query_params)
                if err:
                    raise RuntimeError(
                        f"Failed to list forwarding policy rules: {err}"
                    )
                batch = [self._to_dict(rule) for rule in (rules or [])]
                results.extend(batch)
                if len(batch) < page_size:
                    break
                page += 1
        return results

    def get_rule(
        self,
        *,
        rule_id: str | None = None,
        rule_name: str | None = None,
    ) -> dict[str, Any]:
        if rule_id is not None and str(rule_id).strip():
            rid = str(rule_id).strip()
            with self.get_client() as client:
                rule, _, err = self._api(client).get_rule(POLICY_TYPE, rid)
                if err:
                    raise RuntimeError(
                        f"Failed to get forwarding policy rule {rid}: {err}"
                    )
                if rule is None:
                    raise RuntimeError(f"Forwarding policy rule not found: {rid}")
                return self._to_dict(rule)

        if not rule_name or not rule_name.strip():
            raise ValueError("rule_id or rule_name is required")

        needle = rule_name.strip().casefold()
        matches = [
            rule
            for rule in self.list_rules(rule_name.strip())
            if str(rule.get("name") or "").casefold() == needle
        ]
        if not matches:
            matches = [
                rule
                for rule in self.list_rules()
                if str(rule.get("name") or "").casefold() == needle
            ]
        if not matches:
            raise RuntimeError(f"Forwarding policy rule not found: {rule_name!r}")
        if len(matches) > 1:
            ids = ", ".join(str(rule.get("id")) for rule in matches)
            raise RuntimeError(
                f"multiple forwarding policy rules named {rule_name!r}: {ids}"
            )
        return matches[0]

    def cmd_list(self, args: argparse.Namespace) -> None:
        self.dump(self.list_rules(search=args.search or None))
        return None

    def cmd_get(self, args: argparse.Namespace) -> None:
        self.dump(
            self.get_rule(
                rule_id=args.id or None,
                rule_name=args.name or None,
            )
        )
        return None

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = ForwardingPolicyClient()
        p = sub.add_parser("forwarding-policy", help="ZPA client forwarding policy")
        cmds = p.add_subparsers(required=True)

        u_list = cmds.add_parser("list", help="List forwarding policy rules")
        u_list.add_argument("--search", default="", help="Filter by name")
        u_list.set_defaults(func=client.cmd_list)

        u_get = cmds.add_parser("get", help="Get a forwarding policy rule")
        u_get.add_argument("--id", help="Rule id")
        u_get.add_argument("--name", help="Exact rule name")
        u_get.set_defaults(func=client.cmd_get)
