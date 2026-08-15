#!/usr/bin/env python3
"""Patch Management — https://help.eset.com/eset_connect/en-US/patch_management.html

GET /v1/device-patches
GET /v1/application-patching-processes/recent/details
GET /v1/patching-process-details
"""

from __future__ import annotations

import argparse
from typing import Iterator

from _client import TOKEN_PARENT, ApiError, BaseClient


class PatchManagementError(ApiError):
    label = "Patch Management API"


class PatchManagementClient(BaseClient):
    error_class = PatchManagementError
    url_key = "patch_url"

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

    def cmd_list(self, args: argparse.Namespace) -> None:
        self.dump(
            self.list_device_patches(
                device_uuid=args.device,
                device_group_uuid=args.group,
                patch_type=args.patch_type,
                page_size=args.page_size,
                page_token=args.page_token,
            )
        )
        return None

    def cmd_recent(self, args: argparse.Namespace) -> None:
        self.dump(self.list_recent_application_patching_details())
        return None

    def cmd_details(self, args: argparse.Namespace) -> None:
        self.dump(
            self.list_patching_process_details(
                page_size=args.page_size, page_token=args.page_token
            )
        )
        return None

    def cmd_apply(self, args: argparse.Namespace) -> None:
        from automation import (
            AutomationClient,
            build_apply_patch_params,
            build_task,
            build_targets,
        )

        client = AutomationClient()
        client.dump(
            client.create_task(
                build_task(
                    "ApplyApplicationPatch",
                    params=build_apply_patch_params(args.application_uuid),
                    targets=build_targets(devices=args.device, groups=args.group),
                    display_name=args.display_name,
                    description=args.description,
                    expire_time=args.expire_time,
                )
            )
        )
        return None

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = PatchManagementClient()
        p = sub.add_parser(
            "patches",
            parents=[TOKEN_PARENT],
            help="Patch Management (pending device patches + apply)",
        )
        cmds = p.add_subparsers(required=True)

        pt_list = cmds.add_parser("list", help="GET /v1/device-patches")
        pt_list.add_argument("--device", help="Filter by device UUID")
        pt_list.add_argument(
            "--group",
            help="Filter by device-group UUID (nested groups included)",
        )
        pt_list.add_argument(
            "--patch-type",
            choices=[
                "PATCH_TYPE_UNSPECIFIED",
                "PATCH_TYPE_APPLICATION",
                "PATCH_TYPE_OPERATING_SYSTEM",
                "PATCH_TYPE_PACKAGE",
            ],
            help="Filter by patch category",
        )
        BaseClient.add_paging(pt_list)
        pt_list.set_defaults(func=client.cmd_list)

        cmds.add_parser(
            "recent",
            help="GET /v1/application-patching-processes/recent/details",
        ).set_defaults(func=client.cmd_recent)

        pt_details = cmds.add_parser(
            "details", help="GET /v1/patching-process-details"
        )
        BaseClient.add_paging(pt_details)
        pt_details.set_defaults(func=client.cmd_details)

        pt_apply = cmds.add_parser(
            "apply",
            help="POST /v1/device_tasks ApplyApplicationPatch (Automation)",
        )
        pt_apply.add_argument(
            "--device",
            action="append",
            default=[],
            metavar="UUID",
            help="Target device UUID (repeatable)",
        )
        pt_apply.add_argument(
            "--group",
            action="append",
            default=[],
            metavar="UUID",
            help="Target device-group UUID (repeatable)",
        )
        pt_apply.add_argument(
            "--application-uuid",
            required=True,
            help="Application UUID from patches list (devices[].uuid / applicationUuid)",
        )
        pt_apply.add_argument("--display-name", help="Task display name")
        pt_apply.add_argument("--description", help="Task description")
        pt_apply.add_argument(
            "--expire-time",
            metavar="RFC3339",
            help="Manual trigger expireTime (e.g. 2026-03-21T11:30:34Z)",
        )
        pt_apply.set_defaults(func=client.cmd_apply)
