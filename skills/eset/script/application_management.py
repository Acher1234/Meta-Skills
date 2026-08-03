#!/usr/bin/env python3
"""Application Management — https://help.eset.com/eset_connect/en-US/application_management.html

GET  /v1/executables
GET  /v1/executables/{executableUuid}
POST /v1/executables/{executableUuid}:block
POST /v1/executables/{executableUuid}:unblock
"""

from __future__ import annotations

from typing import Iterator

from _client import ApiError, BaseClient


class ApplicationManagementError(ApiError):
    label = "Application Management API"


class ApplicationManagementClient(BaseClient):
    error_class = ApplicationManagementError

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
