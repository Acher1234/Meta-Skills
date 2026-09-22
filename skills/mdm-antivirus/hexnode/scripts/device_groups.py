"""Hexnode Device Groups API — https://www.hexnode.com/mobile-device-management/developers/device-groups/

GET    /devicegroups/                 list_device_groups
POST   /devicegroups/                 create_device_group
GET    /devicegroups/{id}/            get_device_group
PUT    /devicegroups/{id}/            update_device_group
POST   /devicegroups/{id}/            add_remove_devices
DELETE /devicegroups/{id}/            delete_device_group
"""

from __future__ import annotations

from typing import Any, Iterable

from client import HexnodeClient


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
