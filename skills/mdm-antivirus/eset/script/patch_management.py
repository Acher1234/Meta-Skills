#!/usr/bin/env python3
"""Patch Management — https://help.eset.com/eset_connect/en-US/patch_management.html

GET /v1/device-patches
GET /v1/application-patching-processes/recent/details
GET /v1/patching-process-details
"""

from __future__ import annotations

from typing import Iterator

from _client import ApiError, BaseClient


class PatchManagementError(ApiError):
    label = "Patch Management API"


class PatchManagementClient(BaseClient):
    error_class = PatchManagementError

    def list_device_patches(
        self,
        *,
        device_uuid: str | None = None,
        device_group_uuid: str | None = None,
        patch_type: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> dict:
        """GET /v1/device-patches — list pending patches per device."""
        extra: dict = {}
        if device_uuid:
            extra["deviceUuid"] = device_uuid
        if device_group_uuid:
            extra["deviceGroupUuid"] = device_group_uuid
        if patch_type:
            extra["patchType"] = patch_type
        return self._request(
            "GET",
            "/v1/device-patches",
            params=self._page_params(page_size, page_token, extra),
        )

    def list_recent_application_patching_details(self) -> dict:
        """GET /v1/application-patching-processes/recent/details."""
        return self._request(
            "GET", "/v1/application-patching-processes/recent/details"
        )

    def list_patching_process_details(
        self,
        *,
        device_uuid: str | None = None,
        device_group_uuid: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> dict:
        """GET /v1/patching-process-details."""
        extra: dict = {}
        if device_uuid:
            extra["deviceUuid"] = device_uuid
        if device_group_uuid:
            extra["deviceGroupUuid"] = device_group_uuid
        return self._request(
            "GET",
            "/v1/patching-process-details",
            params=self._page_params(page_size, page_token, extra),
        )

    def iter_device_patches(
        self,
        *,
        device_uuid: str | None = None,
        device_group_uuid: str | None = None,
        patch_type: str | None = None,
        page_size: int | None = None,
    ) -> Iterator[dict]:
        token: str | None = None
        while True:
            page = self.list_device_patches(
                device_uuid=device_uuid,
                device_group_uuid=device_group_uuid,
                patch_type=patch_type,
                page_size=page_size,
                page_token=token,
            )
            for item in page.get("devicePatches", []) or page.get("patches", []) or []:
                yield item
            token = page.get("nextPageToken")
            if not token:
                break
