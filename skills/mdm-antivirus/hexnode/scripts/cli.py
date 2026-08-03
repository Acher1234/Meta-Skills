#!/usr/bin/env python3
"""Hexnode MDM CLI — Devices, Users, Apps, Policies, Device groups."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from application import ApplicationClient  # noqa: E402
from client import HexnodeError  # noqa: E402
from device_groups import DeviceGroupsClient  # noqa: E402
from devices import DevicesClient  # noqa: E402
from env_load import (  # noqa: E402
    ConfigError,
    base_url,
    display_skill_home,
    env_cred,
    load_env,
    require_api_key,
)
from policy import PolicyClient  # noqa: E402
from users import UsersClient  # noqa: E402


def _print(data: Any) -> None:
    print(json.dumps(data, indent=2, default=str))


def _load_json_file(path: str) -> Any:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return data


def _add_paging(p: argparse.ArgumentParser) -> None:
    p.add_argument("--page", type=int)
    p.add_argument("--per-page", type=int)


def cmd_env(_: argparse.Namespace) -> int:
    path = load_env()
    has_key = False
    api_base = None
    errors: list[str] = []
    try:
        require_api_key()
        has_key = True
    except ConfigError as exc:
        errors.append(str(exc))
    try:
        api_base = base_url()
    except ConfigError as exc:
        errors.append(str(exc))
    payload: dict[str, Any] = {
        "ok": bool(has_key and api_base),
        "env_path": str(path),
        "env_exists": path.is_file(),
        "library": display_skill_home(),
        "CURRENT_SKILL_DIRECTORY": str(env_cred().workspace),
        "has_api_key": has_key,
        "base_url": api_base,
    }
    if errors:
        payload["error"] = errors[0] if len(errors) == 1 else errors
    _print(payload)
    return 0 if payload["ok"] else 1


def cmd_devices(args: argparse.Namespace) -> int:
    client = DevicesClient()
    cmd = args.devices_cmd

    if cmd == "list":
        is_active = None
        if args.active:
            is_active = True
        elif args.inactive:
            is_active = False
        _print(
            client.list_devices(
                order_by=args.order_by,
                platform=args.platform,
                is_active=is_active,
                device_type=args.device_type,
                page=args.page,
                per_page=args.per_page,
            )
        )
        return 0
    if cmd == "get":
        _print(client.get_device(args.device_id))
        return 0
    if cmd == "policies":
        _print(
            client.list_device_policies(
                args.device_id, page=args.page, per_page=args.per_page
            )
        )
        return 0
    if cmd == "applications":
        _print(
            client.list_device_applications(
                args.device_id, page=args.page, per_page=args.per_page
            )
        )
        return 0
    if cmd == "locations":
        _print(
            client.list_device_locations(
                args.device_id, page=args.page, per_page=args.per_page
            )
        )
        return 0
    raise ConfigError(f"unknown devices command: {cmd}")


def cmd_users(args: argparse.Namespace) -> int:
    client = UsersClient()
    cmd = args.users_cmd

    if cmd == "list":
        _print(
            client.list_users(
                order_by=args.order_by,
                user_type=args.user_type,
                enrollment_status=args.enrollment_status,
                page=args.page,
                per_page=args.per_page,
            )
        )
        return 0
    if cmd == "create":
        _print(
            client.create_user(
                name=args.name,
                email=args.email,
                phoneno=args.phoneno,
                password=args.password,
            )
        )
        return 0
    if cmd == "get":
        _print(client.get_user(args.user_id))
        return 0
    if cmd == "edit":
        _print(
            client.edit_user(
                args.user_id,
                name=args.name,
                email=args.email,
                phoneno=args.phoneno,
                password=args.password,
            )
        )
        return 0
    if cmd == "delete":
        result = client.delete_user(args.user_id)
        _print(result if result is not None else {"ok": True, "status": 204})
        return 0
    if cmd == "send-enrollment":
        _print(
            client.send_enrollment_request(
                args.user_id, ownership=args.ownership
            )
        )
        return 0
    raise ConfigError(f"unknown users command: {cmd}")


def cmd_apps(args: argparse.Namespace) -> int:
    client = ApplicationClient()
    cmd = args.apps_cmd

    if cmd == "list":
        _print(
            client.list_apps(
                order_by=args.order_by,
                app_type=args.app_type,
                platform=args.platform,
                page=args.page,
                per_page=args.per_page,
            )
        )
        return 0
    if cmd == "search":
        _print(
            client.search_apps(
                keyword=args.keyword,
                platform=args.platform,
                country=args.country,
            )
        )
        return 0
    if cmd == "add":
        if args.file:
            body = _load_json_file(args.file)
        else:
            body = {
                "name": args.name,
                "app_type": args.app_type,
                "platform": args.platform,
                "category": args.category,
                "icon": args.icon,
            }
            optional = {
                "identifier": args.identifier,
                "version": args.version,
                "price": args.price,
                "vendor": args.vendor,
                "webapp_url": args.webapp_url,
                "appstore_id": args.appstore_id,
                "bundle_size": args.bundle_size,
                "description": args.description,
                "appstore_url": args.appstore_url,
                "average_user_rating": args.average_user_rating,
                "content_rating": args.content_rating,
            }
            for key, value in optional.items():
                if value is not None:
                    body[key] = value
            if args.remove_with_mdm is not None:
                body["remove_with_mdm"] = args.remove_with_mdm
            if args.prevent_backup is not None:
                body["prevent_backup"] = args.prevent_backup
            body = [body]
        result = client.add_app(body)
        _print(result if result is not None else {"ok": True, "status": 201})
        return 0
    if cmd == "get":
        _print(client.get_app(args.app_id))
        return 0
    raise ConfigError(f"unknown apps command: {cmd}")


def cmd_policies(args: argparse.Namespace) -> int:
    client = PolicyClient()
    cmd = args.policies_cmd

    if cmd == "list":
        _print(client.list_policies(page=args.page, per_page=args.per_page))
        return 0
    if cmd == "create":
        if args.file:
            body = _load_json_file(args.file)
            if not isinstance(body, dict):
                raise ConfigError("policies create --file must be a JSON object")
        else:
            if not args.name:
                raise ConfigError("policies create requires --name or --file")
            body = {"name": args.name, "description": args.description or ""}
        _print(client.create_policy(body))
        return 0
    if cmd == "get":
        _print(client.get_policy(args.policy_id))
        return 0
    if cmd == "edit":
        body = _load_json_file(args.file)
        if not isinstance(body, dict):
            raise ConfigError("policies edit --file must be a JSON object")
        _print(client.edit_policy(args.policy_id, body))
        return 0
    if cmd == "archive":
        result = client.archive_policy(args.policy_id)
        _print(result if result is not None else {"ok": True, "status": 204})
        return 0
    raise ConfigError(f"unknown policies command: {cmd}")


def _parse_id_list(values: list[str] | None) -> list[int]:
    out: list[int] = []
    for raw in values or []:
        for part in str(raw).split(","):
            part = part.strip()
            if part:
                out.append(int(part))
    return out


def cmd_device_groups(args: argparse.Namespace) -> int:
    client = DeviceGroupsClient()
    cmd = args.device_groups_cmd

    if cmd == "list":
        _print(
            client.list_device_groups(page=args.page, per_page=args.per_page)
        )
        return 0
    if cmd == "create":
        _print(
            client.create_device_group(
                groupname=args.name,
                description=args.description,
                devices=_parse_id_list(args.device) or None,
            )
        )
        return 0
    if cmd == "get":
        _print(client.get_device_group(args.group_id))
        return 0
    if cmd == "update":
        _print(
            client.update_device_group(
                args.group_id,
                groupname=args.name,
                description=args.description,
                devices=_parse_id_list(args.device) or None,
            )
        )
        return 0
    if cmd == "add-remove":
        add_ids = _parse_id_list(args.add)
        remove_ids = _parse_id_list(args.remove)
        if not add_ids and not remove_ids:
            raise ConfigError("add-remove requires --add and/or --remove")
        _print(
            client.add_remove_devices(
                args.group_id,
                add_devices=add_ids,
                remove_devices=remove_ids,
            )
        )
        return 0
    if cmd == "delete":
        result = client.delete_device_group(args.group_id)
        _print(result if result is not None else {"ok": True, "status": 204})
        return 0
    raise ConfigError(f"unknown device-groups command: {cmd}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cli.py",
        description=(
            "Hexnode MDM API CLI — Devices + Users + Apps + Policies + "
            "Device groups."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_env = sub.add_parser("env", help="Validate SkillCred .env (no network)")
    p_env.set_defaults(func=cmd_env)

    p_devices = sub.add_parser("devices", help="Devices API")
    devices_sub = p_devices.add_subparsers(dest="devices_cmd", required=True)
    p_devices.set_defaults(func=cmd_devices)

    d_list = devices_sub.add_parser(
        "list", help="GET /devices/ — list enrolled devices"
    )
    d_list.add_argument("--order-by", choices=["asc", "desc"])
    d_list.add_argument("--platform", choices=["ios", "android", "windows"])
    d_list.add_argument("--active", action="store_true", help="is_active=True")
    d_list.add_argument("--inactive", action="store_true", help="is_active=False")
    d_list.add_argument("--device-type", choices=["smartphone", "tablet"])
    _add_paging(d_list)

    d_get = devices_sub.add_parser(
        "get", help="GET /devices/{id}/ — device details"
    )
    d_get.add_argument("device_id", help="Hexnode device id")

    d_pol = devices_sub.add_parser(
        "policies", help="GET /devices/{id}/policies/"
    )
    d_pol.add_argument("device_id", help="Hexnode device id")
    _add_paging(d_pol)

    d_apps = devices_sub.add_parser(
        "applications", help="GET /devices/{id}/applications/"
    )
    d_apps.add_argument("device_id", help="Hexnode device id")
    _add_paging(d_apps)

    d_loc = devices_sub.add_parser(
        "locations", help="GET /devices/{id}/locations/"
    )
    d_loc.add_argument("device_id", help="Hexnode device id")
    _add_paging(d_loc)

    p_users = sub.add_parser("users", help="Users API")
    users_sub = p_users.add_subparsers(dest="users_cmd", required=True)
    p_users.set_defaults(func=cmd_users)

    u_list = users_sub.add_parser("list", help="GET /users/")
    u_list.add_argument("--order-by", choices=["asc", "desc"])
    u_list.add_argument("--user-type", choices=["local", "active directory"])
    u_list.add_argument(
        "--enrollment-status", choices=["enrolled", "unenrolled"]
    )
    _add_paging(u_list)

    u_create = users_sub.add_parser("create", help="POST /users/")
    u_create.add_argument("--name", required=True, help="Display name")
    u_create.add_argument("--email", required=True, help="Unique email")
    u_create.add_argument("--phoneno", help="Contact number")
    u_create.add_argument("--password", help="Optional password")

    u_get = users_sub.add_parser("get", help="GET /users/{id}/")
    u_get.add_argument("user_id", help="Hexnode user id")

    u_edit = users_sub.add_parser("edit", help="PUT /users/{id}/")
    u_edit.add_argument("user_id", help="Hexnode user id")
    u_edit.add_argument("--name", required=True, help="Display name")
    u_edit.add_argument("--email", required=True, help="Unique email")
    u_edit.add_argument("--phoneno", help="Contact number")
    u_edit.add_argument("--password", help="Optional password")

    u_del = users_sub.add_parser(
        "delete",
        help="DELETE /users/{id}/ (also disenrolls associated devices)",
    )
    u_del.add_argument("user_id", help="Hexnode user id")

    u_enroll = users_sub.add_parser(
        "send-enrollment", help="POST /users/{id}/send_request/"
    )
    u_enroll.add_argument("user_id", help="Hexnode user id")
    u_enroll.add_argument(
        "--ownership",
        required=True,
        choices=["personal", "corporate", "user_choice"],
        help="Device ownership for the enrollment request",
    )

    p_apps = sub.add_parser("apps", help="Applications API (portal catalog)")
    apps_sub = p_apps.add_subparsers(dest="apps_cmd", required=True)
    p_apps.set_defaults(func=cmd_apps)

    a_list = apps_sub.add_parser("list", help="GET /applications/")
    a_list.add_argument("--order-by", choices=["asc", "desc"])
    a_list.add_argument("--app-type", choices=["store", "web", "enterprise"])
    a_list.add_argument("--platform", choices=["ios", "android"])
    _add_paging(a_list)

    a_search = apps_sub.add_parser(
        "search", help="GET /applications/searchapp/"
    )
    a_search.add_argument("--keyword", required=True, help="App name to search")
    a_search.add_argument(
        "--platform", required=True, choices=["ios", "android"]
    )
    a_search.add_argument("--country", help="ISO alpha-2 country code (e.g. us)")

    a_add = apps_sub.add_parser(
        "add",
        help="POST /applications/ — add app to catalog (--file or flags)",
    )
    a_add.add_argument(
        "--file",
        metavar="JSON",
        help="Raw JSON body (object or list); overrides individual flags",
    )
    a_add.add_argument("--name", help="App display name (required without --file)")
    a_add.add_argument("--app-type", choices=["store", "web"])
    a_add.add_argument("--platform", choices=["ios", "android"])
    a_add.add_argument("--category", help="App category")
    a_add.add_argument("--icon", help="Icon URL or base64")
    a_add.add_argument("--identifier", help="Bundle / package id")
    a_add.add_argument("--version")
    a_add.add_argument("--price")
    a_add.add_argument("--vendor")
    a_add.add_argument("--webapp-url", dest="webapp_url")
    a_add.add_argument("--appstore-id", dest="appstore_id", type=int)
    a_add.add_argument("--bundle-size", dest="bundle_size", type=float)
    a_add.add_argument("--description")
    a_add.add_argument("--appstore-url", dest="appstore_url")
    a_add.add_argument("--average-user-rating", dest="average_user_rating")
    a_add.add_argument("--content-rating", dest="content_rating")
    a_add.add_argument(
        "--remove-with-mdm",
        dest="remove_with_mdm",
        action=argparse.BooleanOptionalAction,
        default=None,
    )
    a_add.add_argument(
        "--prevent-backup",
        dest="prevent_backup",
        action=argparse.BooleanOptionalAction,
        default=None,
    )

    a_get = apps_sub.add_parser("get", help="GET /applications/{id}/")
    a_get.add_argument("app_id", help="Hexnode application id")

    p_pol = sub.add_parser("policies", help="Policies API (portal policies)")
    pol_sub = p_pol.add_subparsers(dest="policies_cmd", required=True)
    p_pol.set_defaults(func=cmd_policies)

    p_list = pol_sub.add_parser("list", help="GET /policy/")
    _add_paging(p_list)

    p_create = pol_sub.add_parser(
        "create", help="POST /policy/ (--file JSON or --name)"
    )
    p_create.add_argument(
        "--file",
        metavar="JSON",
        help="Full policy body (name, ios/android/…, policy_targets, …)",
    )
    p_create.add_argument("--name", help="Policy name (simple create without --file)")
    p_create.add_argument("--description", default="", help="Policy description")

    p_get = pol_sub.add_parser("get", help="GET /policy/{id}/")
    p_get.add_argument("policy_id", help="Hexnode policy id")

    p_edit = pol_sub.add_parser("edit", help="PUT /policy/{id}/")
    p_edit.add_argument("policy_id", help="Hexnode policy id")
    p_edit.add_argument(
        "--file",
        required=True,
        metavar="JSON",
        help="Full policy body to PUT",
    )

    p_arch = pol_sub.add_parser(
        "archive",
        help="DELETE /policy/{id}/ — archive (dissociates from all devices)",
    )
    p_arch.add_argument("policy_id", help="Hexnode policy id")

    p_dg = sub.add_parser("device-groups", help="Device Groups API")
    dg_sub = p_dg.add_subparsers(dest="device_groups_cmd", required=True)
    p_dg.set_defaults(func=cmd_device_groups)

    dg_list = dg_sub.add_parser("list", help="GET /devicegroups/")
    _add_paging(dg_list)

    dg_create = dg_sub.add_parser("create", help="POST /devicegroups/")
    dg_create.add_argument("--name", required=True, help="groupname")
    dg_create.add_argument("--description", required=True, help="description")
    dg_create.add_argument(
        "--device",
        action="append",
        default=[],
        metavar="ID",
        help="Device id to include (repeatable or comma-separated)",
    )

    dg_get = dg_sub.add_parser("get", help="GET /devicegroups/{id}/")
    dg_get.add_argument("group_id", help="Device group id")

    dg_upd = dg_sub.add_parser("update", help="PUT /devicegroups/{id}/")
    dg_upd.add_argument("group_id", help="Device group id")
    dg_upd.add_argument("--name", required=True, help="groupname")
    dg_upd.add_argument("--description", required=True, help="description")
    dg_upd.add_argument(
        "--device",
        action="append",
        default=[],
        metavar="ID",
        help="Replace member device ids (repeatable or comma-separated)",
    )

    dg_ar = dg_sub.add_parser(
        "add-remove", help="POST /devicegroups/{id}/ — add/remove devices"
    )
    dg_ar.add_argument("group_id", help="Device group id")
    dg_ar.add_argument(
        "--add",
        action="append",
        default=[],
        metavar="ID",
        help="Device id(s) to add (repeatable or comma-separated)",
    )
    dg_ar.add_argument(
        "--remove",
        action="append",
        default=[],
        metavar="ID",
        help="Device id(s) to remove (repeatable or comma-separated)",
    )

    dg_del = dg_sub.add_parser("delete", help="DELETE /devicegroups/{id}/")
    dg_del.add_argument("group_id", help="Device group id")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "command", None) == "apps" and args.apps_cmd == "add":
        if not args.file:
            missing = [
                name
                for name, val in (
                    ("--name", args.name),
                    ("--app-type", args.app_type),
                    ("--platform", args.platform),
                    ("--category", args.category),
                    ("--icon", args.icon),
                )
                if not val
            ]
            if missing:
                parser.error(
                    "apps add requires --file JSON or flags: "
                    + ", ".join(missing)
                )
    try:
        return args.func(args)
    except ConfigError as exc:
        _print({"ok": False, "error": str(exc)})
        return 1
    except HexnodeError as exc:
        _print({"ok": False, "status": exc.status, "error": exc.body})
        return 1
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        _print({"ok": False, "error": str(exc)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
