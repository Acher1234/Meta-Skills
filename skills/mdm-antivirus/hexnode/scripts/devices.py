"""Hexnode Devices API — https://www.hexnode.com/mobile-device-management/developers/devices/

GET /devices/                              list_devices
GET /devices/{id}/                         get_device
GET /devices/{id}/policies/                list_device_policies
GET /devices/{id}/applications/            list_device_applications
GET /devices/{id}/locations/               list_device_locations
"""

from __future__ import annotations

import argparse
from typing import Any

from client import HexnodeClient


class DevicesClient(HexnodeClient):
    def list_devices(
        self,
        *,
        order_by: str | None = None,
        platform: str | None = None,
        is_active: bool | None = None,
        device_type: str | None = None,
        page: int | None = None,
        per_page: int | None = None,
    ) -> Any:
        """GET /devices/ — list enrolled devices."""
        params: dict[str, Any] = {
            "order_by": order_by,
            "platform": platform,
            "device_type": device_type,
            **self._page_params(page, per_page),
        }
        if is_active is not None:
            params["is_active"] = "True" if is_active else "False"
        return self.request("GET", "/devices/", params=params)

    def get_device(self, device_id: int | str) -> Any:
        """GET /devices/{id}/ — retrieve device details."""
        return self.request("GET", f"/devices/{device_id}/")

    def list_device_policies(
        self,
        device_id: int | str,
        *,
        page: int | None = None,
        per_page: int | None = None,
    ) -> Any:
        """GET /devices/{id}/policies/ — policies associated with a device."""
        return self.request(
            "GET",
            f"/devices/{device_id}/policies/",
            params=self._page_params(page, per_page),
        )

    def list_device_applications(
        self,
        device_id: int | str,
        *,
        page: int | None = None,
        per_page: int | None = None,
    ) -> Any:
        """GET /devices/{id}/applications/ — apps on a device."""
        return self.request(
            "GET",
            f"/devices/{device_id}/applications/",
            params=self._page_params(page, per_page),
        )

    def list_device_locations(
        self,
        device_id: int | str,
        *,
        page: int | None = None,
        per_page: int | None = None,
    ) -> Any:
        """GET /devices/{id}/locations/ — reported locations for a device."""
        return self.request(
            "GET",
            f"/devices/{device_id}/locations/",
            params=self._page_params(page, per_page),
        )

    def cmd_list(self, args: argparse.Namespace) -> int:
        is_active = True if args.active else False if args.inactive else None
        self.dump(
            self.list_devices(
                order_by=args.order_by,
                platform=args.platform,
                is_active=is_active,
                device_type=args.device_type,
                page=args.page,
                per_page=args.per_page,
            )
        )
        return 0

    def cmd_get(self, args: argparse.Namespace) -> int:
        self.dump(self.get_device(args.device_id))
        return 0

    def cmd_policies(self, args: argparse.Namespace) -> int:
        self.dump(
            self.list_device_policies(
                args.device_id, page=args.page, per_page=args.per_page
            )
        )
        return 0

    def cmd_applications(self, args: argparse.Namespace) -> int:
        self.dump(
            self.list_device_applications(
                args.device_id, page=args.page, per_page=args.per_page
            )
        )
        return 0

    def cmd_locations(self, args: argparse.Namespace) -> int:
        self.dump(
            self.list_device_locations(
                args.device_id, page=args.page, per_page=args.per_page
            )
        )
        return 0

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = DevicesClient()
        p = sub.add_parser("devices", help="Devices API")
        cmds = p.add_subparsers(required=True)

        d_list = cmds.add_parser("list", help="GET /devices/ — list enrolled devices")
        d_list.add_argument("--order-by", choices=["asc", "desc"])
        d_list.add_argument("--platform", choices=["ios", "android", "windows"])
        d_list.add_argument("--active", action="store_true", help="is_active=True")
        d_list.add_argument("--inactive", action="store_true", help="is_active=False")
        d_list.add_argument("--device-type", choices=["smartphone", "tablet"])
        HexnodeClient.add_paging(d_list)
        d_list.set_defaults(func=client.cmd_list)

        d_get = cmds.add_parser("get", help="GET /devices/{id}/ — device details")
        d_get.add_argument("device_id", help="Hexnode device id")
        d_get.set_defaults(func=client.cmd_get)

        d_pol = cmds.add_parser("policies", help="GET /devices/{id}/policies/")
        d_pol.add_argument("device_id", help="Hexnode device id")
        HexnodeClient.add_paging(d_pol)
        d_pol.set_defaults(func=client.cmd_policies)

        d_apps = cmds.add_parser("applications", help="GET /devices/{id}/applications/")
        d_apps.add_argument("device_id", help="Hexnode device id")
        HexnodeClient.add_paging(d_apps)
        d_apps.set_defaults(func=client.cmd_applications)

        d_loc = cmds.add_parser("locations", help="GET /devices/{id}/locations/")
        d_loc.add_argument("device_id", help="Hexnode device id")
        HexnodeClient.add_paging(d_loc)
        d_loc.set_defaults(func=client.cmd_locations)
