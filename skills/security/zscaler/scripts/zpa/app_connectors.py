"""ZPA App Connectors — list, get, health."""

from __future__ import annotations

import argparse
from typing import Any

from zpa.client import ZpaClient
from zscaler.zpa.app_connectors import AppConnectorControllerAPI

HEALTHY_STATUS = "ZPN_STATUS_AUTHENTICATED"


class AppConnectorsClient(ZpaClient):
    @staticmethod
    def _api(client: Any) -> Any:
        zpa_svc = client.zpa
        api = getattr(zpa_svc, "app_connectors", None)
        if api is not None:
            return api
        return AppConnectorControllerAPI(zpa_svc.request_executor, zpa_svc.config)

    def list_connectors(self, search: str | None = None) -> list[dict[str, Any]]:
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
                connectors, _, err = api.list_connectors(query_params=query_params)
                if err:
                    raise RuntimeError(f"Failed to list App Connectors: {err}")
                batch = [self._to_dict(connector) for connector in (connectors or [])]
                results.extend(batch)
                if len(batch) < page_size:
                    break
                page += 1
        return results

    def get_connector(
        self,
        *,
        connector_id: str | None = None,
        connector_name: str | None = None,
    ) -> dict[str, Any]:
        if connector_id is not None and str(connector_id).strip():
            cid = str(connector_id).strip()
            with self.get_client() as client:
                connector, _, err = self._api(client).get_connector(cid)
                if err:
                    raise RuntimeError(f"Failed to get App Connector {cid}: {err}")
                if connector is None:
                    raise RuntimeError(f"App Connector not found: {cid}")
                return self._to_dict(connector)

        if not connector_name or not connector_name.strip():
            raise ValueError("connector_id or connector_name is required")

        needle = connector_name.strip().casefold()
        matches = [
            connector
            for connector in self.list_connectors(connector_name.strip())
            if str(connector.get("name") or "").casefold() == needle
        ]
        if not matches:
            matches = [
                connector
                for connector in self.list_connectors()
                if str(connector.get("name") or "").casefold() == needle
            ]
        if not matches:
            raise RuntimeError(f"App Connector not found: {connector_name!r}")
        if len(matches) > 1:
            ids = ", ".join(str(connector.get("id")) for connector in matches)
            raise RuntimeError(
                f"multiple App Connectors named {connector_name!r}: {ids}"
            )
        return matches[0]

    @staticmethod
    def _status(connector: dict[str, Any]) -> str:
        return str(
            connector.get("control_channel_status")
            or connector.get("controlChannelStatus")
            or ""
        ).strip()

    @staticmethod
    def _is_enabled(connector: dict[str, Any]) -> bool:
        enabled = connector.get("enabled")
        return True if enabled is None else bool(enabled)

    @classmethod
    def _is_healthy(cls, connector: dict[str, Any]) -> bool:
        return cls._status(connector).casefold() == HEALTHY_STATUS.casefold()

    @classmethod
    def _summary(cls, connector: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": connector.get("id"),
            "name": connector.get("name"),
            "healthy": cls._is_healthy(connector),
            "enabled": cls._is_enabled(connector),
            "control_channel_status": cls._status(connector) or None,
            "app_connector_group_name": connector.get("app_connector_group_name")
            or connector.get("appConnectorGroupName"),
            "last_broker_connect_time": connector.get("last_broker_connect_time")
            or connector.get("lastBrokerConnectTime"),
            "last_broker_disconnect_time": connector.get("last_broker_disconnect_time")
            or connector.get("lastBrokerDisconnectTime"),
        }

    def health(
        self,
        *,
        search: str | None = None,
        enabled_only: bool = False,
    ) -> dict[str, Any]:
        connectors = self.list_connectors(search=search)
        if enabled_only:
            connectors = [c for c in connectors if self._is_enabled(c)]
        summaries = [self._summary(c) for c in connectors]
        unhealthy = [item for item in summaries if not item["healthy"]]
        return {
            "ok": all(item["healthy"] for item in summaries),
            "total": len(summaries),
            "healthy_count": len(summaries) - len(unhealthy),
            "unhealthy_count": len(unhealthy),
        }

    def cmd_list(self, args: argparse.Namespace) -> None:
        self.dump(self.list_connectors(search=args.search or None))
        return None

    def cmd_get(self, args: argparse.Namespace) -> None:
        self.dump(
            self.get_connector(
                connector_id=args.id or None,
                connector_name=args.name or None,
            )
        )
        return None

    def cmd_health(self, args: argparse.Namespace) -> None:
        self.dump(
            self.health(
                search=args.search or None,
                enabled_only=bool(args.enabled_only),
            )
        )
        return None

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = AppConnectorsClient()
        p = sub.add_parser("app-connector", help="ZPA App Connectors")
        cmds = p.add_subparsers(required=True)

        u_list = cmds.add_parser("list", help="List App Connectors")
        u_list.add_argument("--search", default="", help="Filter by name")
        u_list.set_defaults(func=client.cmd_list)

        u_get = cmds.add_parser("get", help="Get an App Connector")
        u_get.add_argument("--id", help="Connector id")
        u_get.add_argument("--name", help="Exact connector name")
        u_get.set_defaults(func=client.cmd_get)

        u_health = cmds.add_parser(
            "health", help="Check that all App Connectors are healthy"
        )
        u_health.add_argument("--search", default="", help="Filter by name")
        u_health.add_argument(
            "--enabled-only",
            action="store_true",
            help="Ignore disabled App Connectors",
        )
        u_health.set_defaults(func=client.cmd_health)
