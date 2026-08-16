"""Hexnode Users API — https://www.hexnode.com/mobile-device-management/developers/users/

GET    /users/                              list_users
POST   /users/                              create_user
GET    /users/{id}/                         get_user
PUT    /users/{id}/                         edit_user
DELETE /users/{id}/                         delete_user
POST   /users/{id}/send_request/            send_enrollment_request
"""

from __future__ import annotations

import argparse
from typing import Any

from client import HexnodeClient


class UsersClient(HexnodeClient):
    def list_users(
        self,
        *,
        order_by: str | None = None,
        user_type: str | None = None,
        enrollment_status: str | None = None,
        page: int | None = None,
        per_page: int | None = None,
    ) -> Any:
        """GET /users/ — list enrolled users."""
        return self.request(
            "GET",
            "/users/",
            params={
                "order_by": order_by,
                "user_type": user_type,
                "enrollment_status": enrollment_status,
                **self._page_params(page, per_page),
            },
        )

    def create_user(
        self,
        *,
        name: str,
        email: str,
        phoneno: str | int | None = None,
        password: str | None = None,
    ) -> Any:
        """POST /users/ — create a user (API expects a one-element list body)."""
        user: dict[str, Any] = {"name": name, "email": email}
        if phoneno is not None:
            user["phoneno"] = phoneno
        if password is not None:
            user["password"] = password
        return self.request("POST", "/users/", json=[user])

    def get_user(self, user_id: int | str) -> Any:
        """GET /users/{id}/ — retrieve user details."""
        return self.request("GET", f"/users/{user_id}/")

    def edit_user(
        self,
        user_id: int | str,
        *,
        name: str,
        email: str,
        phoneno: str | int | None = None,
        password: str | None = None,
    ) -> Any:
        """PUT /users/{id}/ — edit user details."""
        body: dict[str, Any] = {"name": name, "email": email}
        if phoneno is not None:
            body["phoneno"] = phoneno
        if password is not None:
            body["password"] = password
        return self.request("PUT", f"/users/{user_id}/", json=body)

    def delete_user(self, user_id: int | str) -> Any:
        """DELETE /users/{id}/ — deletes user and disenrolls their devices."""
        return self.request("DELETE", f"/users/{user_id}/")

    def send_enrollment_request(
        self, user_id: int | str, *, ownership: str
    ) -> Any:
        """POST /users/{id}/send_request/ — send enrollment request."""
        return self.request(
            "POST",
            f"/users/{user_id}/send_request/",
            json={"ownership": ownership},
        )

    def cmd_list(self, args: argparse.Namespace) -> int:
        self.dump(
            self.list_users(
                order_by=args.order_by,
                user_type=args.user_type,
                enrollment_status=args.enrollment_status,
                page=args.page,
                per_page=args.per_page,
            )
        )
        return 0

    def cmd_create(self, args: argparse.Namespace) -> int:
        self.dump(
            self.create_user(
                name=args.name,
                email=args.email,
                phoneno=args.phoneno,
                password=args.password,
            )
        )
        return 0

    def cmd_get(self, args: argparse.Namespace) -> int:
        self.dump(self.get_user(args.user_id))
        return 0

    def cmd_edit(self, args: argparse.Namespace) -> int:
        self.dump(
            self.edit_user(
                args.user_id,
                name=args.name,
                email=args.email,
                phoneno=args.phoneno,
                password=args.password,
            )
        )
        return 0

    def cmd_delete(self, args: argparse.Namespace) -> int:
        return self.dump_result(self.delete_user(args.user_id))

    def cmd_send_enrollment(self, args: argparse.Namespace) -> int:
        self.dump(
            self.send_enrollment_request(args.user_id, ownership=args.ownership)
        )
        return 0

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = UsersClient()
        p = sub.add_parser("users", help="Users API")
        cmds = p.add_subparsers(required=True)

        u_list = cmds.add_parser("list", help="GET /users/")
        u_list.add_argument("--order-by", choices=["asc", "desc"])
        u_list.add_argument("--user-type", choices=["local", "active directory"])
        u_list.add_argument(
            "--enrollment-status", choices=["enrolled", "unenrolled"]
        )
        HexnodeClient.add_paging(u_list)
        u_list.set_defaults(func=client.cmd_list)

        u_create = cmds.add_parser("create", help="POST /users/")
        u_create.add_argument("--name", required=True, help="Display name")
        u_create.add_argument("--email", required=True, help="Unique email")
        u_create.add_argument("--phoneno", help="Contact number")
        u_create.add_argument("--password", help="Optional password")
        u_create.set_defaults(func=client.cmd_create)

        u_get = cmds.add_parser("get", help="GET /users/{id}/")
        u_get.add_argument("user_id", help="Hexnode user id")
        u_get.set_defaults(func=client.cmd_get)

        u_edit = cmds.add_parser("edit", help="PUT /users/{id}/")
        u_edit.add_argument("user_id", help="Hexnode user id")
        u_edit.add_argument("--name", required=True, help="Display name")
        u_edit.add_argument("--email", required=True, help="Unique email")
        u_edit.add_argument("--phoneno", help="Contact number")
        u_edit.add_argument("--password", help="Optional password")
        u_edit.set_defaults(func=client.cmd_edit)

        u_del = cmds.add_parser(
            "delete",
            help="DELETE /users/{id}/ (also disenrolls associated devices)",
        )
        u_del.add_argument("user_id", help="Hexnode user id")
        u_del.set_defaults(func=client.cmd_delete)

        u_enroll = cmds.add_parser(
            "send-enrollment", help="POST /users/{id}/send_request/"
        )
        u_enroll.add_argument("user_id", help="Hexnode user id")
        u_enroll.add_argument(
            "--ownership",
            required=True,
            choices=["personal", "corporate", "user_choice"],
            help="Device ownership for the enrollment request",
        )
        u_enroll.set_defaults(func=client.cmd_send_enrollment)
