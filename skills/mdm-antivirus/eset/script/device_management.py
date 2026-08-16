#!/usr/bin/env python3
"""Device Management — https://help.eset.com/eset_connect/en-US/device_management.html

GET  /v1/device_groups
GET  /v1/device_groups/{groupUuid}/devices
GET  /v1/devices
GET  /v1/devices/{deviceUuid}
POST /v1/devices/{deviceUuid}:move
POST /v1/devices/{deviceUuid}:rename
GET  /v1/devices:batchGet
POST /v1/devices:batchImport
"""

from __future__ import annotations

import argparse
from typing import Any, Iterable, Iterator

from _client import TOKEN_PARENT, ApiError, BaseClient


class DeviceManagementError(ApiError):
    label = "Device Management API"


class DeviceManagementClient(BaseClient):
    error_class = DeviceManagementError
    url_key = "api_url"

    def list_device_groups(
        self, *, page_size: int | None = None, page_token: str | None = None
    ) -> dict:
        return self._request(
            "GET", "/v1/device_groups", params=self._page_params(page_size, page_token)
        )

    def list_devices_in_group(
        self,
        group_uuid: str,
        *,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> dict:
        return self._request(
            "GET",
            f"/v1/device_groups/{group_uuid}/devices",
            params=self._page_params(page_size, page_token),
        )

    def list_devices(
        self, *, page_size: int | None = None, page_token: str | None = None
    ) -> dict:
        return self._request(
            "GET", "/v1/devices", params=self._page_params(page_size, page_token)
        )

    def get_device(self, device_uuid: str) -> dict:
        return self._request("GET", f"/v1/devices/{device_uuid}")

    def move_device(
        self,
        device_uuid: str,
        device_group_uuid: str | None = None,
        *,
        body: dict | None = None,
    ) -> dict:
        payload = body if body is not None else {"deviceGroupUuid": device_group_uuid}
        return self._request(
            "POST", f"/v1/devices/{device_uuid}:move", json_body=payload
        )

    def rename_device(
        self,
        device_uuid: str,
        name: str | None = None,
        *,
        body: dict | None = None,
    ) -> dict:
        payload = body if body is not None else {"name": name}
        return self._request(
            "POST", f"/v1/devices/{device_uuid}:rename", json_body=payload
        )

    def batch_get_devices(self, device_uuids: Iterable[str]) -> dict:
        return self._request(
            "GET", "/v1/devices:batchGet", params={"deviceUuids": list(device_uuids)}
        )

    def batch_import_devices(self, devices: Any) -> dict:
        payload = devices if isinstance(devices, dict) else {"devices": list(devices)}
        return self._request("POST", "/v1/devices:batchImport", json_body=payload)

    def iter_devices(self, *, page_size: int | None = None) -> Iterator[dict]:
        token: str | None = None
        while True:
            page = self.list_devices(page_size=page_size, page_token=token)
            for device in page.get("devices", []) or []:
                yield device
            token = page.get("nextPageToken")
            if not token:
                break

    def iter_device_groups(self, *, page_size: int | None = None) -> Iterator[dict]:
        token: str | None = None
        while True:
            page = self.list_device_groups(page_size=page_size, page_token=token)
            for group in page.get("deviceGroups", []) or []:
                yield group
            token = page.get("nextPageToken")
            if not token:
                break

    def cmd_groups_list(self, args: argparse.Namespace) -> None:
        self.dump(
            self.list_device_groups(
                page_size=args.page_size, page_token=args.page_token
            )
        )
        return None

    def cmd_groups_devices(self, args: argparse.Namespace) -> None:
        self.dump(
            self.list_devices_in_group(
                args.group_uuid,
                page_size=args.page_size,
                page_token=args.page_token,
            )
        )
        return None

    def cmd_list(self, args: argparse.Namespace) -> None:
        self.dump(
            self.list_devices(page_size=args.page_size, page_token=args.page_token)
        )
        return None

    def cmd_get(self, args: argparse.Namespace) -> None:
        self.dump(self.get_device(args.device_uuid))
        return None

    def cmd_move(self, args: argparse.Namespace) -> None:
        self.dump(self.move_device(args.device_uuid, args.group))
        return None

    def cmd_rename(self, args: argparse.Namespace) -> None:
        self.dump(self.rename_device(args.device_uuid, args.name))
        return None

    def cmd_batch_get(self, args: argparse.Namespace) -> None:
        self.dump(self.batch_get_devices(args.device_uuids))
        return None

    def cmd_batch_import(self, args: argparse.Namespace) -> None:
        self.dump(self.batch_import_devices(self.load_json_file(args.file)))
        return None

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = DeviceManagementClient()

        p_groups = sub.add_parser(
            "groups", parents=[TOKEN_PARENT], help="Device groups"
        )
        groups = p_groups.add_subparsers(required=True)

        g_list = groups.add_parser("list", help="GET /v1/device_groups")
        BaseClient.add_paging(g_list)
        g_list.set_defaults(func=client.cmd_groups_list)

        g_devices = groups.add_parser(
            "devices", help="GET /v1/device_groups/{groupUuid}/devices"
        )
        g_devices.add_argument("group_uuid", help="Device group UUID")
        BaseClient.add_paging(g_devices)
        g_devices.set_defaults(func=client.cmd_groups_devices)

        p_devices = sub.add_parser("devices", parents=[TOKEN_PARENT], help="Devices")
        devices = p_devices.add_subparsers(required=True)

        d_list = devices.add_parser("list", help="GET /v1/devices")
        BaseClient.add_paging(d_list)
        d_list.set_defaults(func=client.cmd_list)

        d_get = devices.add_parser("get", help="GET /v1/devices/{deviceUuid}")
        d_get.add_argument("device_uuid", help="Device UUID")
        d_get.set_defaults(func=client.cmd_get)

        d_move = devices.add_parser("move", help="POST /v1/devices/{deviceUuid}:move")
        d_move.add_argument("device_uuid", help="Device UUID")
        d_move.add_argument(
            "--group",
            required=True,
            metavar="GROUP_UUID",
            help="Target device group UUID",
        )
        d_move.set_defaults(func=client.cmd_move)

        d_rename = devices.add_parser(
            "rename", help="POST /v1/devices/{deviceUuid}:rename"
        )
        d_rename.add_argument("device_uuid", help="Device UUID")
        d_rename.add_argument("--name", required=True, help="New device name")
        d_rename.set_defaults(func=client.cmd_rename)

        d_bget = devices.add_parser("batch-get", help="GET /v1/devices:batchGet")
        d_bget.add_argument("device_uuids", nargs="+", help="One or more device UUIDs")
        d_bget.set_defaults(func=client.cmd_batch_get)

        d_bimport = devices.add_parser(
            "batch-import", help="POST /v1/devices:batchImport"
        )
        d_bimport.add_argument(
            "--file",
            required=True,
            help="JSON file: a devices list or a full request body",
        )
        d_bimport.set_defaults(func=client.cmd_batch_import)
