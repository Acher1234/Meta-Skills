"""ZIA IP/FQDN destination groups — list, get, update, resolve ids."""

from __future__ import annotations

import argparse
from typing import Any

from zia.client import ZiaClient

DESTINATION_GROUP_TYPES = frozenset(
    {"DSTN_IP", "DSTN_FQDN", "DSTN_DOMAIN", "DSTN_OTHER"}
)


class IpFqdnGroupsClient(ZiaClient):
    @staticmethod
    def _to_dict(item: Any) -> dict[str, Any]:
        if item is None:
            return {}
        if hasattr(item, "as_dict"):
            return item.as_dict()
        return dict(item)

    def list_ip_destination_groups(
        self,
        *,
        exclude_type: str | None = None,
        search: str | None = None,
        cfg: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        exclude: str | None = None
        if exclude_type:
            exclude = exclude_type.strip().upper()
            if exclude not in DESTINATION_GROUP_TYPES:
                raise ValueError(
                    f"invalid exclude_type {exclude_type!r}; "
                    f"expected one of {sorted(DESTINATION_GROUP_TYPES)}"
                )
        with self.get_client(cfg) as client:
            groups, _, err = client.zia.cloud_firewall.list_ip_destination_groups(
                exclude_type=exclude
            )
            if err:
                raise RuntimeError(f"Failed to list destination IP groups: {err}")
            result = [self._to_dict(group) for group in (groups or [])]
        if search and search.strip():
            needle = search.strip().casefold()
            result = [
                group
                for group in result
                if needle in str(group.get("name") or "").casefold()
                or needle == str(group.get("id") or "").casefold()
            ]
        return result

    def get_ip_destination_group(
        self,
        *,
        group_id: int | str | None = None,
        group_name: str | None = None,
        cfg: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if group_id is not None and str(group_id).strip():
            with self.get_client(cfg) as client:
                group, _, err = client.zia.cloud_firewall.get_ip_destination_group(
                    int(group_id)
                )
                if err:
                    raise RuntimeError(
                        f"Failed to get destination IP group {group_id}: {err}"
                    )
                if group is None:
                    raise RuntimeError(f"Destination IP group not found: {group_id}")
                return self._to_dict(group)

        if not group_name or not group_name.strip():
            raise ValueError("group_id or group_name is required")

        needle = group_name.strip().casefold()
        matches = [
            group
            for group in self.list_ip_destination_groups(cfg=cfg)
            if str(group.get("name") or "").casefold() == needle
        ]
        if not matches:
            raise RuntimeError(f"Destination IP group not found: {group_name!r}")
        if len(matches) > 1:
            ids = ", ".join(str(group.get("id")) for group in matches)
            raise RuntimeError(
                f"multiple destination IP groups named {group_name!r}: {ids}"
            )
        return matches[0]

    @staticmethod
    def _payload_from_current(current: dict[str, Any]) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": current.get("name"),
            "type": current.get("type"),
        }
        if current.get("description") is not None:
            payload["description"] = current.get("description")
        addresses = current.get("addresses")
        if addresses:
            payload["addresses"] = list(addresses)
        categories = current.get("ip_categories") or current.get("ipCategories")
        if categories:
            payload["ip_categories"] = list(categories)
        countries = current.get("countries")
        if countries:
            payload["countries"] = list(countries)
        return payload

    @staticmethod
    def _clean_values(values: list[str] | None) -> list[str]:
        return [str(v).strip() for v in (values or []) if str(v).strip()]

    def update_ip_destination_group(
        self,
        *,
        group_id: int | str | None = None,
        group_name: str | None = None,
        name: str | None = None,
        description: str | None = None,
        group_type: str | None = None,
        addresses: list[str] | None = None,
        ip_categories: list[str] | None = None,
        countries: list[str] | None = None,
        append: bool = False,
        cfg: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        current = self.get_ip_destination_group(
            group_id=group_id, group_name=group_name, cfg=cfg
        )
        gid = current["id"]
        kwargs = self._payload_from_current(current)
        if name is not None and str(name).strip():
            kwargs["name"] = str(name).strip()
        if description is not None:
            kwargs["description"] = description
        if group_type is not None:
            type_norm = group_type.strip().upper()
            if type_norm not in DESTINATION_GROUP_TYPES:
                raise ValueError(
                    f"invalid type {group_type!r}; "
                    f"expected one of {sorted(DESTINATION_GROUP_TYPES)}"
                )
            kwargs["type"] = type_norm
        query_params: dict[str, Any] | None = None
        if addresses is not None:
            cleaned = self._clean_values(addresses)
            if append:
                if not cleaned:
                    raise ValueError("--address is required when --append is set")
                kwargs["addresses"] = cleaned
                query_params = {"override": False}
            else:
                if not cleaned:
                    kwargs.pop("addresses", None)
                else:
                    kwargs["addresses"] = cleaned
        elif append:
            raise ValueError("--address is required when --append is set")
        if ip_categories is not None:
            cleaned = self._clean_values(ip_categories)
            if cleaned:
                kwargs["ip_categories"] = cleaned
            else:
                kwargs.pop("ip_categories", None)
        if countries is not None:
            cleaned = self._clean_values(countries)
            if cleaned:
                kwargs["countries"] = cleaned
            else:
                kwargs.pop("countries", None)
        with self.get_client(cfg) as client:
            updated, _, err = client.zia.cloud_firewall.update_ip_destination_group(
                str(gid),
                query_params=query_params,
                **kwargs,
            )
            if err:
                raise RuntimeError(f"Failed to update destination IP group {gid}: {err}")
            payload = self._to_dict(updated)
        return self.with_activation(payload, cfg=cfg)

    def resolve_dest_ip_group_ids(
        self,
        *,
        group_ids: list[int | str] | None = None,
        group_names: list[str] | None = None,
        cfg: dict[str, Any] | None = None,
    ) -> list[int]:
        resolved: list[int] = []
        seen: set[int] = set()
        for gid in group_ids or []:
            gid_int = int(gid)
            if gid_int not in seen:
                seen.add(gid_int)
                resolved.append(gid_int)
        names = [str(n).strip() for n in (group_names or []) if str(n).strip()]
        if names:
            groups = self.list_ip_destination_groups(cfg=cfg)
            by_name = {str(g.get("name") or "").casefold(): g for g in groups}
            for name in names:
                needle = name.casefold()
                if needle not in by_name:
                    raise RuntimeError(f"Destination IP group not found: {name!r}")
                gid_int = int(by_name[needle]["id"])
                if gid_int not in seen:
                    seen.add(gid_int)
                    resolved.append(gid_int)
        return resolved

    def cmd_list(self, args: argparse.Namespace) -> None:
        self.dump(
            self.list_ip_destination_groups(
                exclude_type=args.exclude_type or None,
                search=args.search or None,
                cfg=self.cfg_from_args(args),
            )
        )
        return None

    def cmd_get(self, args: argparse.Namespace) -> None:
        self.dump(
            self.get_ip_destination_group(
                group_id=args.id or None,
                group_name=args.name or None,
                cfg=self.cfg_from_args(args),
            )
        )
        return None

    def cmd_update(self, args: argparse.Namespace) -> None:
        self.dump(
            self.update_ip_destination_group(
                group_id=args.id or None,
                group_name=args.name or None,
                name=args.new_name or None,
                description=args.description,
                group_type=args.type or None,
                addresses=args.address,
                ip_categories=args.ip_category,
                countries=args.country,
                append=bool(args.append),
                cfg=self.cfg_from_args(args),
            )
        )
        return None

    @staticmethod
    def _add_group_ref(parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--id", help="Group id")
        parser.add_argument("--name", help="Exact group name")

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = IpFqdnGroupsClient()
        overrides = argparse.ArgumentParser(add_help=False)
        ZiaClient.add_overrides(overrides)

        p = sub.add_parser(
            "ip-fqdn-groups", help="ZIA IP/FQDN destination groups"
        )
        cmds = p.add_subparsers(required=True)

        u_list = cmds.add_parser("list", parents=[overrides], help="List groups")
        u_list.add_argument("--search", default="", help="Filter by name or id")
        u_list.add_argument(
            "--exclude-type",
            help="DSTN_IP, DSTN_FQDN, DSTN_DOMAIN, DSTN_OTHER",
        )
        u_list.set_defaults(func=client.cmd_list)

        u_get = cmds.add_parser("get", parents=[overrides], help="Get a group")
        IpFqdnGroupsClient._add_group_ref(u_get)
        u_get.set_defaults(func=client.cmd_get)

        u_update = cmds.add_parser(
            "update", parents=[overrides], help="Update a group"
        )
        IpFqdnGroupsClient._add_group_ref(u_update)
        u_update.add_argument("--new-name", help="Rename the group")
        u_update.add_argument("--description")
        u_update.add_argument(
            "--type", help="DSTN_IP, DSTN_FQDN, DSTN_DOMAIN, DSTN_OTHER"
        )
        u_update.add_argument(
            "--address",
            action="append",
            help="IP or FQDN (repeatable; replaces unless --append)",
        )
        u_update.add_argument(
            "--append",
            action="store_true",
            help="Append --address instead of replacing",
        )
        u_update.add_argument(
            "--ip-category",
            action="append",
            help="Custom URL category (DSTN_OTHER)",
        )
        u_update.add_argument(
            "--country",
            action="append",
            help="Country code e.g. COUNTRY_US (DSTN_OTHER)",
        )
        u_update.set_defaults(func=client.cmd_update)
