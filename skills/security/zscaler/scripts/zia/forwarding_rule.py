"""ZIA forwarding control — list, get, create, delete."""

from __future__ import annotations

import argparse
from typing import Any

from zia.client import ZiaClient
from zia.dedicated_ip_gateways import DedicatedIpGatewaysClient
from zia.ip_fqdn_groups import IpFqdnGroupsClient
from zia.url_categories import UrlCategoriesClient
from zia.users import UsersClient

FORWARD_METHODS = (
    "DIRECT",
    "PROXYCHAIN",
    "ZIA",
    "ZPA",
    "ECZPA",
    "ECSELF",
    "DROP",
    "ENATDEDIP",
    "GEOIP",
)
FORWARDING_RULE_NAME_MAX = 31


class ForwardingRuleClient(ZiaClient):
    @staticmethod
    def _to_dict(item: Any) -> dict[str, Any]:
        if item is None:
            return {}
        if hasattr(item, "as_dict"):
            return item.as_dict()
        return dict(item)

    @staticmethod
    def _forwarding_control_api(client: Any) -> Any:
        zia_svc = client.zia
        api = getattr(zia_svc, "forwarding_control", None)
        if api is not None:
            return api
        from zscaler.zia.forwarding_control import ForwardingControlAPI

        return ForwardingControlAPI(zia_svc.request_executor)

    def list_forwarding_rules(
        self,
        search: str | None = None,
        *,
        cfg: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        query_params: dict[str, Any] = {}
        if search:
            query_params["search"] = search
        with self.get_client(cfg) as client:
            rules, _, err = self._forwarding_control_api(client).list_rules(
                query_params=query_params or None
            )
            if err:
                raise RuntimeError(f"Failed to list forwarding rules: {err}")
            return [self._to_dict(rule) for rule in (rules or [])]

    def get_forwarding_rule(
        self,
        *,
        rule_id: int | str | None = None,
        rule_name: str | None = None,
        cfg: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if rule_id is not None and str(rule_id).strip():
            with self.get_client(cfg) as client:
                rule, _, err = self._forwarding_control_api(client).get_rule(
                    str(rule_id)
                )
                if err:
                    raise RuntimeError(
                        f"Failed to get forwarding rule {rule_id}: {err}"
                    )
                if rule is None:
                    raise RuntimeError(f"Forwarding rule not found: {rule_id}")
                return self._to_dict(rule)

        if not rule_name or not rule_name.strip():
            raise ValueError("rule_id or rule_name is required")

        needle = rule_name.strip().casefold()
        matches = [
            rule
            for rule in self.list_forwarding_rules(rule_name, cfg=cfg)
            if str(rule.get("name") or "").casefold() == needle
        ]
        if not matches:
            matches = [
                rule
                for rule in self.list_forwarding_rules(cfg=cfg)
                if str(rule.get("name") or "").casefold() == needle
            ]
        if not matches:
            raise RuntimeError(f"Forwarding rule not found: {rule_name!r}")
        if len(matches) > 1:
            ids = ", ".join(str(rule.get("id")) for rule in matches)
            raise RuntimeError(
                f"multiple forwarding rules named {rule_name!r}: {ids}"
            )
        return matches[0]

    def create_forwarding_rule(
        self,
        name: str,
        *,
        forward_method: str = "ENATDEDIP",
        gateway_id: int | str | None = None,
        gateway_name: str | None = None,
        group_ids: list[int | str] | None = None,
        group_names: list[str] | None = None,
        url_category_ids: list[str] | None = None,
        url_category_names: list[str] | None = None,
        dest_addresses: list[str] | None = None,
        dest_ip_group_ids: list[int | str] | None = None,
        dest_ip_group_names: list[str] | None = None,
        description: str | None = None,
        order: int | None = None,
        rank: int = 7,
        state: str = "ENABLED",
        cfg: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        name = (name or "").strip()
        if not name:
            raise ValueError("name is required")
        if len(name) > FORWARDING_RULE_NAME_MAX:
            raise ValueError(
                f"name is too long ({len(name)}); maximum {FORWARDING_RULE_NAME_MAX} characters"
            )

        method = (forward_method or "ENATDEDIP").strip().upper()
        if method not in FORWARD_METHODS:
            raise ValueError(
                f"invalid forward_method {forward_method!r}; "
                f"supported: {', '.join(FORWARD_METHODS)}"
            )

        state_norm = (state or "ENABLED").strip().upper()
        if state_norm not in ("ENABLED", "DISABLED"):
            raise ValueError("state must be ENABLED or DISABLED")

        kwargs: dict[str, Any] = {
            "name": name,
            "type": "FORWARDING",
            "forward_method": method,
            "state": state_norm,
            "rank": int(rank),
        }
        if description:
            kwargs["description"] = description
        if order is not None:
            kwargs["order"] = int(order)

        if method == "ENATDEDIP":
            gateway = DedicatedIpGatewaysClient(self.cfg).resolve_dedicated_ip_gateway(
                gateway_id=gateway_id, gateway_name=gateway_name, cfg=cfg
            )
            # API wire key is dedicatedIPGateway (IP uppercase), not dedicatedIpGateway
            # that snake_case → camelCase conversion would produce.
            kwargs["dedicatedIPGateway"] = gateway
        elif gateway_id is not None or gateway_name:
            raise ValueError(
                "gateway_id / gateway_name only apply with forward_method=ENATDEDIP"
            )

        if group_ids or group_names:
            groups = UsersClient(self.cfg).resolve_group_ids(
                group_ids=group_ids, group_names=group_names, cfg=cfg
            )
            kwargs["groups"] = [group["id"] for group in groups]

        if url_category_ids or url_category_names:
            categories = UrlCategoriesClient(self.cfg).resolve_url_category_ids(
                category_ids=url_category_ids,
                category_names=url_category_names,
                cfg=cfg,
            )
            if categories:
                kwargs["dest_ip_categories"] = categories

        addresses = [a.strip() for a in (dest_addresses or []) if a and a.strip()]
        if addresses:
            kwargs["dest_addresses"] = addresses

        if dest_ip_group_ids or dest_ip_group_names:
            dest_groups = IpFqdnGroupsClient(self.cfg).resolve_dest_ip_group_ids(
                group_ids=dest_ip_group_ids,
                group_names=dest_ip_group_names,
                cfg=cfg,
            )
            if dest_groups:
                kwargs["dest_ip_groups"] = dest_groups

        with self.get_client(cfg) as client:
            created, _, err = self._forwarding_control_api(client).add_rule(**kwargs)
            if err:
                raise RuntimeError(
                    f"Failed to create forwarding rule {name!r}: {err}"
                )
            payload = self._to_dict(created)
        return self.with_activation(payload, cfg=cfg)

    def delete_forwarding_rule(
        self,
        *,
        rule_id: int | str | None = None,
        rule_name: str | None = None,
        cfg: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        current = self.get_forwarding_rule(
            rule_id=rule_id, rule_name=rule_name, cfg=cfg
        )
        rid = current["id"]
        with self.get_client(cfg) as client:
            _, _, err = self._forwarding_control_api(client).delete_rule(str(rid))
            if err:
                raise RuntimeError(f"Failed to delete forwarding rule {rid}: {err}")
        return self.with_activation(
            {"deleted": True, "id": rid, "name": current.get("name")},
            cfg=cfg,
        )

    def cmd_list(self, args: argparse.Namespace) -> None:
        self.dump(
            self.list_forwarding_rules(
                search=args.search or None,
                cfg=self.cfg_from_args(args),
            )
        )
        return None

    def cmd_get(self, args: argparse.Namespace) -> None:
        self.dump(
            self.get_forwarding_rule(
                rule_id=args.id or None,
                rule_name=args.name or None,
                cfg=self.cfg_from_args(args),
            )
        )
        return None

    def cmd_create(self, args: argparse.Namespace) -> None:
        self.dump(
            self.create_forwarding_rule(
                args.name,
                forward_method=args.forward_method,
                gateway_id=args.gateway_id,
                gateway_name=args.gateway_name,
                group_ids=args.group_id,
                group_names=args.group_name,
                url_category_ids=args.category_id,
                url_category_names=args.category_name,
                dest_addresses=args.dest_address,
                dest_ip_group_ids=args.dest_ip_group_id,
                dest_ip_group_names=args.dest_ip_group_name,
                description=args.description or None,
                order=args.order,
                rank=args.rank,
                state=args.state,
                cfg=self.cfg_from_args(args),
            )
        )
        return None

    def cmd_delete(self, args: argparse.Namespace) -> None:
        self.dump(
            self.delete_forwarding_rule(
                rule_id=args.id or None,
                rule_name=args.name or None,
                cfg=self.cfg_from_args(args),
            )
        )
        return None

    @staticmethod
    def _add_rule_ref(parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--id", help="Rule id")
        parser.add_argument("--name", help="Exact rule name")

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = ForwardingRuleClient()
        overrides = argparse.ArgumentParser(add_help=False)
        ZiaClient.add_overrides(overrides)

        p = sub.add_parser("forwarding-rule", help="ZIA forwarding control")
        cmds = p.add_subparsers(required=True)

        u_list = cmds.add_parser("list", parents=[overrides], help="List rules")
        u_list.add_argument("--search", default="", help="Filter by name")
        u_list.set_defaults(func=client.cmd_list)

        u_get = cmds.add_parser("get", parents=[overrides], help="Get a rule")
        ForwardingRuleClient._add_rule_ref(u_get)
        u_get.set_defaults(func=client.cmd_get)

        u_create = cmds.add_parser(
            "create", parents=[overrides], help="Create a rule"
        )
        u_create.add_argument("name", help="Rule name (max 31 characters)")
        u_create.add_argument(
            "--forward-method",
            default="ENATDEDIP",
            help="DIRECT, PROXYCHAIN, ZIA, ZPA, ECZPA, ECSELF, DROP, ENATDEDIP, GEOIP",
        )
        u_create.add_argument("--gateway-id", help="Dedicated IP gateway id")
        u_create.add_argument("--gateway-name", help="Dedicated IP gateway name")
        u_create.add_argument("--group-id", action="append")
        u_create.add_argument("--group-name", action="append")
        u_create.add_argument("--category-id", action="append")
        u_create.add_argument("--category-name", action="append")
        u_create.add_argument("--dest-address", action="append")
        u_create.add_argument("--dest-ip-group-id", action="append")
        u_create.add_argument("--dest-ip-group-name", action="append")
        u_create.add_argument("--order", type=int)
        u_create.add_argument("--rank", type=int, default=7)
        u_create.add_argument("--state", default="ENABLED")
        u_create.add_argument("--description")
        u_create.set_defaults(func=client.cmd_create)

        u_del = cmds.add_parser("delete", parents=[overrides], help="Delete a rule")
        ForwardingRuleClient._add_rule_ref(u_del)
        u_del.set_defaults(func=client.cmd_delete)
