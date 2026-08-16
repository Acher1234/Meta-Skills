#!/usr/bin/env python3
"""Application Management — https://help.eset.com/eset_connect/en-US/application_management.html

GET  /v1/executables
GET  /v1/executables/{executableUuid}
POST /v1/executables/{executableUuid}:block
POST /v1/executables/{executableUuid}:unblock
"""

from __future__ import annotations

import argparse
from typing import Iterator

from _client import TOKEN_PARENT, ApiError, BaseClient


class ApplicationManagementError(ApiError):
    label = "Application Management API"


class ApplicationManagementClient(BaseClient):
    error_class = ApplicationManagementError
    url_key = "app_url"

    def list_executables(
        self, *, page_size: int | None = None, page_token: str | None = None
    ) -> dict:
        return self._request(
            "GET", "/v1/executables", params=self._page_params(page_size, page_token)
        )

    def get_executable(self, executable_uuid: str) -> dict:
        return self._request("GET", f"/v1/executables/{executable_uuid}")

    def block_executable(
        self, executable_uuid: str, *, body: dict | None = None
    ) -> dict:
        return self._request(
            "POST",
            f"/v1/executables/{executable_uuid}:block",
            json_body=body if body is not None else {},
        )

    def unblock_executable(
        self, executable_uuid: str, *, body: dict | None = None
    ) -> dict:
        return self._request(
            "POST",
            f"/v1/executables/{executable_uuid}:unblock",
            json_body=body if body is not None else {},
        )

    def iter_executables(self, *, page_size: int | None = None) -> Iterator[dict]:
        token: str | None = None
        while True:
            page = self.list_executables(page_size=page_size, page_token=token)
            for executable in page.get("executables", []) or []:
                yield executable
            token = page.get("nextPageToken")
            if not token:
                break

    def cmd_list(self, args: argparse.Namespace) -> None:
        self.dump(
            self.list_executables(page_size=args.page_size, page_token=args.page_token)
        )
        return None

    def cmd_get(self, args: argparse.Namespace) -> None:
        self.dump(self.get_executable(args.executable_uuid))
        return None

    def cmd_block(self, args: argparse.Namespace) -> None:
        self.dump(self.block_executable(args.executable_uuid))
        return None

    def cmd_unblock(self, args: argparse.Namespace) -> None:
        self.dump(self.unblock_executable(args.executable_uuid))
        return None

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = ApplicationManagementClient()
        p = sub.add_parser(
            "executables",
            parents=[TOKEN_PARENT],
            help="Application Management (executables)",
        )
        cmds = p.add_subparsers(required=True)

        e_list = cmds.add_parser("list", help="GET /v1/executables")
        BaseClient.add_paging(e_list)
        e_list.set_defaults(func=client.cmd_list)

        e_get = cmds.add_parser("get", help="GET /v1/executables/{executableUuid}")
        e_get.add_argument("executable_uuid", help="Executable UUID")
        e_get.set_defaults(func=client.cmd_get)

        e_block = cmds.add_parser(
            "block", help="POST /v1/executables/{executableUuid}:block"
        )
        e_block.add_argument("executable_uuid", help="Executable UUID")
        e_block.set_defaults(func=client.cmd_block)

        e_unblock = cmds.add_parser(
            "unblock", help="POST /v1/executables/{executableUuid}:unblock"
        )
        e_unblock.add_argument("executable_uuid", help="Executable UUID")
        e_unblock.set_defaults(func=client.cmd_unblock)
