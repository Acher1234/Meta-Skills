"""Minimal GoDaddy Domains v3 HTTP client (Bearer PAT)."""

from __future__ import annotations

import uuid
from typing import Any

import requests

from env_load import base_url, require_pat


class GoDaddyError(RuntimeError):
    def __init__(self, status: int, body: Any):
        self.status = status
        self.body = body
        super().__init__(f"GoDaddy API {status}: {body}")


class GoDaddyClient:
    def __init__(self, pat: str | None = None, api_base: str | None = None):
        self.pat = pat or require_pat()
        self.api_base = (api_base or base_url()).rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.pat}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        request_id: str | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Any:
        headers = {"X-Request-Id": request_id or str(uuid.uuid4())}
        if extra_headers:
            headers.update(extra_headers)
        url = f"{self.api_base}{path}"
        if params:
            clean: dict[str, Any] = {}
            for key, value in params.items():
                if value is None or value == "":
                    continue
                clean[key] = value
            params = clean
        resp = self.session.request(
            method, url, params=params, json=json, headers=headers, timeout=60
        )
        if resp.status_code == 204:
            return None
        try:
            body: Any = resp.json() if resp.content else None
        except ValueError:
            body = resp.text
        if resp.status_code >= 400:
            raise GoDaddyError(resp.status_code, body)
        return body

    # Discovery — https://developer.godaddy.com/en/docs/references/rest/domains/v3/discovery

    def suggest(
        self,
        *,
        query: str | None = None,
        tlds: list[str] | None = None,
        length_min: int | None = None,
        length_max: int | None = None,
        page_size: int | None = None,
        sources: list[str] | None = None,
    ) -> Any:
        params: dict[str, Any] = {
            "query": query,
            "lengthMin": length_min,
            "lengthMax": length_max,
            "pageSize": page_size,
        }
        if tlds:
            params["tlds"] = ",".join(tlds)
        if sources:
            params["sources"] = ",".join(sources)
        return self.request("GET", "/v3/domains/suggestions", params=params)

    def check_availability(
        self,
        domain: str,
        *,
        optimize_for: str | None = None,
        isc_code: str | None = None,
    ) -> Any:
        return self.request(
            "GET",
            "/v3/domains/check-availability",
            params={
                "domain": domain,
                "optimizeFor": optimize_for,
                "iscCode": isc_code,
            },
        )

    # Domains v1 — https://developer.godaddy.com/en/docs/references/rest/domains/v1/manage-domain-settings

    def list_domains(
        self,
        *,
        statuses: list[str] | None = None,
        status_groups: list[str] | None = None,
        limit: int | None = None,
        marker: str | None = None,
        includes: list[str] | None = None,
        modified_date: str | None = None,
        shopper_id: str | None = None,
    ) -> Any:
        """GET /v1/domains — paginated list of domains for the authenticated shopper."""
        params: dict[str, Any] = {
            "limit": limit,
            "marker": marker,
            "modifiedDate": modified_date,
        }
        if statuses:
            params["statuses"] = statuses
        if status_groups:
            params["statusGroups"] = status_groups
        if includes:
            params["includes"] = includes
        headers = {"X-Shopper-Id": shopper_id} if shopper_id else None
        return self.request(
            "GET", "/v1/domains", params=params, extra_headers=headers
        )

    # Domains v3 — https://developer.godaddy.com/en/docs/references/rest/domains/v3/domains

    def get_domain(self, domain_name: str) -> Any:
        """GET /v3/domains/domain-names/{domain-name} — owned domain management view."""
        return self.request("GET", f"/v3/domains/domain-names/{domain_name}")

    # DNS — https://developer.godaddy.com/en/docs/references/rest/domains/v3/records

    def dns_list(
        self,
        zone: str,
        *,
        record_type: str | None = None,
        name: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        total_required: bool | None = None,
    ) -> Any:
        return self.request(
            "GET",
            f"/v3/domains/zones/{zone}/dns-records",
            params={
                "type": record_type,
                "name": name,
                "page": page,
                "pageSize": page_size,
                "totalRequired": total_required,
            },
        )

    def dns_add(self, zone: str, record: dict[str, Any]) -> Any:
        return self.request(
            "POST", f"/v3/domains/zones/{zone}/dns-records", json=record
        )

    def dns_delete(self, zone: str, record_id: str) -> Any:
        return self.request(
            "DELETE", f"/v3/domains/zones/{zone}/dns-records/{record_id}"
        )
