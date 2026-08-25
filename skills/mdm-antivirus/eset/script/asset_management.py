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
    url_key = "asset_url"

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

    def cmd_create(self, args: argparse.Namespace) -> None:
        self.dump(self.create_group(args.name, args.parent))
        return None

    def cmd_delete(self, args: argparse.Namespace) -> None:
        self.dump(self.delete_group(args.group_uuid))
        return None

    def cmd_move(self, args: argparse.Namespace) -> None:
        self.dump(self.move_group(args.group_uuid, args.parent))
        return None

    def cmd_rename(self, args: argparse.Namespace) -> None:
        self.dump(self.rename_group(args.group_uuid, args.name))
        return None

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = AssetManagementClient()
        p = sub.add_parser(
            "assets",
            parents=[TOKEN_PARENT],
            help="Asset Management (group create/delete/move/rename)",
        )
        cmds = p.add_subparsers(required=True)

        a_create = cmds.add_parser("create", help="POST /v1/groups")
        a_create.add_argument("--name", required=True, help="New group name")
        a_create.add_argument("--parent", metavar="PARENT_UUID", help="Parent group UUID")
        a_create.set_defaults(func=client.cmd_create)

        a_delete = cmds.add_parser("delete", help="DELETE /v1/groups/{groupUuid}")
        a_delete.add_argument("group_uuid", help="Group UUID")
        a_delete.set_defaults(func=client.cmd_delete)

        a_move = cmds.add_parser("move", help="POST /v1/groups/{groupUuid}:move")
        a_move.add_argument("group_uuid", help="Group UUID")
        a_move.add_argument(
            "--parent",
            required=True,
            metavar="PARENT_UUID",
            help="Target parent group UUID",
        )
        a_move.set_defaults(func=client.cmd_move)

        a_rename = cmds.add_parser("rename", help="POST /v1/groups/{groupUuid}:rename")
        a_rename.add_argument("group_uuid", help="Group UUID")
        a_rename.add_argument("--name", required=True, help="New group name")
        a_rename.set_defaults(func=client.cmd_rename)
