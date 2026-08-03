#!/usr/bin/env python3
"""ESET Connect CLI — OAuth + Device / App / Asset / Policy / Incident / Automation APIs."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import requests

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import application_management as am  # noqa: E402
import asset_management as asm  # noqa: E402
import authentication as auth  # noqa: E402
import automation as autom  # noqa: E402
import device_management as dm  # noqa: E402
import incident_detections as idet  # noqa: E402
import incident_edr as iedr  # noqa: E402
import incident_incidents as iinc  # noqa: E402
import policy_management as pm  # noqa: E402
from _client import ApiError  # noqa: E402
from env_load import (  # noqa: E402
    display_env_path,
    display_skill_home,
    env_path,
    load_env,
)

KNOWN_REGIONS = {
    "eu": "https://eu.business-account.iam.eset.systems",
    "de": "https://de.business-account.iam.eset.systems",
    "us": "https://us.business-account.iam.eset.systems",
    "ca": "https://ca.business-account.iam.eset.systems",
    "jpn": "https://jpn.business-account.iam.eset.systems",
}


class ConfigError(Exception):
    pass


def normalize_base_url(raw: str) -> str:
    if not raw:
        raise ConfigError("ESET_URL is not set")
    value = raw.strip()
    if value.lower() in KNOWN_REGIONS:
        return KNOWN_REGIONS[value.lower()]
    value = value.rstrip("/")
    if value.endswith(auth.TOKEN_PATH):
        value = value[: -len(auth.TOKEN_PATH)].rstrip("/")
    return value


def _region_from_base(base_url: str) -> str:
    host = base_url.split("://", 1)[-1]
    return host.split(".", 1)[0] if host else ""


def _service_url(base_url: str, service_host: str, override_env: str) -> str:
    override = os.getenv(override_env, "").strip()
    if override:
        return override.rstrip("/")
    region = _region_from_base(base_url)
    if not region:
        raise ConfigError(f"Cannot resolve {service_host} URL; set {override_env}")
    return f"https://{region}.{service_host}.eset.systems"


def resolve_api_url(base_url: str) -> str:
    return _service_url(base_url, "automation", "ESET_API_URL")


def resolve_automation_url(base_url: str) -> str:
    return _service_url(base_url, "automation", "ESET_AUTOMATION_URL")


def resolve_app_url(base_url: str) -> str:
    return _service_url(base_url, "application-management", "ESET_APP_URL")


def resolve_asset_url(base_url: str) -> str:
    return _service_url(base_url, "automation", "ESET_ASSET_URL")


def resolve_policy_url(base_url: str) -> str:
    return _service_url(base_url, "automation", "ESET_POLICY_URL")


def resolve_incident_url(base_url: str) -> str:
    return _service_url(base_url, "incident-management", "ESET_INCIDENT_URL")


def load_config(require_credentials: bool = True) -> dict:
    load_env()
    base = normalize_base_url(os.getenv("ESET_URL", ""))
    username = os.getenv("ESET_USERNAME", "").strip()
    password = os.getenv("ESET_PASSWORD", "")

    required = [("ESET_URL", base)]
    if require_credentials:
        required += [("ESET_USERNAME", username), ("ESET_PASSWORD", password)]
    missing = [name for name, val in required if not val]
    if missing:
        raise ConfigError(
            f"Missing in {display_env_path()}: {', '.join(missing)}. "
            f"Copy .env.example there and fill it in."
        )

    return {
        "base_url": base,
        "token_url": auth.token_url(base),
        "api_url": resolve_api_url(base),
        "automation_url": resolve_automation_url(base),
        "app_url": resolve_app_url(base),
        "asset_url": resolve_asset_url(base),
        "policy_url": resolve_policy_url(base),
        "incident_url": resolve_incident_url(base),
        "username": username,
        "password": password,
        "env_path": str(env_path()),
    }


def _resolve_token(args: argparse.Namespace, cfg: dict) -> str:
    """Reuse ESET_ACCESS_TOKEN from `.env`, else refresh / password grant and save."""
    try:
        result = auth.ensure_access_token(
            cfg["token_url"],
            username=cfg.get("username"),
            password=cfg.get("password"),
            access_token=getattr(args, "token", None),
            refresh_token=os.getenv("ESET_REFRESH_TOKEN", "").strip() or None,
            force=bool(getattr(args, "force_token", False)),
        )
    except auth.AuthError as exc:
        raise ConfigError(str(exc)) from exc
    return result["access_token"]


def _client(args: argparse.Namespace) -> "dm.DeviceManagementClient":
    cfg = load_config(require_credentials=False)
    return dm.DeviceManagementClient(cfg["api_url"], _resolve_token(args, cfg))


def _app_client(args: argparse.Namespace) -> "am.ApplicationManagementClient":
    cfg = load_config(require_credentials=False)
    return am.ApplicationManagementClient(cfg["app_url"], _resolve_token(args, cfg))


def _automation_client(args: argparse.Namespace) -> "autom.AutomationClient":
    cfg = load_config(require_credentials=False)
    return autom.AutomationClient(cfg["automation_url"], _resolve_token(args, cfg))


def _asset_client(args: argparse.Namespace) -> "asm.AssetManagementClient":
    cfg = load_config(require_credentials=False)
    return asm.AssetManagementClient(cfg["asset_url"], _resolve_token(args, cfg))


def _policy_client(args: argparse.Namespace) -> "pm.PolicyManagementClient":
    cfg = load_config(require_credentials=False)
    return pm.PolicyManagementClient(cfg["policy_url"], _resolve_token(args, cfg))


def _detections_client(args: argparse.Namespace) -> "idet.DetectionsClient":
    cfg = load_config(require_credentials=False)
    return idet.DetectionsClient(cfg["incident_url"], _resolve_token(args, cfg))


def _edr_client(args: argparse.Namespace) -> "iedr.EdrClient":
    cfg = load_config(require_credentials=False)
    return iedr.EdrClient(cfg["incident_url"], _resolve_token(args, cfg))


def _incidents_client(args: argparse.Namespace) -> "iinc.IncidentsClient":
    cfg = load_config(require_credentials=False)
    return iinc.IncidentsClient(cfg["incident_url"], _resolve_token(args, cfg))


def _print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, default=str))


def cmd_env_check(args: argparse.Namespace) -> int:
    try:
        cfg = load_config()
    except ConfigError as exc:
        _print_json(
            {
                "ok": False,
                "env": str(env_path()),
                "library": display_skill_home(),
                "error": str(exc),
            }
        )
        return 1
    _print_json(
        {
            "ok": True,
            "env": str(env_path()),
            "library": display_skill_home(),
            "base_url": cfg["base_url"],
            "token_url": cfg["token_url"],
            "api_url": cfg["api_url"],
            "automation_url": cfg["automation_url"],
            "app_url": cfg["app_url"],
            "asset_url": cfg["asset_url"],
            "policy_url": cfg["policy_url"],
            "incident_url": cfg["incident_url"],
            "username": cfg["username"],
            "has_access_token": bool(os.getenv("ESET_ACCESS_TOKEN", "").strip()),
            "has_refresh_token": bool(os.getenv("ESET_REFRESH_TOKEN", "").strip()),
        }
    )
    return 0


def cmd_token(args: argparse.Namespace) -> int:
    cfg = load_config()

    if args.print_request:
        req = auth.build_request(
            cfg["token_url"],
            username=cfg["username"],
            password=cfg["password"],
            refresh_token=args.refresh,
        )
        _print_json(
            {
                "method": req["method"],
                "url": req["url"],
                "headers": req["headers"],
                "body": auth.redact(req["data"]),
            }
        )
        return 0

    try:
        result = auth.ensure_access_token(
            cfg["token_url"],
            username=cfg["username"],
            password=cfg["password"],
            refresh_token=args.refresh or os.getenv("ESET_REFRESH_TOKEN", "").strip() or None,
            force=True,
        )
    except auth.AuthError as exc:
        _print_json({"ok": False, "error": str(exc)})
        return 1

    if args.token_only and result.get("ok"):
        print(result["access_token"])
        return 0

    safe = {
        k: v
        for k, v in result.items()
        if k not in ("access_token", "refresh_token")
    }
    safe["access_token"] = "***"
    if result.get("refresh_token"):
        safe["refresh_token"] = "***"
    safe["saved_to"] = str(env_path())
    _print_json(safe)
    return 0 if result.get("ok") else 1


def cmd_groups(args: argparse.Namespace) -> int:
    """Device group endpoints."""
    client = _client(args)
    if args.groups_cmd == "list":
        _print_json(client.list_device_groups(page_size=args.page_size, page_token=args.page_token))
    elif args.groups_cmd == "devices":
        _print_json(
            client.list_devices_in_group(
                args.group_uuid, page_size=args.page_size, page_token=args.page_token
            )
        )
    return 0


def cmd_devices(args: argparse.Namespace) -> int:
    """Device endpoints."""
    client = _client(args)
    cmd = args.devices_cmd
    if cmd == "list":
        _print_json(client.list_devices(page_size=args.page_size, page_token=args.page_token))
    elif cmd == "get":
        _print_json(client.get_device(args.device_uuid))
    elif cmd == "move":
        _print_json(client.move_device(args.device_uuid, args.group))
    elif cmd == "rename":
        _print_json(client.rename_device(args.device_uuid, args.name))
    elif cmd == "batch-get":
        _print_json(client.batch_get_devices(args.device_uuids))
    elif cmd == "batch-import":
        data = json.loads(Path(args.file).read_text())
        _print_json(client.batch_import_devices(data))
    return 0


def cmd_assets(args: argparse.Namespace) -> int:
    """Asset Management — group endpoints."""
    client = _asset_client(args)
    cmd = args.assets_cmd
    if cmd == "create":
        _print_json(client.create_group(args.name, args.parent))
    elif cmd == "delete":
        _print_json(client.delete_group(args.group_uuid))
    elif cmd == "move":
        _print_json(client.move_group(args.group_uuid, args.parent))
    elif cmd == "rename":
        _print_json(client.rename_group(args.group_uuid, args.name))
    return 0


def cmd_policies(args: argparse.Namespace) -> int:
    """Policy Management — policy endpoints."""
    client = _policy_client(args)
    cmd = args.policies_cmd
    if cmd == "list":
        _print_json(client.list_policies(page_size=args.page_size, page_token=args.page_token))
    elif cmd == "get":
        _print_json(client.get_policy(args.policy_uuid))
    elif cmd == "create":
        body = json.loads(Path(args.file).read_text())
        _print_json(client.create_policy(body))
    elif cmd == "delete":
        _print_json(client.delete_policy(args.policy_uuid))
    return 0


def cmd_policy_assignments(args: argparse.Namespace) -> int:
    """Policy Management — policy assignment endpoints."""
    client = _policy_client(args)
    cmd = args.assignments_cmd
    if cmd == "list":
        _print_json(
            client.list_policy_assignments(page_size=args.page_size, page_token=args.page_token)
        )
    elif cmd == "get":
        _print_json(client.get_policy_assignment(args.assignment_uuid))
    elif cmd == "assign":
        body = json.loads(Path(args.file).read_text())
        _print_json(client.assign_policy(body))
    elif cmd == "unassign":
        _print_json(client.unassign_policy(args.assignment_uuid))
    elif cmd == "update-ranking":
        if args.file:
            body = json.loads(Path(args.file).read_text())
            _print_json(client.update_assignment_ranking(args.assignment_uuid, body=body))
        elif args.ranking is not None:
            _print_json(client.update_assignment_ranking(args.assignment_uuid, args.ranking))
        else:
            raise ConfigError("update-ranking requires --ranking N or --file body.json")
    return 0


def cmd_executables(args: argparse.Namespace) -> int:
    """Application Management — executable endpoints."""
    client = _app_client(args)
    cmd = args.executables_cmd
    if cmd == "list":
        _print_json(
            client.list_executables(page_size=args.page_size, page_token=args.page_token)
        )
    elif cmd == "get":
        _print_json(client.get_executable(args.executable_uuid))
    elif cmd == "block":
        _print_json(client.block_executable(args.executable_uuid))
    elif cmd == "unblock":
        _print_json(client.unblock_executable(args.executable_uuid))
    return 0


def _task_common(args: argparse.Namespace) -> dict:
    """Collect the shared build_task keyword args from parsed CLI options."""
    return {
        "targets": autom.build_targets(devices=args.device, groups=args.group),
        "display_name": args.display_name,
        "description": args.description,
        "expire_time": args.expire_time,
    }


def cmd_tasks(args: argparse.Namespace) -> int:
    """Automation — Device task endpoints and task builders."""
    client = _automation_client(args)
    cmd = args.tasks_cmd

    if cmd == "list":
        _print_json(client.list_tasks(page_size=args.page_size, page_token=args.page_token))
        return 0
    if cmd == "get":
        _print_json(client.get_task(args.task_uuid))
        return 0
    if cmd == "delete":
        _print_json(client.delete_task(args.task_uuid))
        return 0
    if cmd == "runs":
        _print_json(
            client.list_task_runs(
                args.task_uuid, page_size=args.page_size, page_token=args.page_token
            )
        )
        return 0
    if cmd == "update-targets":
        if args.file:
            _print_json(client.update_task_targets(args.task_uuid, body=_load_body(args.file)))
        else:
            targets = autom.build_targets(devices=args.device, groups=args.group)
            _print_json(client.update_task_targets(args.task_uuid, targets))
        return 0
    if cmd == "update-triggers":
        if args.file:
            _print_json(client.update_task_triggers(args.task_uuid, body=_load_body(args.file)))
        else:
            triggers = [autom.build_manual_trigger(args.expire_time)]
            _print_json(client.update_task_triggers(args.task_uuid, triggers))
        return 0

    # ---- task creation (generic + per-action builders) -----------------
    if cmd == "create":
        if args.file:
            _print_json(client.create_task(_load_body(args.file)))
            return 0
        if not args.action:
            raise ConfigError("create requires --action NAME (or --file body.json)")
        params = _load_body(args.params_file) if args.params_file else None
        body = autom.build_task(args.action, params=params, **_task_common(args))
        _print_json(client.create_task(body))
        return 0

    # Convenience builders map to a specific action.name.
    builders = {
        "isolate": ("StartNetworkIsolation", None),
        "end-isolation": ("EndNetworkIsolation", None),
        "stop-managing": ("StopManaging", None),
        "av-remove": ("ThirdPartyAVRemove", None),
        "logout": ("LogOffComputerUser", None),
        "vulnerability-scan": (
            "InitiateVulnerabilityScan",
            lambda a: autom.build_vulnerability_scan_params(),
        ),
        "scan": (
            "OnDemandScan",
            lambda a: autom.build_scan_params(
                scan_profile=a.scan_profile,
                custom_profile_name=a.custom_profile or "",
                scan_targets=a.scan_target or None,
                cleaning_enabled=a.cleaning,
                shutdown_enabled=a.shutdown,
                postpone=a.postpone,
            ),
        ),
        "shutdown": (
            "ShutdownComputer",
            lambda a: autom.build_shutdown_params(restart=a.restart, postpone=a.postpone),
        ),
        "os-update": (
            "SystemUpdate",
            lambda a: autom.build_system_update_params(
                accept_eula=a.accept_eula,
                install_optional_updates=a.optional_updates,
                allow_reboot=a.allow_reboot,
                postpone=a.postpone,
            ),
        ),
        "run-command": (
            "RunCommand",
            lambda a: autom.build_run_command_params(a.command_line, a.current_directory or ""),
        ),
        "kill-process": (
            "KillProcessByPid",
            lambda a: autom.build_kill_process_params(
                pid=a.pid,
                executable_hash_sha1=a.sha1 or "",
                executable_hash_sha2_256=a.sha256 or "",
            ),
        ),
        "apply-patch": (
            "ApplyApplicationPatch",
            lambda a: autom.build_apply_patch_params(a.application_uuid),
        ),
    }
    if cmd in builders:
        action_name, param_builder = builders[cmd]
        params = param_builder(args) if param_builder else None
        body = autom.build_task(action_name, params=params, **_task_common(args))
        _print_json(client.create_task(body))
        return 0

    return 0


def _load_body(file: str | None) -> dict | None:
    """Read a JSON request body from *file* (``-`` reads stdin), else ``None``."""
    if not file:
        return None
    text = sys.stdin.read() if file == "-" else Path(file).read_text()
    return json.loads(text)


def cmd_detections(args: argparse.Namespace) -> int:
    """Incident Management — Detections endpoints."""
    client = _detections_client(args)
    cmd = args.detections_cmd
    if cmd == "list":
        _print_json(
            client.list_detections(
                args.version,
                device_uuid=args.device,
                start_time=args.start_time,
                end_time=args.end_time,
                page_size=args.page_size,
                page_token=args.page_token,
            )
        )
    elif cmd == "get":
        _print_json(client.get_detection(args.detection_uuid, args.version))
    elif cmd == "resolve":
        _print_json(client.resolve_detection(args.detection_uuid, args.note))
    elif cmd == "batch-get":
        _print_json(client.batch_get_detections(args.detection_uuids))
    return 0


def cmd_detection_groups(args: argparse.Namespace) -> int:
    """Incident Management — DetectionGroups endpoints."""
    client = _detections_client(args)
    cmd = args.detection_groups_cmd
    if cmd == "list":
        _print_json(
            client.list_detection_groups(
                page_size=args.page_size, page_token=args.page_token
            )
        )
    elif cmd == "get":
        _print_json(client.get_detection_group(args.group_uuid))
    elif cmd == "resolve":
        _print_json(client.resolve_detection_group(args.group_uuid, args.note))
    elif cmd == "search":
        _print_json(
            client.search_detection_groups(
                args.filter, return_total_size=args.total_size
            )
        )
    return 0


def cmd_edr_rules(args: argparse.Namespace) -> int:
    """Incident Management — EdrRules endpoints."""
    client = _edr_client(args)
    cmd = args.edr_rules_cmd
    if cmd == "list":
        _print_json(
            client.list_edr_rules(page_size=args.page_size, page_token=args.page_token)
        )
    elif cmd == "create":
        _print_json(client.create_edr_rule(body=_load_body(args.file)))
    elif cmd == "get":
        _print_json(client.get_edr_rule(args.rule_uuid))
    elif cmd == "delete":
        _print_json(client.delete_edr_rule(args.rule_uuid))
    elif cmd == "enable":
        _print_json(client.enable_edr_rule(args.rule_uuid))
    elif cmd == "disable":
        _print_json(client.disable_edr_rule(args.rule_uuid))
    elif cmd == "update-definition":
        _print_json(
            client.update_edr_rule_definition(args.rule_uuid, args.xml_definition)
        )
    return 0


def cmd_edr_exclusions(args: argparse.Namespace) -> int:
    """Incident Management — EdrRuleExclusions endpoints."""
    client = _edr_client(args)
    cmd = args.edr_exclusions_cmd
    if cmd == "list":
        _print_json(
            client.list_edr_rule_exclusions(
                page_size=args.page_size, page_token=args.page_token
            )
        )
    elif cmd == "create":
        _print_json(client.create_edr_rule_exclusion(body=_load_body(args.file)))
    elif cmd == "get":
        _print_json(client.get_edr_rule_exclusion(args.exclusion_uuid))
    elif cmd == "delete":
        _print_json(client.delete_edr_rule_exclusion(args.exclusion_uuid))
    elif cmd == "update-definition":
        _print_json(
            client.update_edr_rule_exclusion_definition(
                args.exclusion_uuid, args.xml_definition
            )
        )
    return 0


def cmd_incidents(args: argparse.Namespace) -> int:
    """Incident Management — Incidents endpoints."""
    client = _incidents_client(args)
    cmd = args.incidents_cmd
    if cmd == "list":
        _print_json(
            client.list_incidents(page_size=args.page_size, page_token=args.page_token)
        )
    elif cmd == "get":
        _print_json(client.get_incident(args.incident_uuid))
    elif cmd == "update-attributes":
        _print_json(
            client.update_incident_basic_attributes(
                args.incident_uuid,
                assignee_uuid=args.assignee,
                description=args.description,
                display_name=args.name,
                severity=args.severity,
                update_mask=args.update_mask,
            )
        )
    elif cmd == "close":
        _print_json(
            client.close_incident(
                args.incident_uuid,
                closure_reason=args.reason,
                final_comment=args.comment,
            )
        )
    elif cmd == "reopen":
        _print_json(client.reopen_incident(args.incident_uuid))
    return 0


def cmd_incident_comments(args: argparse.Namespace) -> int:
    """Incident Management — IncidentComments endpoints."""
    client = _incidents_client(args)
    cmd = args.incident_comments_cmd
    if cmd == "list":
        _print_json(
            client.list_incident_comments(
                args.incident_uuid, page_size=args.page_size, page_token=args.page_token
            )
        )
    elif cmd == "create":
        _print_json(client.create_incident_comment(args.incident_uuid, args.text))
    elif cmd == "get":
        _print_json(
            client.get_incident_comment(args.incident_uuid, args.comment_uuid)
        )
    elif cmd == "delete":
        _print_json(
            client.delete_incident_comment(args.incident_uuid, args.comment_uuid)
        )
    elif cmd == "update-text":
        _print_json(
            client.update_incident_comment_text(
                args.incident_uuid, args.comment_uuid, args.text
            )
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cli.py",
        description=(
            "ESET Connect CLI: OAuth token (/oauth/token), Device / Application / "
            "Asset / Policy Management, Automation (Device tasks) and Incident "
            "Management (detections, EDR rules, incidents) APIs "
            "(resolves .env + regional gateway URLs)."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_env = sub.add_parser("env-check", help="Validate .env + resolved paths (no network)")
    p_env.set_defaults(func=cmd_env_check)

    p_token = sub.add_parser("token", help="Get an OAuth Bearer token")
    p_token.add_argument(
        "--refresh",
        metavar="REFRESH_TOKEN",
        help="Use the refresh_token grant instead of password",
    )
    p_token.add_argument(
        "--print-request",
        action="store_true",
        help="Dry run: print the request (secrets masked) without calling the API",
    )
    p_token.add_argument(
        "--token-only",
        action="store_true",
        help="On success, print only the access_token",
    )
    p_token.set_defaults(func=cmd_token)

    # Common options for API (Device Management) commands.
    api_common = argparse.ArgumentParser(add_help=False)
    api_common.add_argument(
        "--token",
        metavar="ACCESS_TOKEN",
        help="Bearer access token to use (skip the password grant)",
    )

    def _add_paging(p: argparse.ArgumentParser) -> None:
        p.add_argument("--page-size", type=int, default=None, help="Page size")
        p.add_argument("--page-token", default=None, help="Pagination token")

    p_groups = sub.add_parser("groups", parents=[api_common], help="Device groups")
    groups_sub = p_groups.add_subparsers(dest="groups_cmd", required=True)

    g_list = groups_sub.add_parser("list", help="GET /v1/device_groups")
    _add_paging(g_list)

    g_devices = groups_sub.add_parser("devices", help="GET /v1/device_groups/{groupUuid}/devices")
    g_devices.add_argument("group_uuid", help="Device group UUID")
    _add_paging(g_devices)

    p_groups.set_defaults(func=cmd_groups)

    p_devices = sub.add_parser("devices", parents=[api_common], help="Devices")
    devices_sub = p_devices.add_subparsers(dest="devices_cmd", required=True)

    d_list = devices_sub.add_parser("list", help="GET /v1/devices")
    _add_paging(d_list)

    d_get = devices_sub.add_parser("get", help="GET /v1/devices/{deviceUuid}")
    d_get.add_argument("device_uuid", help="Device UUID")

    d_move = devices_sub.add_parser("move", help="POST /v1/devices/{deviceUuid}:move")
    d_move.add_argument("device_uuid", help="Device UUID")
    d_move.add_argument("--group", required=True, metavar="GROUP_UUID", help="Target device group UUID")

    d_rename = devices_sub.add_parser("rename", help="POST /v1/devices/{deviceUuid}:rename")
    d_rename.add_argument("device_uuid", help="Device UUID")
    d_rename.add_argument("--name", required=True, help="New device name")

    d_bget = devices_sub.add_parser("batch-get", help="GET /v1/devices:batchGet")
    d_bget.add_argument("device_uuids", nargs="+", help="One or more device UUIDs")

    d_bimport = devices_sub.add_parser("batch-import", help="POST /v1/devices:batchImport")
    d_bimport.add_argument("--file", required=True, help="JSON file: a devices list or a full request body")

    p_devices.set_defaults(func=cmd_devices)

    # Asset Management API (group CRUD): create / delete / move / rename.
    p_assets = sub.add_parser(
        "assets", parents=[api_common], help="Asset Management (group create/delete/move/rename)"
    )
    assets_sub = p_assets.add_subparsers(dest="assets_cmd", required=True)

    a_create = assets_sub.add_parser("create", help="POST /v1/groups")
    a_create.add_argument("--name", required=True, help="New group name")
    a_create.add_argument("--parent", metavar="PARENT_UUID", help="Parent group UUID")

    a_delete = assets_sub.add_parser("delete", help="DELETE /v1/groups/{groupUuid}")
    a_delete.add_argument("group_uuid", help="Group UUID")

    a_move = assets_sub.add_parser("move", help="POST /v1/groups/{groupUuid}:move")
    a_move.add_argument("group_uuid", help="Group UUID")
    a_move.add_argument("--parent", required=True, metavar="PARENT_UUID", help="Target parent group UUID")

    a_rename = assets_sub.add_parser("rename", help="POST /v1/groups/{groupUuid}:rename")
    a_rename.add_argument("group_uuid", help="Group UUID")
    a_rename.add_argument("--name", required=True, help="New group name")

    p_assets.set_defaults(func=cmd_assets)

    # Policy Management API (v2).
    p_pol = sub.add_parser("policies", parents=[api_common], help="Policy Management (policies)")
    pol_sub = p_pol.add_subparsers(dest="policies_cmd", required=True)

    pl_list = pol_sub.add_parser("list", help="GET /v2/policies")
    _add_paging(pl_list)

    pl_get = pol_sub.add_parser("get", help="GET /v2/policies/{policyUuid}")
    pl_get.add_argument("policy_uuid", help="Policy UUID")

    pl_create = pol_sub.add_parser("create", help="POST /v2/policies")
    pl_create.add_argument("--file", required=True, help="JSON file with the policy definition body")

    pl_delete = pol_sub.add_parser("delete", help="DELETE /v2/policies/{policyUuid}")
    pl_delete.add_argument("policy_uuid", help="Policy UUID")

    p_pol.set_defaults(func=cmd_policies)

    p_pa = sub.add_parser(
        "policy-assignments", parents=[api_common], help="Policy Management (assignments)"
    )
    pa_sub = p_pa.add_subparsers(dest="assignments_cmd", required=True)

    pa_list = pa_sub.add_parser("list", help="GET /v2/policy-assignments")
    _add_paging(pa_list)

    pa_get = pa_sub.add_parser("get", help="GET /v2/policy-assignments/{assignmentUuid}")
    pa_get.add_argument("assignment_uuid", help="Policy assignment UUID")

    pa_assign = pa_sub.add_parser("assign", help="POST /v2/policy-assignments")
    pa_assign.add_argument("--file", required=True, help="JSON file with the assignment body")

    pa_unassign = pa_sub.add_parser("unassign", help="DELETE /v2/policy-assignments/{assignmentUuid}")
    pa_unassign.add_argument("assignment_uuid", help="Policy assignment UUID")

    pa_rank = pa_sub.add_parser(
        "update-ranking", help="POST /v2/policy-assignments/{assignmentUuid}:updateRanking"
    )
    pa_rank.add_argument("assignment_uuid", help="Policy assignment UUID")
    pa_rank.add_argument("--ranking", type=int, help="New ranking value")
    pa_rank.add_argument("--file", help="JSON file with the ranking body (overrides --ranking)")

    p_pa.set_defaults(func=cmd_policy_assignments)

    # Application Management API (different gateway host, resolved as app_url).
    p_exe = sub.add_parser(
        "executables", parents=[api_common], help="Application Management (executables)"
    )
    exe_sub = p_exe.add_subparsers(dest="executables_cmd", required=True)

    e_list = exe_sub.add_parser("list", help="GET /v1/executables")
    _add_paging(e_list)

    e_get = exe_sub.add_parser("get", help="GET /v1/executables/{executableUuid}")
    e_get.add_argument("executable_uuid", help="Executable UUID")

    e_block = exe_sub.add_parser("block", help="POST /v1/executables/{executableUuid}:block")
    e_block.add_argument("executable_uuid", help="Executable UUID")

    e_unblock = exe_sub.add_parser(
        "unblock", help="POST /v1/executables/{executableUuid}:unblock"
    )
    e_unblock.add_argument("executable_uuid", help="Executable UUID")

    p_exe.set_defaults(func=cmd_executables)

    # Incident Management API (gateway host: incident-management, incident_url).
    p_det = sub.add_parser(
        "detections", parents=[api_common], help="Incident Management (detections)"
    )
    det_sub = p_det.add_subparsers(dest="detections_cmd", required=True)

    def _add_version(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "--version",
            choices=["v1", "v2"],
            default="v1",
            help="API version (v1 = PROTECT/Inspect, v2 = Cloud Office Security/Inspect)",
        )

    dt_list = det_sub.add_parser("list", help="GET /{version}/detections")
    _add_version(dt_list)
    dt_list.add_argument("--device", metavar="DEVICE_UUID", help="Filter by device UUID")
    dt_list.add_argument("--start-time", help="Filter: occurred after (ISO 8601)")
    dt_list.add_argument("--end-time", help="Filter: occurred before (ISO 8601)")
    _add_paging(dt_list)

    dt_get = det_sub.add_parser("get", help="GET /{version}/detections/{detectionUuid}")
    dt_get.add_argument("detection_uuid", help="Detection UUID")
    _add_version(dt_get)

    dt_resolve = det_sub.add_parser(
        "resolve", help="POST /v2/detections/{detectionUuid}:resolve"
    )
    dt_resolve.add_argument("detection_uuid", help="Detection UUID")
    dt_resolve.add_argument("--note", help="Text explaining the resolution")

    dt_bget = det_sub.add_parser("batch-get", help="POST /v2/detections:batchGet")
    dt_bget.add_argument("detection_uuids", nargs="+", help="One or more detection UUIDs")

    p_det.set_defaults(func=cmd_detections)

    p_dg = sub.add_parser(
        "detection-groups", parents=[api_common], help="Incident Management (detection groups)"
    )
    dg_sub = p_dg.add_subparsers(dest="detection_groups_cmd", required=True)

    dg_list = dg_sub.add_parser("list", help="GET /v2/detection-groups")
    _add_paging(dg_list)

    dg_get = dg_sub.add_parser("get", help="GET /v2/detection-groups/{groupUuid}")
    dg_get.add_argument("group_uuid", help="Detection group UUID")

    dg_resolve = dg_sub.add_parser(
        "resolve", help="POST /v2/detection-groups/{groupUuid}:resolve"
    )
    dg_resolve.add_argument("group_uuid", help="Detection group UUID")
    dg_resolve.add_argument("--note", help="Text explaining the resolution")

    dg_search = dg_sub.add_parser("search", help="POST /v2/detection-groups:search")
    dg_search.add_argument("--filter", help="Filter, e.g. \"resolved eq 0\"")
    dg_search.add_argument(
        "--total-size", action="store_true", help="Compute total_size in the response"
    )

    p_dg.set_defaults(func=cmd_detection_groups)

    p_edr = sub.add_parser(
        "edr-rules", parents=[api_common], help="Incident Management (EDR rules)"
    )
    edr_sub = p_edr.add_subparsers(dest="edr_rules_cmd", required=True)

    er_list = edr_sub.add_parser("list", help="GET /v2/edr-rules")
    _add_paging(er_list)

    er_create = edr_sub.add_parser("create", help="POST /v2/edr-rules")
    er_create.add_argument(
        "--file", required=True, help="JSON body (or '-' for stdin), e.g. {\"rule\": {...}}"
    )

    er_get = edr_sub.add_parser("get", help="GET /v2/edr-rules/{ruleUuid}")
    er_get.add_argument("rule_uuid", help="EDR rule UUID")

    er_delete = edr_sub.add_parser("delete", help="DELETE /v2/edr-rules/{ruleUuid}")
    er_delete.add_argument("rule_uuid", help="EDR rule UUID")

    er_enable = edr_sub.add_parser("enable", help="POST /v2/edr-rules/{ruleUuid}:enable")
    er_enable.add_argument("rule_uuid", help="EDR rule UUID")

    er_disable = edr_sub.add_parser("disable", help="POST /v2/edr-rules/{ruleUuid}:disable")
    er_disable.add_argument("rule_uuid", help="EDR rule UUID")

    er_upd = edr_sub.add_parser(
        "update-definition", help="POST /v2/edr-rules/{ruleUuid}:updateDefinition"
    )
    er_upd.add_argument("rule_uuid", help="EDR rule UUID")
    er_upd.add_argument("--xml-definition", required=True, help="New XML rule definition")

    p_edr.set_defaults(func=cmd_edr_rules)

    p_exc = sub.add_parser(
        "edr-exclusions", parents=[api_common], help="Incident Management (EDR rule exclusions)"
    )
    exc_sub = p_exc.add_subparsers(dest="edr_exclusions_cmd", required=True)

    ex_list = exc_sub.add_parser("list", help="GET /v2/edr-rule-exclusions")
    _add_paging(ex_list)

    ex_create = exc_sub.add_parser("create", help="POST /v2/edr-rule-exclusions")
    ex_create.add_argument(
        "--file", required=True, help="JSON body (or '-' for stdin), e.g. {\"exclusion\": {...}}"
    )

    ex_get = exc_sub.add_parser("get", help="GET /v2/edr-rule-exclusions/{exclusionUuid}")
    ex_get.add_argument("exclusion_uuid", help="EDR rule exclusion UUID")

    ex_delete = exc_sub.add_parser(
        "delete", help="DELETE /v2/edr-rule-exclusions/{exclusionUuid}"
    )
    ex_delete.add_argument("exclusion_uuid", help="EDR rule exclusion UUID")

    ex_upd = exc_sub.add_parser(
        "update-definition",
        help="POST /v2/edr-rule-exclusions/{exclusionUuid}:updateDefinition",
    )
    ex_upd.add_argument("exclusion_uuid", help="EDR rule exclusion UUID")
    ex_upd.add_argument("--xml-definition", required=True, help="New XML exclusion definition")

    p_exc.set_defaults(func=cmd_edr_exclusions)

    p_inc = sub.add_parser(
        "incidents", parents=[api_common], help="Incident Management (incidents)"
    )
    inc_sub = p_inc.add_subparsers(dest="incidents_cmd", required=True)

    in_list = inc_sub.add_parser("list", help="GET /v2/incidents")
    _add_paging(in_list)

    in_get = inc_sub.add_parser("get", help="GET /v2/incidents/{incidentUuid}")
    in_get.add_argument("incident_uuid", help="Incident UUID")

    in_upd = inc_sub.add_parser(
        "update-attributes",
        help="POST /v2/incidents/{incidentUuid}/basic-attributes:update",
    )
    in_upd.add_argument("incident_uuid", help="Incident UUID")
    in_upd.add_argument("--assignee", metavar="USER_UUID", help="Assignee user UUID")
    in_upd.add_argument("--description", help="New description")
    in_upd.add_argument("--name", help="New display name")
    in_upd.add_argument(
        "--severity",
        help="Severity, e.g. INCIDENT_SEVERITY_LEVEL_LOW/MEDIUM/HIGH",
    )
    in_upd.add_argument(
        "--update-mask",
        help="Comma-separated fields to update (default: derived from options)",
    )

    in_close = inc_sub.add_parser("close", help="POST /v2/incidents/{incidentUuid}:close")
    in_close.add_argument("incident_uuid", help="Incident UUID")
    in_close.add_argument(
        "--reason",
        help="Closure reason, e.g. INCIDENT_RESOLVE_REASON_TRUE_POSITIVE",
    )
    in_close.add_argument("--comment", help="Final comment text")

    in_reopen = inc_sub.add_parser("reopen", help="POST /v2/incidents/{incidentUuid}:reopen")
    in_reopen.add_argument("incident_uuid", help="Incident UUID")

    p_inc.set_defaults(func=cmd_incidents)

    p_com = sub.add_parser(
        "incident-comments", parents=[api_common], help="Incident Management (incident comments)"
    )
    com_sub = p_com.add_subparsers(dest="incident_comments_cmd", required=True)

    cm_list = com_sub.add_parser("list", help="GET /v2/incidents/{incidentUuid}/comments")
    cm_list.add_argument("incident_uuid", help="Incident UUID")
    _add_paging(cm_list)

    cm_create = com_sub.add_parser(
        "create", help="POST /v2/incidents/{incidentUuid}/comments"
    )
    cm_create.add_argument("incident_uuid", help="Incident UUID")
    cm_create.add_argument("--text", required=True, help="Comment text")

    cm_get = com_sub.add_parser(
        "get", help="GET /v2/incidents/{incidentUuid}/comments/{commentUuid}"
    )
    cm_get.add_argument("incident_uuid", help="Incident UUID")
    cm_get.add_argument("comment_uuid", help="Comment UUID")

    cm_delete = com_sub.add_parser(
        "delete", help="DELETE /v2/incidents/{incidentUuid}/comments/{commentUuid}"
    )
    cm_delete.add_argument("incident_uuid", help="Incident UUID")
    cm_delete.add_argument("comment_uuid", help="Comment UUID")

    cm_upd = com_sub.add_parser(
        "update-text",
        help="POST /v2/incidents/{incidentUuid}/comments/{commentUuid}/text:update",
    )
    cm_upd.add_argument("incident_uuid", help="Incident UUID")
    cm_upd.add_argument("comment_uuid", help="Comment UUID")
    cm_upd.add_argument("--text", required=True, help="New comment text")

    p_com.set_defaults(func=cmd_incident_comments)

    # Automation API (Device tasks) — lives on the automation gateway.
    p_tasks = sub.add_parser(
        "tasks", parents=[api_common], help="Automation (Device tasks)"
    )
    tasks_sub = p_tasks.add_subparsers(dest="tasks_cmd", required=True)

    t_list = tasks_sub.add_parser("list", help="GET /v1/device_tasks")
    _add_paging(t_list)

    t_get = tasks_sub.add_parser("get", help="GET /v1/device_tasks/{taskUuid}")
    t_get.add_argument("task_uuid", help="Device task UUID")

    t_delete = tasks_sub.add_parser("delete", help="DELETE /v1/device_tasks/{taskUuid}")
    t_delete.add_argument("task_uuid", help="Device task UUID")

    t_runs = tasks_sub.add_parser("runs", help="GET /v1/device_tasks/{taskUuid}/runs")
    t_runs.add_argument("task_uuid", help="Device task UUID")
    _add_paging(t_runs)

    t_utargets = tasks_sub.add_parser(
        "update-targets", help="POST /v1/device_tasks/{taskUuid}:updateTaskTargets"
    )
    t_utargets.add_argument("task_uuid", help="Device task UUID")
    t_utargets.add_argument("--device", action="append", default=[], metavar="UUID", help="Target device UUID (repeatable)")
    t_utargets.add_argument("--group", action="append", default=[], metavar="UUID", help="Target device-group UUID (repeatable)")
    t_utargets.add_argument("--file", help="JSON file with the full targets body (overrides --device/--group)")

    t_utriggers = tasks_sub.add_parser(
        "update-triggers", help="POST /v1/device_tasks/{taskUuid}:updateTaskTriggers"
    )
    t_utriggers.add_argument("task_uuid", help="Device task UUID")
    t_utriggers.add_argument("--expire-time", metavar="RFC3339", help="Manual trigger expireTime (e.g. 2026-03-21T11:30:34Z)")
    t_utriggers.add_argument("--file", help="JSON file with the full triggers body (overrides --expire-time)")

    # Shared target / metadata options for every create-style subcommand.
    task_common = argparse.ArgumentParser(add_help=False)
    task_common.add_argument("--device", action="append", default=[], metavar="UUID", help="Target device UUID (repeatable)")
    task_common.add_argument("--group", action="append", default=[], metavar="UUID", help="Target device-group UUID (repeatable)")
    task_common.add_argument("--display-name", help="Task display name")
    task_common.add_argument("--description", help="Task description")
    task_common.add_argument("--expire-time", metavar="RFC3339", help="Manual trigger expireTime (e.g. 2026-03-21T11:30:34Z)")

    t_create = tasks_sub.add_parser(
        "create", parents=[task_common], help="POST /v1/device_tasks (generic create)"
    )
    t_create.add_argument("--action", choices=sorted(autom.TASK_ACTIONS), help="task.action.name")
    t_create.add_argument("--params-file", help="JSON file for action.params (must include @type)")
    t_create.add_argument("--file", help="JSON file with the full {'task': {...}} body (overrides all other flags)")

    # Convenience builders (one per documented Device task action).
    tasks_sub.add_parser("isolate", parents=[task_common], help="Create StartNetworkIsolation task")
    tasks_sub.add_parser("end-isolation", parents=[task_common], help="Create EndNetworkIsolation task")
    tasks_sub.add_parser("stop-managing", parents=[task_common], help="Create StopManaging task")
    tasks_sub.add_parser("av-remove", parents=[task_common], help="Create ThirdPartyAVRemove task")
    tasks_sub.add_parser("logout", parents=[task_common], help="Create LogOffComputerUser task")
    tasks_sub.add_parser("vulnerability-scan", parents=[task_common], help="Create InitiateVulnerabilityScan task")

    t_scan = tasks_sub.add_parser("scan", parents=[task_common], help="Create OnDemandScan task")
    t_scan.add_argument("--scan-profile", choices=autom.SCAN_PROFILES, default="InDepth", help="Scan profile")
    t_scan.add_argument("--custom-profile", help="Custom profile name (for scan-profile Custom)")
    t_scan.add_argument("--scan-target", action="append", default=[], metavar="TARGET", help="Scan target (repeatable; empty = eset://AllTargets)")
    t_scan.add_argument("--cleaning", action="store_true", help="Enable cleaning")
    t_scan.add_argument("--shutdown", action="store_true", help="Shut down after scan")
    t_scan.add_argument("--postpone", choices=autom.POSTPONE_VALUES, help="Allowed user postpone duration")

    t_shutdown = tasks_sub.add_parser("shutdown", parents=[task_common], help="Create ShutdownComputer task")
    t_shutdown.add_argument("--restart", action="store_true", help="Restart instead of shutting down")
    t_shutdown.add_argument("--postpone", choices=autom.POSTPONE_VALUES, help="Allowed user postpone duration")

    t_osupd = tasks_sub.add_parser("os-update", parents=[task_common], help="Create SystemUpdate task")
    t_osupd.add_argument("--accept-eula", action="store_true", help="Accept EULA automatically (Windows)")
    t_osupd.add_argument("--optional-updates", action="store_true", help="Install optional updates (Windows)")
    t_osupd.add_argument("--allow-reboot", action="store_true", help="Allow reboot if an update requests it")
    t_osupd.add_argument("--postpone", choices=autom.POSTPONE_VALUES, help="Allowed user postpone duration")

    t_run = tasks_sub.add_parser("run-command", parents=[task_common], help="Create RunCommand task")
    t_run.add_argument("--command-line", required=True, help="Command line to execute")
    t_run.add_argument("--current-directory", help="Working directory for the script")

    t_kill = tasks_sub.add_parser("kill-process", parents=[task_common], help="Create KillProcessByPid task")
    t_kill.add_argument("--pid", type=int, required=True, help="Local process ID")
    t_kill.add_argument("--sha1", help="SHA1 hash of the process executable")
    t_kill.add_argument("--sha256", help="SHA2-256 hash of the process executable")

    t_patch = tasks_sub.add_parser("apply-patch", parents=[task_common], help="Create ApplyApplicationPatch task")
    t_patch.add_argument("--application-uuid", required=True, help="UUID of the application to patch")

    p_tasks.set_defaults(func=cmd_tasks)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (ConfigError, auth.AuthError) as exc:
        _print_json({"ok": False, "error": str(exc)})
        return 1
    except ApiError as exc:
        _print_json(
            {
                "ok": False,
                "status": exc.status,
                "request_id": exc.request_id,
                "error": exc.body,
            }
        )
        return 1
    except requests.RequestException as exc:
        _print_json({"ok": False, "error": f"HTTP request failed: {exc}"})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
