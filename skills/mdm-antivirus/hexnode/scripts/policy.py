"""Hexnode Policies API — https://www.hexnode.com/mobile-device-management/developers/policies/

GET    /policy/                 list_policies
POST   /policy/                 create_policy
GET    /policy/{id}/            get_policy
PUT    /policy/{id}/            edit_policy
DELETE /policy/{id}/            archive_policy

Platform payload keys (ios / android / macos / windows) are documented at:
https://www.hexnode.com/mobile-device-management/developers/policies/ios-policies/
https://www.hexnode.com/mobile-device-management/developers/policies/android-policies/
https://www.hexnode.com/mobile-device-management/developers/policies/macos-policies/
https://www.hexnode.com/mobile-device-management/developers/policies/windows-policies/
"""

from __future__ import annotations

import argparse
from typing import Any

from client import ConfigError, HexnodeClient


class PolicyClient(HexnodeClient):
    def list_policies(
        self, *, page: int | None = None, per_page: int | None = None
    ) -> Any:
        """GET /policy/ — list all policies."""
        return self.request(
            "GET", "/policy/", params=self._page_params(page, per_page)
        )

    def create_policy(self, body: dict[str, Any]) -> Any:
        """POST /policy/ — create a policy (full JSON body)."""
        return self.request("POST", "/policy/", json=body)

    def get_policy(self, policy_id: int | str) -> Any:
        """GET /policy/{id}/ — policy details."""
        return self.request("GET", f"/policy/{policy_id}/")

    def edit_policy(self, policy_id: int | str, body: dict[str, Any]) -> Any:
        """PUT /policy/{id}/ — edit an existing policy."""
        return self.request("PUT", f"/policy/{policy_id}/", json=body)

    def archive_policy(self, policy_id: int | str) -> Any:
        """DELETE /policy/{id}/ — archive policy (dissociates from all devices)."""
        return self.request("DELETE", f"/policy/{policy_id}/")

    def cmd_list(self, args: argparse.Namespace) -> int:
        self.dump(self.list_policies(page=args.page, per_page=args.per_page))
        return 0

    def cmd_create(self, args: argparse.Namespace) -> int:
        if args.file:
            body = self.load_json_file(args.file)
            if not isinstance(body, dict):
                raise ConfigError("policies create --file must be a JSON object")
        else:
            if not args.name:
                raise ConfigError("policies create requires --name or --file")
            body = {"name": args.name, "description": args.description or ""}
        self.dump(self.create_policy(body))
        return 0

    def cmd_get(self, args: argparse.Namespace) -> int:
        self.dump(self.get_policy(args.policy_id))
        return 0

    def cmd_edit(self, args: argparse.Namespace) -> int:
        body = self.load_json_file(args.file)
        if not isinstance(body, dict):
            raise ConfigError("policies edit --file must be a JSON object")
        self.dump(self.edit_policy(args.policy_id, body))
        return 0

    def cmd_archive(self, args: argparse.Namespace) -> int:
        return self.dump_result(self.archive_policy(args.policy_id))

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = PolicyClient()
        p = sub.add_parser("policies", help="Policies API (portal policies)")
        cmds = p.add_subparsers(required=True)

        p_list = cmds.add_parser("list", help="GET /policy/")
        HexnodeClient.add_paging(p_list)
        p_list.set_defaults(func=client.cmd_list)

        p_create = cmds.add_parser(
            "create", help="POST /policy/ (--file JSON or --name)"
        )
        p_create.add_argument(
            "--file",
            metavar="JSON",
            help="Full policy body (name, ios/android/…, policy_targets, …)",
        )
        p_create.add_argument(
            "--name", help="Policy name (simple create without --file)"
        )
        p_create.add_argument("--description", default="", help="Policy description")
        p_create.set_defaults(func=client.cmd_create)

        p_get = cmds.add_parser("get", help="GET /policy/{id}/")
        p_get.add_argument("policy_id", help="Hexnode policy id")
        p_get.set_defaults(func=client.cmd_get)

        p_edit = cmds.add_parser("edit", help="PUT /policy/{id}/")
        p_edit.add_argument("policy_id", help="Hexnode policy id")
        p_edit.add_argument(
            "--file",
            required=True,
            metavar="JSON",
            help="Full policy body to PUT",
        )
        p_edit.set_defaults(func=client.cmd_edit)

        p_arch = cmds.add_parser(
            "archive",
            help="DELETE /policy/{id}/ — archive (dissociates from all devices)",
        )
        p_arch.add_argument("policy_id", help="Hexnode policy id")
        p_arch.set_defaults(func=client.cmd_archive)
