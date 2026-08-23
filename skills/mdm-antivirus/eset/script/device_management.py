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

from typing import Any, Iterable, Iterator

from _client import ApiError, BaseClient


class DeviceManagementError(ApiError):
    label = "Device Management API"


class DeviceManagementClient(BaseClient):
    error_class = DeviceManagementError

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
