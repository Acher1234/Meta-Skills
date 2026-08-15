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

import argparse
from typing import Iterator

from _client import TOKEN_PARENT, ApiError, BaseClient


class EdrError(ApiError):
    """Raised when an EdrRules/EdrRuleExclusions API call fails."""

    label = "Incident Management API"


class EdrClient(BaseClient):
    """Client over the ESET Connect EdrRules + EdrRuleExclusions endpoints."""

    error_class = EdrError
    url_key = "incident_url"


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

    def cmd_rules_list(self, args: argparse.Namespace) -> None:
        self.dump(
            self.list_edr_rules(page_size=args.page_size, page_token=args.page_token)
        )
        return None

    def cmd_rules_create(self, args: argparse.Namespace) -> None:
        self.dump(self.create_edr_rule(body=self.load_json_file(args.file)))
        return None

    def cmd_rules_get(self, args: argparse.Namespace) -> None:
        self.dump(self.get_edr_rule(args.rule_uuid))
        return None

    def cmd_rules_delete(self, args: argparse.Namespace) -> None:
        self.dump(self.delete_edr_rule(args.rule_uuid))
        return None

    def cmd_rules_enable(self, args: argparse.Namespace) -> None:
        self.dump(self.enable_edr_rule(args.rule_uuid))
        return None

    def cmd_rules_disable(self, args: argparse.Namespace) -> None:
        self.dump(self.disable_edr_rule(args.rule_uuid))
        return None

    def cmd_rules_update_definition(self, args: argparse.Namespace) -> None:
        self.dump(
            self.update_edr_rule_definition(args.rule_uuid, args.xml_definition)
        )
        return None

    def cmd_exclusions_list(self, args: argparse.Namespace) -> None:
        self.dump(
            self.list_edr_rule_exclusions(
                page_size=args.page_size, page_token=args.page_token
            )
        )
        return None

    def cmd_exclusions_create(self, args: argparse.Namespace) -> None:
        self.dump(self.create_edr_rule_exclusion(body=self.load_json_file(args.file)))
        return None

    def cmd_exclusions_get(self, args: argparse.Namespace) -> None:
        self.dump(self.get_edr_rule_exclusion(args.exclusion_uuid))
        return None

    def cmd_exclusions_delete(self, args: argparse.Namespace) -> None:
        self.dump(self.delete_edr_rule_exclusion(args.exclusion_uuid))
        return None

    def cmd_exclusions_update_definition(self, args: argparse.Namespace) -> None:
        self.dump(
            self.update_edr_rule_exclusion_definition(
                args.exclusion_uuid, args.xml_definition
            )
        )
        return None

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = EdrClient()

        p_edr = sub.add_parser(
            "edr-rules",
            parents=[TOKEN_PARENT],
            help="Incident Management (EDR rules)",
        )
        edr = p_edr.add_subparsers(required=True)

        er_list = edr.add_parser("list", help="GET /v2/edr-rules")
        BaseClient.add_paging(er_list)
        er_list.set_defaults(func=client.cmd_rules_list)

        er_create = edr.add_parser("create", help="POST /v2/edr-rules")
        er_create.add_argument(
            "--file",
            required=True,
            help="JSON body (or '-' for stdin), e.g. {\"rule\": {...}}",
        )
        er_create.set_defaults(func=client.cmd_rules_create)

        er_get = edr.add_parser("get", help="GET /v2/edr-rules/{ruleUuid}")
        er_get.add_argument("rule_uuid", help="EDR rule UUID")
        er_get.set_defaults(func=client.cmd_rules_get)

        er_delete = edr.add_parser("delete", help="DELETE /v2/edr-rules/{ruleUuid}")
        er_delete.add_argument("rule_uuid", help="EDR rule UUID")
        er_delete.set_defaults(func=client.cmd_rules_delete)

        er_enable = edr.add_parser(
            "enable", help="POST /v2/edr-rules/{ruleUuid}:enable"
        )
        er_enable.add_argument("rule_uuid", help="EDR rule UUID")
        er_enable.set_defaults(func=client.cmd_rules_enable)

        er_disable = edr.add_parser(
            "disable", help="POST /v2/edr-rules/{ruleUuid}:disable"
        )
        er_disable.add_argument("rule_uuid", help="EDR rule UUID")
        er_disable.set_defaults(func=client.cmd_rules_disable)

        er_upd = edr.add_parser(
            "update-definition", help="POST /v2/edr-rules/{ruleUuid}:updateDefinition"
        )
        er_upd.add_argument("rule_uuid", help="EDR rule UUID")
        er_upd.add_argument(
            "--xml-definition", required=True, help="New XML rule definition"
        )
        er_upd.set_defaults(func=client.cmd_rules_update_definition)

        p_exc = sub.add_parser(
            "edr-exclusions",
            parents=[TOKEN_PARENT],
            help="Incident Management (EDR rule exclusions)",
        )
        exc = p_exc.add_subparsers(required=True)

        ex_list = exc.add_parser("list", help="GET /v2/edr-rule-exclusions")
        BaseClient.add_paging(ex_list)
        ex_list.set_defaults(func=client.cmd_exclusions_list)

        ex_create = exc.add_parser("create", help="POST /v2/edr-rule-exclusions")
        ex_create.add_argument(
            "--file",
            required=True,
            help="JSON body (or '-' for stdin), e.g. {\"exclusion\": {...}}",
        )
        ex_create.set_defaults(func=client.cmd_exclusions_create)

        ex_get = exc.add_parser(
            "get", help="GET /v2/edr-rule-exclusions/{exclusionUuid}"
        )
        ex_get.add_argument("exclusion_uuid", help="EDR rule exclusion UUID")
        ex_get.set_defaults(func=client.cmd_exclusions_get)

        ex_delete = exc.add_parser(
            "delete", help="DELETE /v2/edr-rule-exclusions/{exclusionUuid}"
        )
        ex_delete.add_argument("exclusion_uuid", help="EDR rule exclusion UUID")
        ex_delete.set_defaults(func=client.cmd_exclusions_delete)

        ex_upd = exc.add_parser(
            "update-definition",
            help="POST /v2/edr-rule-exclusions/{exclusionUuid}:updateDefinition",
        )
        ex_upd.add_argument("exclusion_uuid", help="EDR rule exclusion UUID")
        ex_upd.add_argument(
            "--xml-definition", required=True, help="New XML exclusion definition"
        )
        ex_upd.set_defaults(func=client.cmd_exclusions_update_definition)
