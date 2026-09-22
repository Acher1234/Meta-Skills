#!/usr/bin/env python3
"""Asset Management — https://help.eset.com/eset_connect/en-US/asset_management.html"""

from __future__ import annotations

import argparse
from typing import Any

from _client import TOKEN_PARENT, ApiError, BaseClient


class AssetManagementError(ApiError):
    label = "Asset Management API"


class AssetManagementClient(BaseClient):
    error_class = AssetManagementError

    def create_group(
        self,
        name: str | None = None,
        parent_group_uuid: str | None = None,
        *,
        body: dict | None = None,
    ) -> dict:
        if body is not None:
            payload = body
        else:
            group: dict[str, Any] = {"displayName": name}
            if parent_group_uuid:
                group["parentGroupUuid"] = parent_group_uuid
            payload = {"group": group}
        return self._request("POST", "/v1/groups", json_body=payload)

    def delete_group(self, group_uuid: str) -> dict:
        return self._request("DELETE", f"/v1/groups/{group_uuid}")

    def move_group(
        self,
        group_uuid: str,
        parent_group_uuid: str | None = None,
        *,
        body: dict | None = None,
    ) -> dict:
        payload = (
            body if body is not None else {"newParentUuid": parent_group_uuid}
        )
        return self._request(
            "POST", f"/v1/groups/{group_uuid}:move", json_body=payload
        )

    def rename_group(
        self,
        group_uuid: str,
        name: str | None = None,
        *,
        body: dict | None = None,
    ) -> dict:
        payload = body if body is not None else {"displayName": name}
        return self._request(
            "POST", f"/v1/groups/{group_uuid}:rename", json_body=payload
        )
