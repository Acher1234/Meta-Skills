"""Hexnode Devices API — https://www.hexnode.com/mobile-device-management/developers/devices/

GET /devices/                              list_devices
GET /devices/{id}/                         get_device
GET /devices/{id}/policies/                list_device_policies
GET /devices/{id}/applications/            list_device_applications
GET /devices/{id}/locations/               list_device_locations
"""

from __future__ import annotations

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
