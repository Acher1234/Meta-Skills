"""Hexnode Device Groups API — https://www.hexnode.com/mobile-device-management/developers/device-groups/

GET    /devicegroups/                 list_device_groups
POST   /devicegroups/                 create_device_group
GET    /devicegroups/{id}/            get_device_group
PUT    /devicegroups/{id}/            update_device_group
POST   /devicegroups/{id}/            add_remove_devices
DELETE /devicegroups/{id}/            delete_device_group
"""

from __future__ import annotations

import argparse
from typing import Any, Iterable

from client import ConfigError, HexnodeClient


class DeviceGroupsClient(HexnodeClient):
    def list_device_groups(
        self, *, page: int | None = None, per_page: int | None = None
    ) -> Any:
        """GET /devicegroups/ — list all device groups."""
        return self.request(
            "GET",
            "/devicegroups/",
            params=self._page_params(page, per_page),
        )

    def create_device_group(
        self,
        *,
        groupname: str,
        description: str,
        devices: Iterable[int] | None = None,
    ) -> Any:
        """POST /devicegroups/ — create a static device group."""
        body: dict[str, Any] = {
            "groupname": groupname,
            "description": description,
        }
        if devices is not None:
            body["devices"] = list(devices)
        return self.request("POST", "/devicegroups/", json=body)

    def get_device_group(self, group_id: int | str) -> Any:
        """GET /devicegroups/{id}/ — retrieve device group details."""
        return self.request("GET", f"/devicegroups/{group_id}/")

    def update_device_group(
        self,
        group_id: int | str,
        *,
        groupname: str,
        description: str,
        devices: Iterable[int] | None = None,
    ) -> Any:
        """PUT /devicegroups/{id}/ — update a device group."""
        body: dict[str, Any] = {
            "groupname": groupname,
            "description": description,
        }
        if devices is not None:
            body["devices"] = list(devices)
        return self.request("PUT", f"/devicegroups/{group_id}/", json=body)

    def add_remove_devices(
        self,
        group_id: int | str,
        *,
        add_devices: Iterable[int] | None = None,
        remove_devices: Iterable[int] | None = None,
    ) -> Any:
        """POST /devicegroups/{id}/ — add and/or remove devices."""
        body = {
            "add_devices": list(add_devices or []),
            "remove_devices": list(remove_devices or []),
        }
        return self.request("POST", f"/devicegroups/{group_id}/", json=body)

    def delete_device_group(self, group_id: int | str) -> Any:
        """DELETE /devicegroups/{id}/ — delete a device group."""
        return self.request("DELETE", f"/devicegroups/{group_id}/")

    @staticmethod
    def _parse_id_list(values: list[str] | None) -> list[int]:
        out: list[int] = []
        for raw in values or []:
            for part in str(raw).split(","):
                part = part.strip()
                if part:
                    out.append(int(part))
        return out

    def cmd_list(self, args: argparse.Namespace) -> int:
        self.dump(self.list_device_groups(page=args.page, per_page=args.per_page))
        return 0

    def cmd_create(self, args: argparse.Namespace) -> int:
        self.dump(
            self.create_device_group(
                groupname=args.name,
                description=args.description,
                devices=self._parse_id_list(args.device) or None,
            )
        )
        return 0

    def cmd_get(self, args: argparse.Namespace) -> int:
        self.dump(self.get_device_group(args.group_id))
        return 0

    def cmd_update(self, args: argparse.Namespace) -> int:
        self.dump(
            self.update_device_group(
                args.group_id,
                groupname=args.name,
                description=args.description,
                devices=self._parse_id_list(args.device) or None,
            )
        )
        return 0

    def cmd_add_remove(self, args: argparse.Namespace) -> int:
        add_ids = self._parse_id_list(args.add)
        remove_ids = self._parse_id_list(args.remove)
        if not add_ids and not remove_ids:
            raise ConfigError("add-remove requires --add and/or --remove")
        self.dump(
            self.add_remove_devices(
                args.group_id,
                add_devices=add_ids,
                remove_devices=remove_ids,
            )
        )
        return 0

    def cmd_delete(self, args: argparse.Namespace) -> int:
        return self.dump_result(self.delete_device_group(args.group_id))

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = DeviceGroupsClient()
        p = sub.add_parser("device-groups", help="Device Groups API")
        cmds = p.add_subparsers(required=True)

        dg_list = cmds.add_parser("list", help="GET /devicegroups/")
        HexnodeClient.add_paging(dg_list)
        dg_list.set_defaults(func=client.cmd_list)

        dg_create = cmds.add_parser("create", help="POST /devicegroups/")
        dg_create.add_argument("--name", required=True, help="groupname")
        dg_create.add_argument("--description", required=True, help="description")
        dg_create.add_argument(
            "--device",
            action="append",
            default=[],
            metavar="ID",
            help="Device id to include (repeatable or comma-separated)",
        )
        dg_create.set_defaults(func=client.cmd_create)

        dg_get = cmds.add_parser("get", help="GET /devicegroups/{id}/")
        dg_get.add_argument("group_id", help="Device group id")
        dg_get.set_defaults(func=client.cmd_get)

        dg_upd = cmds.add_parser("update", help="PUT /devicegroups/{id}/")
        dg_upd.add_argument("group_id", help="Device group id")
        dg_upd.add_argument("--name", required=True, help="groupname")
        dg_upd.add_argument("--description", required=True, help="description")
        dg_upd.add_argument(
            "--device",
            action="append",
            default=[],
            metavar="ID",
            help="Replace member device ids (repeatable or comma-separated)",
        )
        dg_upd.set_defaults(func=client.cmd_update)

        dg_ar = cmds.add_parser(
            "add-remove", help="POST /devicegroups/{id}/ — add/remove devices"
        )
        dg_ar.add_argument("group_id", help="Device group id")
        dg_ar.add_argument(
            "--add",
            action="append",
            default=[],
            metavar="ID",
            help="Device id(s) to add (repeatable or comma-separated)",
        )
        dg_ar.add_argument(
            "--remove",
            action="append",
            default=[],
            metavar="ID",
            help="Device id(s) to remove (repeatable or comma-separated)",
        )
        dg_ar.set_defaults(func=client.cmd_add_remove)

        dg_del = cmds.add_parser("delete", help="DELETE /devicegroups/{id}/")
        dg_del.add_argument("group_id", help="Device group id")
        dg_del.set_defaults(func=client.cmd_delete)
