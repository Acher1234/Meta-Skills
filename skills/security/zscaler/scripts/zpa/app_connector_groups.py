"""ZPA App Connector groups — list, get."""

from __future__ import annotations

import argparse
from typing import Any

from zpa.client import ZpaClient
from zscaler.zpa.app_connector_groups import AppConnectorGroupAPI


class AppConnectorGroupsClient(ZpaClient):
    @staticmethod
    def _api(client: Any) -> Any:
        zpa_svc = client.zpa
        api = getattr(zpa_svc, "app_connector_groups", None)
        if api is not None:
            return api
        return AppConnectorGroupAPI(zpa_svc.request_executor, zpa_svc.config)

    def list_groups(self, search: str | None = None) -> list[dict[str, Any]]:
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
                groups, _, err = api.list_connector_groups(query_params=query_params)
                if err:
                    raise RuntimeError(f"Failed to list App Connector groups: {err}")
                batch = [self._to_dict(group) for group in (groups or [])]
                results.extend(batch)
                if len(batch) < page_size:
                    break
                page += 1
        return results

    def get_group(
        self,
        *,
        group_id: str | None = None,
        group_name: str | None = None,
    ) -> dict[str, Any]:
        if group_id is not None and str(group_id).strip():
            gid = str(group_id).strip()
            with self.get_client() as client:
                group, _, err = self._api(client).get_connector_group(gid)
                if err:
                    raise RuntimeError(f"Failed to get App Connector group {gid}: {err}")
                if group is None:
                    raise RuntimeError(f"App Connector group not found: {gid}")
                return self._to_dict(group)

        if not group_name or not group_name.strip():
            raise ValueError("group_id or group_name is required")

        needle = group_name.strip().casefold()
        matches = [
            group
            for group in self.list_groups(group_name.strip())
            if str(group.get("name") or "").casefold() == needle
        ]
        if not matches:
            matches = [
                group
                for group in self.list_groups()
                if str(group.get("name") or "").casefold() == needle
            ]
        if not matches:
            raise RuntimeError(f"App Connector group not found: {group_name!r}")
        if len(matches) > 1:
            ids = ", ".join(str(group.get("id")) for group in matches)
            raise RuntimeError(
                f"multiple App Connector groups named {group_name!r}: {ids}"
            )
        return matches[0]

    def cmd_list(self, args: argparse.Namespace) -> None:
        self.dump(self.list_groups(search=args.search or None))
        return None

    def cmd_get(self, args: argparse.Namespace) -> None:
        self.dump(
            self.get_group(
                group_id=args.id or None,
                group_name=args.name or None,
            )
        )
        return None

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = AppConnectorGroupsClient()
        p = sub.add_parser("app-connector-group", help="ZPA App Connector groups")
        cmds = p.add_subparsers(required=True)

        u_list = cmds.add_parser("list", help="List App Connector groups")
        u_list.add_argument("--search", default="", help="Filter by name")
        u_list.set_defaults(func=client.cmd_list)

        u_get = cmds.add_parser("get", help="Get an App Connector group")
        u_get.add_argument("--id", help="Group id")
        u_get.add_argument("--name", help="Exact group name")
        u_get.set_defaults(func=client.cmd_get)
