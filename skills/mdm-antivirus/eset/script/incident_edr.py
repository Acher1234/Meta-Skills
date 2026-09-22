#!/usr/bin/env python3
"""ESET Connect — Incident Management: EdrRules + EdrRuleExclusions.

Implements the EdrRules and EdrRuleExclusions endpoints documented at
https://help.eset.com/eset_connect/en-US/incident_management.html:

EdrRules
    GET    /v2/edr-rules                                     list_edr_rules()
    POST   /v2/edr-rules                                     create_edr_rule()
    GET    /v2/edr-rules/{ruleUuid}                          get_edr_rule()
    DELETE /v2/edr-rules/{ruleUuid}                          delete_edr_rule()
    POST   /v2/edr-rules/{ruleUuid}:disable                 disable_edr_rule()
    POST   /v2/edr-rules/{ruleUuid}:enable                  enable_edr_rule()
    POST   /v2/edr-rules/{ruleUuid}:updateDefinition        update_edr_rule_definition()

EdrRuleExclusions
    GET    /v2/edr-rule-exclusions                           list_edr_rule_exclusions()
    POST   /v2/edr-rule-exclusions                           create_edr_rule_exclusion()
    GET    /v2/edr-rule-exclusions/{exclusionUuid}           get_edr_rule_exclusion()
    DELETE /v2/edr-rule-exclusions/{exclusionUuid}           delete_edr_rule_exclusion()
    POST   /v2/edr-rule-exclusions/{exclusionUuid}:updateDefinition
                                                    update_edr_rule_exclusion_definition()

EDR endpoints require an ESET Inspect subscription. The Incident Management
gateway is ``https://<region>.incident-management.eset.systems`` (resolved by
``cli.py`` as ``incident_url``, override ``ESET_INCIDENT_URL``). The client only
needs that base URL and a Bearer access token.
"""

from __future__ import annotations

from typing import Iterator

from _client import ApiError, BaseClient


class EdrError(ApiError):
    """Raised when an EdrRules/EdrRuleExclusions API call fails."""

    label = "Incident Management API"


class EdrClient(BaseClient):
    """Client over the ESET Connect EdrRules + EdrRuleExclusions endpoints."""

    error_class = EdrError


    def list_edr_rules(
        self, *, page_size: int | None = None, page_token: str | None = None
    ) -> dict:
        """GET /v2/edr-rules — List EDR rules."""
        return self._request(
            "GET", "/v2/edr-rules", params=self._page_params(page_size, page_token)
        )

    def create_edr_rule(
        self, rule: dict | None = None, *, body: dict | None = None
    ) -> dict:
        """POST /v2/edr-rules — Create an EDR rule.

        Pass *rule* (wrapped as ``{"rule": {...}}``) with keys like ``enabled``,
        ``scopes``, ``severityLevel``, ``xmlDefinition``; or a raw *body* dict.
        """
        payload = body if body is not None else {"rule": rule or {}}
        return self._request("POST", "/v2/edr-rules", json_body=payload)

    def get_edr_rule(self, rule_uuid: str) -> dict:
        """GET /v2/edr-rules/{ruleUuid} — Get an EDR rule."""
        return self._request("GET", f"/v2/edr-rules/{rule_uuid}")

    def delete_edr_rule(self, rule_uuid: str) -> dict:
        """DELETE /v2/edr-rules/{ruleUuid} — Delete an EDR rule."""
        return self._request("DELETE", f"/v2/edr-rules/{rule_uuid}")

    def enable_edr_rule(self, rule_uuid: str, *, body: dict | None = None) -> dict:
        """POST /v2/edr-rules/{ruleUuid}:enable — Enable an EDR rule."""
        return self._request(
            "POST",
            f"/v2/edr-rules/{rule_uuid}:enable",
            json_body=body if body is not None else {},
        )

    def disable_edr_rule(self, rule_uuid: str, *, body: dict | None = None) -> dict:
        """POST /v2/edr-rules/{ruleUuid}:disable — Disable an EDR rule."""
        return self._request(
            "POST",
            f"/v2/edr-rules/{rule_uuid}:disable",
            json_body=body if body is not None else {},
        )

    def update_edr_rule_definition(
        self,
        rule_uuid: str,
        xml_definition: str | None = None,
        *,
        body: dict | None = None,
    ) -> dict:
        """POST /v2/edr-rules/{ruleUuid}:updateDefinition — Update the rule XML.

        Pass *xml_definition* (sent as ``{"xmlDefinition": ...}``) or a raw
        *body* dict.
        """
        payload = body if body is not None else {"xmlDefinition": xml_definition}
        return self._request(
            "POST",
            f"/v2/edr-rules/{rule_uuid}:updateDefinition",
            json_body=payload,
        )


    def list_edr_rule_exclusions(
        self, *, page_size: int | None = None, page_token: str | None = None
    ) -> dict:
        """GET /v2/edr-rule-exclusions — List EDR rule exclusions."""
        return self._request(
            "GET",
            "/v2/edr-rule-exclusions",
            params=self._page_params(page_size, page_token),
        )

    def create_edr_rule_exclusion(
        self, exclusion: dict | None = None, *, body: dict | None = None
    ) -> dict:
        """POST /v2/edr-rule-exclusions — Create an EDR rule exclusion.

        Pass *exclusion* (wrapped as ``{"exclusion": {...}}``) with keys like
        ``enabled``, ``note``, ``ruleUuids``, ``scopes``, ``xmlDefinition``; or a
        raw *body* dict.
        """
        payload = body if body is not None else {"exclusion": exclusion or {}}
        return self._request("POST", "/v2/edr-rule-exclusions", json_body=payload)

    def get_edr_rule_exclusion(self, exclusion_uuid: str) -> dict:
        """GET /v2/edr-rule-exclusions/{exclusionUuid} — Get an exclusion."""
        return self._request("GET", f"/v2/edr-rule-exclusions/{exclusion_uuid}")

    def delete_edr_rule_exclusion(self, exclusion_uuid: str) -> dict:
        """DELETE /v2/edr-rule-exclusions/{exclusionUuid} — Delete an exclusion."""
        return self._request("DELETE", f"/v2/edr-rule-exclusions/{exclusion_uuid}")

    def update_edr_rule_exclusion_definition(
        self,
        exclusion_uuid: str,
        xml_definition: str | None = None,
        *,
        body: dict | None = None,
    ) -> dict:
        """POST /v2/edr-rule-exclusions/{exclusionUuid}:updateDefinition —
        Update the exclusion XML.

        Pass *xml_definition* (sent as ``{"xmlDefinition": ...}``) or a raw
        *body* dict.
        """
        payload = body if body is not None else {"xmlDefinition": xml_definition}
        return self._request(
            "POST",
            f"/v2/edr-rule-exclusions/{exclusion_uuid}:updateDefinition",
            json_body=payload,
        )


    def iter_edr_rules(self, *, page_size: int | None = None) -> Iterator[dict]:
        """Yield every EDR rule, following ``nextPageToken`` pagination."""
        token: str | None = None
        while True:
            page = self.list_edr_rules(page_size=page_size, page_token=token)
            for rule in page.get("edrRules", []) or []:
                yield rule
            token = page.get("nextPageToken")
            if not token:
                break

    def iter_edr_rule_exclusions(
        self, *, page_size: int | None = None
    ) -> Iterator[dict]:
        """Yield every EDR rule exclusion, following ``nextPageToken``."""
        token: str | None = None
        while True:
            page = self.list_edr_rule_exclusions(page_size=page_size, page_token=token)
            for exclusion in page.get("edrRuleExclusions", []) or []:
                yield exclusion
            token = page.get("nextPageToken")
            if not token:
                break
