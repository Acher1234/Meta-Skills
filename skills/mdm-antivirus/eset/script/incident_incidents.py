#!/usr/bin/env python3
"""ESET Connect — Incident Management: Incidents + IncidentComments.

Implements the Incidents and IncidentComments endpoints documented at
https://help.eset.com/eset_connect/en-US/incident_management.html:

Incidents
    GET  /v2/incidents                                          list_incidents()
    GET  /v2/incidents/{incidentUuid}                           get_incident()
    POST /v2/incidents/{incidentUuid}/basic-attributes:update   update_incident_basic_attributes()
    POST /v2/incidents/{incidentUuid}:close                     close_incident()
    POST /v2/incidents/{incidentUuid}:reopen                    reopen_incident()

IncidentComments
    GET    /v2/incidents/{incidentUuid}/comments                list_incident_comments()
    POST   /v2/incidents/{incidentUuid}/comments                create_incident_comment()
    GET    /v2/incidents/{incidentUuid}/comments/{commentUuid}  get_incident_comment()
    DELETE /v2/incidents/{incidentUuid}/comments/{commentUuid}  delete_incident_comment()
    POST   /v2/incidents/{incidentUuid}/comments/{commentUuid}/text:update
                                                        update_incident_comment_text()

Incident endpoints require an ESET Inspect subscription. The Incident Management
gateway is ``https://<region>.incident-management.eset.systems`` (resolved by
``cli.py`` as ``incident_url``, override ``ESET_INCIDENT_URL``). The client only
needs that base URL and a Bearer access token.
"""

from __future__ import annotations

from typing import Iterator

from _client import ApiError, BaseClient


class IncidentsError(ApiError):
    """Raised when an Incidents/IncidentComments API call fails."""

    label = "Incident Management API"


class IncidentsClient(BaseClient):
    """Client over the ESET Connect Incidents + IncidentComments endpoints."""

    error_class = IncidentsError


    def list_incidents(
        self, *, page_size: int | None = None, page_token: str | None = None
    ) -> dict:
        """GET /v2/incidents — List incidents."""
        return self._request(
            "GET", "/v2/incidents", params=self._page_params(page_size, page_token)
        )

    def get_incident(self, incident_uuid: str) -> dict:
        """GET /v2/incidents/{incidentUuid} — Get incident details."""
        return self._request("GET", f"/v2/incidents/{incident_uuid}")

    def update_incident_basic_attributes(
        self,
        incident_uuid: str,
        *,
        assignee_uuid: str | None = None,
        description: str | None = None,
        display_name: str | None = None,
        severity: str | None = None,
        update_mask: str | None = None,
        body: dict | None = None,
    ) -> dict:
        """POST /v2/incidents/{incidentUuid}/basic-attributes:update.

        Only the fields listed in ``update_mask`` (comma-separated lower camel
        case, e.g. ``displayName,severity``) are changed. When *body* is omitted,
        *update_mask* is derived from the provided keyword arguments.
        """
        if body is not None:
            payload = body
        else:
            payload = {}
            mask: list[str] = []
            if assignee_uuid is not None:
                payload["assigneeUuid"] = assignee_uuid
                mask.append("assigneeUuid")
            if description is not None:
                payload["description"] = description
                mask.append("description")
            if display_name is not None:
                payload["displayName"] = display_name
                mask.append("displayName")
            if severity is not None:
                payload["severity"] = severity
                mask.append("severity")
            payload["updateMask"] = update_mask if update_mask is not None else ",".join(mask)
        return self._request(
            "POST",
            f"/v2/incidents/{incident_uuid}/basic-attributes:update",
            json_body=payload,
        )

    def close_incident(
        self,
        incident_uuid: str,
        *,
        closure_reason: str | None = None,
        final_comment: str | None = None,
        body: dict | None = None,
    ) -> dict:
        """POST /v2/incidents/{incidentUuid}:close — Close an incident.

        *closure_reason* is one of the ``INCIDENT_RESOLVE_REASON_*`` values;
        *final_comment* text is wrapped as ``{"text": ...}``. Pass a raw *body*
        dict to override the payload.
        """
        if body is not None:
            payload = body
        else:
            payload = {}
            if closure_reason is not None:
                payload["closureReason"] = closure_reason
            if final_comment is not None:
                payload["finalComment"] = {"text": final_comment}
        return self._request(
            "POST", f"/v2/incidents/{incident_uuid}:close", json_body=payload
        )

    def reopen_incident(self, incident_uuid: str, *, body: dict | None = None) -> dict:
        """POST /v2/incidents/{incidentUuid}:reopen — Reopen a closed incident."""
        return self._request(
            "POST",
            f"/v2/incidents/{incident_uuid}:reopen",
            json_body=body if body is not None else {},
        )


    def list_incident_comments(
        self,
        incident_uuid: str,
        *,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> dict:
        """GET /v2/incidents/{incidentUuid}/comments — List incident comments."""
        return self._request(
            "GET",
            f"/v2/incidents/{incident_uuid}/comments",
            params=self._page_params(page_size, page_token),
        )

    def create_incident_comment(
        self,
        incident_uuid: str,
        text: str | None = None,
        *,
        body: dict | None = None,
    ) -> dict:
        """POST /v2/incidents/{incidentUuid}/comments — Create an incident comment.

        Pass *text* (wrapped as ``{"comment": {"text": ...}}``) or a raw *body*
        dict.
        """
        payload = body if body is not None else {"comment": {"text": text}}
        return self._request(
            "POST", f"/v2/incidents/{incident_uuid}/comments", json_body=payload
        )

    def get_incident_comment(self, incident_uuid: str, comment_uuid: str) -> dict:
        """GET /v2/incidents/{incidentUuid}/comments/{commentUuid} — Get comment."""
        return self._request(
            "GET", f"/v2/incidents/{incident_uuid}/comments/{comment_uuid}"
        )

    def delete_incident_comment(self, incident_uuid: str, comment_uuid: str) -> dict:
        """DELETE /v2/incidents/{incidentUuid}/comments/{commentUuid} — Delete."""
        return self._request(
            "DELETE", f"/v2/incidents/{incident_uuid}/comments/{comment_uuid}"
        )

    def update_incident_comment_text(
        self,
        incident_uuid: str,
        comment_uuid: str,
        text: str | None = None,
        *,
        body: dict | None = None,
    ) -> dict:
        """POST /v2/incidents/{incidentUuid}/comments/{commentUuid}/text:update.

        Pass *text* (sent as ``{"text": ...}``) or a raw *body* dict.
        """
        payload = body if body is not None else {"text": text}
        return self._request(
            "POST",
            f"/v2/incidents/{incident_uuid}/comments/{comment_uuid}/text:update",
            json_body=payload,
        )


    def iter_incidents(self, *, page_size: int | None = None) -> Iterator[dict]:
        """Yield every incident, following ``nextPageToken`` pagination."""
        token: str | None = None
        while True:
            page = self.list_incidents(page_size=page_size, page_token=token)
            for incident in page.get("incidents", []) or []:
                yield incident
            token = page.get("nextPageToken")
            if not token:
                break

    def iter_incident_comments(
        self, incident_uuid: str, *, page_size: int | None = None
    ) -> Iterator[dict]:
        """Yield every comment of an incident, following ``nextPageToken``."""
        token: str | None = None
        while True:
            page = self.list_incident_comments(
                incident_uuid, page_size=page_size, page_token=token
            )
            for comment in page.get("comments", []) or []:
                yield comment
            token = page.get("nextPageToken")
            if not token:
                break
