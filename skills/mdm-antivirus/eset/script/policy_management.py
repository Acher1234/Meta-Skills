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

import argparse
from typing import Iterator

from _client import TOKEN_PARENT, ApiError, BaseClient
from skill_env import ConfigError


class PolicyManagementError(ApiError):
    label = "Policy Management API"


class PolicyManagementClient(BaseClient):
    error_class = PolicyManagementError
    url_key = "policy_url"

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

    def cmd_list(self, args: argparse.Namespace) -> None:
        self.dump(
            self.list_policies(page_size=args.page_size, page_token=args.page_token)
        )
        return None

    def cmd_get(self, args: argparse.Namespace) -> None:
        self.dump(self.get_policy(args.policy_uuid))
        return None

    def cmd_create(self, args: argparse.Namespace) -> None:
        self.dump(self.create_policy(self.load_json_file(args.file)))
        return None

    def cmd_delete(self, args: argparse.Namespace) -> None:
        self.dump(self.delete_policy(args.policy_uuid))
        return None

    def cmd_assignments_list(self, args: argparse.Namespace) -> None:
        self.dump(
            self.list_policy_assignments(
                page_size=args.page_size, page_token=args.page_token
            )
        )
        return None

    def cmd_assignments_get(self, args: argparse.Namespace) -> None:
        self.dump(self.get_policy_assignment(args.assignment_uuid))
        return None

    def cmd_assign(self, args: argparse.Namespace) -> None:
        self.dump(self.assign_policy(self.load_json_file(args.file)))
        return None

    def cmd_unassign(self, args: argparse.Namespace) -> None:
        self.dump(self.unassign_policy(args.assignment_uuid))
        return None

    def cmd_update_ranking(self, args: argparse.Namespace) -> None:
        if args.file:
            self.dump(
                self.update_assignment_ranking(
                    args.assignment_uuid, body=self.load_json_file(args.file)
                )
            )
        elif args.ranking is not None:
            self.dump(
                self.update_assignment_ranking(args.assignment_uuid, args.ranking)
            )
        else:
            raise ConfigError("update-ranking requires --ranking N or --file body.json")
        return None

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = PolicyManagementClient()

        p_pol = sub.add_parser(
            "policies", parents=[TOKEN_PARENT], help="Policy Management (policies)"
        )
        pol = p_pol.add_subparsers(required=True)

        pl_list = pol.add_parser("list", help="GET /v2/policies")
        BaseClient.add_paging(pl_list)
        pl_list.set_defaults(func=client.cmd_list)

        pl_get = pol.add_parser("get", help="GET /v2/policies/{policyUuid}")
        pl_get.add_argument("policy_uuid", help="Policy UUID")
        pl_get.set_defaults(func=client.cmd_get)

        pl_create = pol.add_parser("create", help="POST /v2/policies")
        pl_create.add_argument(
            "--file", required=True, help="JSON file with the policy definition body"
        )
        pl_create.set_defaults(func=client.cmd_create)

        pl_delete = pol.add_parser("delete", help="DELETE /v2/policies/{policyUuid}")
        pl_delete.add_argument("policy_uuid", help="Policy UUID")
        pl_delete.set_defaults(func=client.cmd_delete)

        p_pa = sub.add_parser(
            "policy-assignments",
            parents=[TOKEN_PARENT],
            help="Policy Management (assignments)",
        )
        pa = p_pa.add_subparsers(required=True)

        pa_list = pa.add_parser("list", help="GET /v2/policy-assignments")
        BaseClient.add_paging(pa_list)
        pa_list.set_defaults(func=client.cmd_assignments_list)

        pa_get = pa.add_parser(
            "get", help="GET /v2/policy-assignments/{assignmentUuid}"
        )
        pa_get.add_argument("assignment_uuid", help="Policy assignment UUID")
        pa_get.set_defaults(func=client.cmd_assignments_get)

        pa_assign = pa.add_parser("assign", help="POST /v2/policy-assignments")
        pa_assign.add_argument(
            "--file", required=True, help="JSON file with the assignment body"
        )
        pa_assign.set_defaults(func=client.cmd_assign)

        pa_unassign = pa.add_parser(
            "unassign", help="DELETE /v2/policy-assignments/{assignmentUuid}"
        )
        pa_unassign.add_argument("assignment_uuid", help="Policy assignment UUID")
        pa_unassign.set_defaults(func=client.cmd_unassign)

        pa_rank = pa.add_parser(
            "update-ranking",
            help="POST /v2/policy-assignments/{assignmentUuid}:updateRanking",
        )
        pa_rank.add_argument("assignment_uuid", help="Policy assignment UUID")
        pa_rank.add_argument("--ranking", type=int, help="New ranking value")
        pa_rank.add_argument(
            "--file", help="JSON file with the ranking body (overrides --ranking)"
        )
        pa_rank.set_defaults(func=client.cmd_update_ranking)
