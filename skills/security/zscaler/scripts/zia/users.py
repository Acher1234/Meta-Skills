"""ZIA user management — list users, groups, and departments."""

from __future__ import annotations

import argparse
from typing import Any

from zia.client import ZiaClient


class UsersClient(ZiaClient):
    def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> list[dict[str, Any]]:
        with self.get_client() as client:
            users, _, err = client.zia.user_management.list_users(
                query_params={"page": page, "pageSize": page_size}
            )
            if err:
                raise RuntimeError(f"Failed to list ZIA users: {err}")
            return self.records(users)

    def list_groups(
        self,
        page: int = 1,
        page_size: int = 100,
    ) -> list[dict[str, Any]]:
        with self.get_client() as client:
            groups, _, err = client.zia.user_management.list_groups(
                query_params={"page": page, "page_size": page_size}
            )
            if err:
                raise RuntimeError(f"Failed to list ZIA groups: {err}")
            return self.records(groups)

    def list_departments(
        self,
        page: int = 1,
        page_size: int = 100,
        search: str | None = None,
    ) -> list[dict[str, Any]]:
        query_params: dict[str, Any] = {"page": page, "page_size": page_size}
        if search:
            query_params["search"] = search

        with self.get_client() as client:
            departments, _, err = client.zia.user_management.list_departments(
                query_params=query_params
            )
            if err:
                raise RuntimeError(f"Failed to list ZIA departments: {err}")
            return self.records(departments)

    def list_all_users(self) -> list[dict[str, Any]]:
        page = 1
        out: list[dict[str, Any]] = []
        while True:
            chunk = self.list_users(page=page, page_size=100)
            out.extend(chunk)
            if len(chunk) < 100:
                break
            page += 1
        return out

    def resolve_user_ids(
        self,
        *,
        user_ids: list[int | str] | None = None,
        usernames: list[str] | None = None
    ) -> list:
        users = self.list_all_users()
        by_id = {str(u.get("id")): u for u in users}
        by_name: dict[str, dict[str, Any]] = {}
        for user in users:
            for key in ("name", "userName", "email"):
                value = str(user.get(key) or "").casefold()
                if value:
                    by_name.setdefault(value, user)
        out: list = []
        for uid in user_ids or []:
            key = str(uid).strip()
            if key not in by_id:
                raise RuntimeError(f"ZIA user not found: {uid}")
            out.append(by_id[key]["id"])
        for name in usernames or []:
            needle = name.strip().casefold()
            if needle not in by_name:
                raise RuntimeError(f"ZIA user not found: {name!r}")
            out.append(by_name[needle]["id"])
        return out

    def list_all_groups(self) -> list[dict[str, Any]]:
        page = 1
        out: list[dict[str, Any]] = []
        while True:
            chunk = self.list_groups(page=page, page_size=100)
            out.extend(chunk)
            if len(chunk) < 100:
                break
            page += 1
        return out

    def resolve_group_ids(
        self,
        *,
        group_ids: list[int | str] | None = None,
        group_names: list[str] | None = None
    ) -> list[dict[str, Any]]:
        groups = self.list_all_groups()
        by_id = {str(g.get("id")): g for g in groups}
        by_name = {str(g.get("name") or "").casefold(): g for g in groups}
        out: list[dict[str, Any]] = []
        for gid in group_ids or []:
            key = str(gid).strip()
            if key not in by_id:
                raise RuntimeError(f"ZIA group not found: {gid}")
            out.append(by_id[key])
        for name in group_names or []:
            needle = name.strip().casefold()
            if needle not in by_name:
                raise RuntimeError(f"ZIA group not found: {name!r}")
            out.append(by_name[needle])
        return out

    def cmd_list(self, args: argparse.Namespace) -> None:
        self.dump(
            self.list_users(
                page=args.page,
                page_size=args.page_size
            )
        )
        return None

    def cmd_groups(self, args: argparse.Namespace) -> None:
        self.dump(
            self.list_groups(
                page=args.page,
                page_size=args.page_size
            )
        )
        return None

    def cmd_departments(self, args: argparse.Namespace) -> None:
        self.dump(
            self.list_departments(
                page=args.page,
                page_size=args.page_size,
                search=args.search or None
            )
        )
        return None

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = UsersClient()
        p = sub.add_parser("users", help="ZIA users, groups, departments")
        cmds = p.add_subparsers(required=True)

        u_list = cmds.add_parser("list", help="List ZIA users")
        u_list.add_argument("--page", type=int, default=1)
        u_list.add_argument("--page-size", type=int, default=20)
        u_list.set_defaults(func=client.cmd_list)

        u_groups = cmds.add_parser(
            "groups", help="List ZIA user groups"
        )
        u_groups.add_argument("--page", type=int, default=1)
        u_groups.add_argument("--page-size", type=int, default=100)
        u_groups.set_defaults(func=client.cmd_groups)

        u_dept = cmds.add_parser(
            "departments", help="List ZIA departments"
        )
        u_dept.add_argument("--page", type=int, default=1)
        u_dept.add_argument("--page-size", type=int, default=100)
        u_dept.add_argument("--search", default="", help="Optional name search")
        u_dept.set_defaults(func=client.cmd_departments)
