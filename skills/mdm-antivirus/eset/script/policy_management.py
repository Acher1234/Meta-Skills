#!/usr/bin/env python3
"""Policy Management v2 — https://help.eset.com/eset_connect/en-US/policy_management.html

GET    /v2/policies
POST   /v2/policies
GET    /v2/policies/{policyUuid}
DELETE /v2/policies/{policyUuid}
GET    /v2/policy-assignments
POST   /v2/policy-assignments
GET    /v2/policy-assignments/{assignmentUuid}
DELETE /v2/policy-assignments/{assignmentUuid}
POST   /v2/policy-assignments/{assignmentUuid}:updateRanking
"""

from __future__ import annotations

from typing import Iterator

from _client import ApiError, BaseClient


class PolicyManagementError(ApiError):
    label = "Policy Management API"


class PolicyManagementClient(BaseClient):
    error_class = PolicyManagementError

    def list_policies(
        self, *, page_size: int | None = None, page_token: str | None = None
    ) -> dict:
        return self._request(
            "GET", "/v2/policies", params=self._page_params(page_size, page_token)
        )

    def create_policy(self, body: dict) -> dict:
        return self._request("POST", "/v2/policies", json_body=body)

    def get_policy(self, policy_uuid: str) -> dict:
        return self._request("GET", f"/v2/policies/{policy_uuid}")

    def delete_policy(self, policy_uuid: str) -> dict:
        return self._request("DELETE", f"/v2/policies/{policy_uuid}")

    def list_policy_assignments(
        self, *, page_size: int | None = None, page_token: str | None = None
    ) -> dict:
        return self._request(
            "GET",
            "/v2/policy-assignments",
            params=self._page_params(page_size, page_token),
        )

    def assign_policy(self, body: dict) -> dict:
        return self._request("POST", "/v2/policy-assignments", json_body=body)

    def get_policy_assignment(self, assignment_uuid: str) -> dict:
        return self._request("GET", f"/v2/policy-assignments/{assignment_uuid}")

    def unassign_policy(self, assignment_uuid: str) -> dict:
        return self._request("DELETE", f"/v2/policy-assignments/{assignment_uuid}")

    def update_assignment_ranking(
        self,
        assignment_uuid: str,
        ranking: int | None = None,
        *,
        body: dict | None = None,
    ) -> dict:
        payload = body if body is not None else {"ranking": ranking}
        return self._request(
            "POST",
            f"/v2/policy-assignments/{assignment_uuid}:updateRanking",
            json_body=payload,
        )

    def iter_policies(self, *, page_size: int | None = None) -> Iterator[dict]:
        token: str | None = None
        while True:
            page = self.list_policies(page_size=page_size, page_token=token)
            for policy in page.get("policies", []) or []:
                yield policy
            token = page.get("nextPageToken")
            if not token:
                break

    def iter_policy_assignments(self, *, page_size: int | None = None) -> Iterator[dict]:
        token: str | None = None
        while True:
            page = self.list_policy_assignments(page_size=page_size, page_token=token)
            for assignment in page.get("policyAssignments", []) or []:
                yield assignment
            token = page.get("nextPageToken")
            if not token:
                break
