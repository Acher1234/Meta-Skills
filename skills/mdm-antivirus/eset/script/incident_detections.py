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

from typing import Iterable, Iterator

from _client import ApiError, BaseClient


class DetectionsError(ApiError):
    """Raised when a Detections/DetectionGroups API call fails."""

    label = "Incident Management API"


class DetectionsClient(BaseClient):
    """Client over the ESET Connect Detections + DetectionGroups endpoints."""

    error_class = DetectionsError


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
