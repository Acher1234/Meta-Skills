"""ZIA dedicated IP gateways — list, get, resolve."""

from __future__ import annotations

import argparse
from typing import Any

from zia.client import ZiaClient


class DedicatedIpGatewaysClient(ZiaClient):
    @staticmethod
    def _to_dict(item: Any) -> dict[str, Any]:
        if item is None:
            return {}
        if hasattr(item, "as_dict"):
            return item.as_dict()
        return dict(item)

    @staticmethod
    def _dedicated_ip_gateways_api(client: Any) -> Any:
        zia_svc = client.zia
        api = getattr(zia_svc, "dedicated_ip_gateways", None)
        if api is not None:
            return api
        from zscaler.zia.dedicated_ip_gateways import DedicatedIPGatewaysAPI

        return DedicatedIPGatewaysAPI(zia_svc.request_executor)

    def list_dedicated_ips(
        self, *, cfg: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        with self.get_client(cfg) as client:
            gateways, _, err = self._dedicated_ip_gateways_api(
                client
            ).list_dedicated_ip_gw_lite()
            if err:
                raise RuntimeError(f"Failed to list dedicated IP gateways: {err}")
            return [self._to_dict(gateway) for gateway in (gateways or [])]

    def resolve_dedicated_ip_gateway(
        self,
        *,
        gateway_id: int | str | None = None,
        gateway_name: str | None = None,
        cfg: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        gateways = self.list_dedicated_ips(cfg=cfg)
        if gateway_id is not None and str(gateway_id).strip():
            gid = int(gateway_id)
            for gateway in gateways:
                if int(gateway.get("id") or 0) == gid:
                    return {"id": int(gateway["id"]), "name": gateway.get("name")}
            available = ", ".join(
                f"{g.get('id')}:{g.get('name')}" for g in gateways
            )
            raise RuntimeError(
                f"Dedicated IP gateway not found: id={gid}. available: {available}"
            )

        if not gateway_name or not gateway_name.strip():
            raise ValueError("gateway_id or gateway_name is required")

        needle = gateway_name.strip().casefold()
        matches = [
            gateway
            for gateway in gateways
            if str(gateway.get("name") or "").casefold() == needle
        ]
        if not matches:
            available = ", ".join(
                sorted(str(g.get("name") or "?") for g in gateways)
            )
            raise RuntimeError(
                f"Dedicated IP gateway not found: {gateway_name!r}. available: {available}"
            )
        if len(matches) > 1:
            ids = ", ".join(str(g.get("id")) for g in matches)
            raise RuntimeError(
                f"multiple dedicated IP gateways named {gateway_name!r}: {ids}"
            )
        return {"id": int(matches[0]["id"]), "name": matches[0].get("name")}

    def cmd_list(self, args: argparse.Namespace) -> None:
        self.dump(self.list_dedicated_ips(cfg=self.cfg_from_args(args)))
        return None

    def cmd_get(self, args: argparse.Namespace) -> None:
        self.dump(
            self.resolve_dedicated_ip_gateway(
                gateway_id=args.id or None,
                gateway_name=args.name or None,
                cfg=self.cfg_from_args(args),
            )
        )
        return None

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = DedicatedIpGatewaysClient()
        overrides = argparse.ArgumentParser(add_help=False)
        ZiaClient.add_overrides(overrides)

        p = sub.add_parser(
            "dedicated-ip-gateways", help="ZIA dedicated IP gateways"
        )
        cmds = p.add_subparsers(required=True)

        cmds.add_parser(
            "list", parents=[overrides], help="List dedicated IP gateways"
        ).set_defaults(func=client.cmd_list)

        u_get = cmds.add_parser("get", parents=[overrides], help="Get a gateway")
        u_get.add_argument("--id", help="Gateway id")
        u_get.add_argument("--name", help="Exact gateway name")
        u_get.set_defaults(func=client.cmd_get)
