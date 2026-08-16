#!/usr/bin/env python3
"""ESET Connect — Incident Management: Detections + DetectionGroups.

Implements the Detections and DetectionGroups endpoints documented at
https://help.eset.com/eset_connect/en-US/incident_management.html:

Detections
    GET  /v1/detections                                 list_detections("v1")
    GET  /v1/detections/{detectionUuid}                 get_detection("v1")
    GET  /v2/detections                                 list_detections("v2")
    GET  /v2/detections/{detectionUuid}                 get_detection("v2")
    POST /v2/detections/{detectionUuid}:resolve         resolve_detection()
    POST /v2/detections:batchGet                        batch_get_detections()

DetectionGroups
    GET  /v2/detection-groups                           list_detection_groups()
    GET  /v2/detection-groups/{detectionGroupUuid}      get_detection_group()
    POST /v2/detection-groups/{groupUuid}:resolve       resolve_detection_group()
    POST /v2/detection-groups:search                    search_detection_groups()

v1 detections work for ESET PROTECT and ESET Inspect. v2 detections are for ESET
Cloud Office Security (list) and ESET Inspect. The Incident Management gateway is
``https://<region>.incident-management.eset.systems`` (resolved by ``cli.py`` as
``incident_url``, override ``ESET_INCIDENT_URL``). The client only needs that base
URL and a Bearer access token.
"""

from __future__ import annotations

import argparse
from typing import Iterable, Iterator

from _client import TOKEN_PARENT, ApiError, BaseClient


class DetectionsError(ApiError):
    """Raised when a Detections/DetectionGroups API call fails."""

    label = "Incident Management API"


class DetectionsClient(BaseClient):
    """Client over the ESET Connect Detections + DetectionGroups endpoints."""

    error_class = DetectionsError
    url_key = "incident_url"


    def list_detections(
        self,
        version: str = "v1",
        *,
        device_uuid: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> dict:
        """GET /{version}/detections — List detections (``version`` = v1 or v2).

        ``device_uuid`` / ``start_time`` / ``end_time`` are optional filters
        (timestamps in UTC or offset format, e.g. ``2024-10-30T12:00Z``).
        """
        extra: dict = {}
        if device_uuid:
            extra["deviceUuid"] = device_uuid
        if start_time:
            extra["startTime"] = start_time
        if end_time:
            extra["endTime"] = end_time
        return self._request(
            "GET",
            f"/{version}/detections",
            params=self._page_params(page_size, page_token, extra),
        )

    def get_detection(self, detection_uuid: str, version: str = "v1") -> dict:
        """GET /{version}/detections/{detectionUuid} — Get detection details."""
        return self._request("GET", f"/{version}/detections/{detection_uuid}")

    def resolve_detection(
        self, detection_uuid: str, note: str | None = None, *, body: dict | None = None
    ) -> dict:
        """POST /v2/detections/{detectionUuid}:resolve — Mark a detection resolved.

        Pass *note* (sent as ``{"note": ...}``) or a raw *body* dict.
        """
        payload = body if body is not None else {"note": note}
        return self._request(
            "POST", f"/v2/detections/{detection_uuid}:resolve", json_body=payload
        )

    def batch_get_detections(self, detection_uuids: Iterable[str]) -> dict:
        """POST /v2/detections:batchGet — Batch-get detections by UUID (atomic)."""
        payload = {"detectionUuids": list(detection_uuids)}
        return self._request("POST", "/v2/detections:batchGet", json_body=payload)


    def list_detection_groups(
        self, *, page_size: int | None = None, page_token: str | None = None
    ) -> dict:
        """GET /v2/detection-groups — List detection groups."""
        return self._request(
            "GET",
            "/v2/detection-groups",
            params=self._page_params(page_size, page_token),
        )

    def get_detection_group(self, detection_group_uuid: str) -> dict:
        """GET /v2/detection-groups/{detectionGroupUuid} — Get a detection group."""
        return self._request(
            "GET", f"/v2/detection-groups/{detection_group_uuid}"
        )

    def resolve_detection_group(
        self,
        detection_group_uuid: str,
        note: str | None = None,
        *,
        body: dict | None = None,
    ) -> dict:
        """POST /v2/detection-groups/{groupUuid}:resolve — Resolve every detection
        in a group.

        Pass *note* (sent as ``{"note": ...}``) or a raw *body* dict.
        """
        payload = body if body is not None else {"note": note}
        return self._request(
            "POST",
            f"/v2/detection-groups/{detection_group_uuid}:resolve",
            json_body=payload,
        )

    def search_detection_groups(
        self,
        filter: str | None = None,
        *,
        return_total_size: bool | None = None,
        body: dict | None = None,
    ) -> dict:
        """POST /v2/detection-groups:search — Search detection groups by filter.

        ``filter`` uses eq/ne/gt/ge/lt/le/and/or operators, e.g.
        ``resolved eq 0``. Pass a raw *body* dict to override the payload.
        """
        if body is not None:
            payload = body
        else:
            payload = {}
            if filter is not None:
                payload["filter"] = filter
            if return_total_size is not None:
                payload["returnTotalSize"] = return_total_size
        return self._request(
            "POST", "/v2/detection-groups:search", json_body=payload
        )


    def iter_detections(
        self, version: str = "v1", *, page_size: int | None = None
    ) -> Iterator[dict]:
        """Yield every detection, following ``nextPageToken`` pagination."""
        token: str | None = None
        while True:
            page = self.list_detections(
                version, page_size=page_size, page_token=token
            )
            for detection in page.get("detections", []) or []:
                yield detection
            token = page.get("nextPageToken")
            if not token:
                break

    def iter_detection_groups(self, *, page_size: int | None = None) -> Iterator[dict]:
        """Yield every detection group, following ``nextPageToken`` pagination."""
        token: str | None = None
        while True:
            page = self.list_detection_groups(page_size=page_size, page_token=token)
            for group in page.get("detectionGroups", []) or []:
                yield group
            token = page.get("nextPageToken")
            if not token:
                break

    def cmd_list(self, args: argparse.Namespace) -> None:
        self.dump(
            self.list_detections(
                args.version,
                device_uuid=args.device,
                start_time=args.start_time,
                end_time=args.end_time,
                page_size=args.page_size,
                page_token=args.page_token,
            )
        )
        return None

    def cmd_get(self, args: argparse.Namespace) -> None:
        self.dump(self.get_detection(args.detection_uuid, args.version))
        return None

    def cmd_resolve(self, args: argparse.Namespace) -> None:
        self.dump(self.resolve_detection(args.detection_uuid, args.note))
        return None

    def cmd_batch_get(self, args: argparse.Namespace) -> None:
        self.dump(self.batch_get_detections(args.detection_uuids))
        return None

    def cmd_groups_list(self, args: argparse.Namespace) -> None:
        self.dump(
            self.list_detection_groups(
                page_size=args.page_size, page_token=args.page_token
            )
        )
        return None

    def cmd_groups_get(self, args: argparse.Namespace) -> None:
        self.dump(self.get_detection_group(args.group_uuid))
        return None

    def cmd_groups_resolve(self, args: argparse.Namespace) -> None:
        self.dump(self.resolve_detection_group(args.group_uuid, args.note))
        return None

    def cmd_groups_search(self, args: argparse.Namespace) -> None:
        self.dump(
            self.search_detection_groups(
                args.filter, return_total_size=args.total_size
            )
        )
        return None

    @staticmethod
    def _add_version(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--version",
            choices=["v1", "v2"],
            default="v1",
            help="API version (v1 = PROTECT/Inspect, v2 = Cloud Office Security/Inspect)",
        )

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = DetectionsClient()

        p_det = sub.add_parser(
            "detections",
            parents=[TOKEN_PARENT],
            help="Incident Management (detections)",
        )
        det = p_det.add_subparsers(required=True)

        dt_list = det.add_parser("list", help="GET /{version}/detections")
        DetectionsClient._add_version(dt_list)
        dt_list.add_argument(
            "--device", metavar="DEVICE_UUID", help="Filter by device UUID"
        )
        dt_list.add_argument("--start-time", help="Filter: occurred after (ISO 8601)")
        dt_list.add_argument("--end-time", help="Filter: occurred before (ISO 8601)")
        BaseClient.add_paging(dt_list)
        dt_list.set_defaults(func=client.cmd_list)

        dt_get = det.add_parser(
            "get", help="GET /{version}/detections/{detectionUuid}"
        )
        dt_get.add_argument("detection_uuid", help="Detection UUID")
        DetectionsClient._add_version(dt_get)
        dt_get.set_defaults(func=client.cmd_get)

        dt_resolve = det.add_parser(
            "resolve", help="POST /v2/detections/{detectionUuid}:resolve"
        )
        dt_resolve.add_argument("detection_uuid", help="Detection UUID")
        dt_resolve.add_argument("--note", help="Text explaining the resolution")
        dt_resolve.set_defaults(func=client.cmd_resolve)

        dt_bget = det.add_parser("batch-get", help="POST /v2/detections:batchGet")
        dt_bget.add_argument(
            "detection_uuids", nargs="+", help="One or more detection UUIDs"
        )
        dt_bget.set_defaults(func=client.cmd_batch_get)

        p_dg = sub.add_parser(
            "detection-groups",
            parents=[TOKEN_PARENT],
            help="Incident Management (detection groups)",
        )
        dg = p_dg.add_subparsers(required=True)

        dg_list = dg.add_parser("list", help="GET /v2/detection-groups")
        BaseClient.add_paging(dg_list)
        dg_list.set_defaults(func=client.cmd_groups_list)

        dg_get = dg.add_parser("get", help="GET /v2/detection-groups/{groupUuid}")
        dg_get.add_argument("group_uuid", help="Detection group UUID")
        dg_get.set_defaults(func=client.cmd_groups_get)

        dg_resolve = dg.add_parser(
            "resolve", help="POST /v2/detection-groups/{groupUuid}:resolve"
        )
        dg_resolve.add_argument("group_uuid", help="Detection group UUID")
        dg_resolve.add_argument("--note", help="Text explaining the resolution")
        dg_resolve.set_defaults(func=client.cmd_groups_resolve)

        dg_search = dg.add_parser("search", help="POST /v2/detection-groups:search")
        dg_search.add_argument("--filter", help="Filter, e.g. \"resolved eq 0\"")
        dg_search.add_argument(
            "--total-size",
            action="store_true",
            help="Compute total_size in the response",
        )
        dg_search.set_defaults(func=client.cmd_groups_search)
