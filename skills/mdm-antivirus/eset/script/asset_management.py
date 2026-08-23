#!/usr/bin/env python3
"""Asset Management — https://help.eset.com/eset_connect/en-US/asset_management.html

POST   /v1/groups
DELETE /v1/groups/{groupUuid}
POST   /v1/groups/{groupUuid}:move
POST   /v1/groups/{groupUuid}:rename
"""

from __future__ import annotations

from _client import ApiError, BaseClient


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
            payload = {"name": name}
            if parent_group_uuid:
                payload["parentGroupUuid"] = parent_group_uuid
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
        payload = body if body is not None else {"parentGroupUuid": parent_group_uuid}
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
        payload = body if body is not None else {"name": name}
        return self._request(
            "POST", f"/v1/groups/{group_uuid}:rename", json_body=payload
        )
