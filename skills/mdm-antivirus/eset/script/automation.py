#!/usr/bin/env python3
"""ESET Connect — Automation API client (Device tasks).

Implements every endpoint documented at
https://help.eset.com/eset_connect/en-US/automation.html:

DeviceTasks
    GET    /v1/device_tasks                                  list_tasks()
    POST   /v1/device_tasks                                  create_task()
    GET    /v1/device_tasks/{taskUuid}                       get_task()
    DELETE /v1/device_tasks/{taskUuid}                       delete_task()
    GET    /v1/device_tasks/{taskUuid}/runs                  list_task_runs()
    POST   /v1/device_tasks/{taskUuid}:updateTaskTargets     update_task_targets()
    POST   /v1/device_tasks/{taskUuid}:updateTaskTriggers    update_task_triggers()

The Automation API triggers actions ("Device tasks", called "Client tasks" in the
ESET PROTECT Web Console) on target devices. A task is created with an
``action.name`` (see :data:`TASK_ACTIONS`), a set of ``targets`` (device and/or
device-group UUIDs) and one or more ``triggers`` (usually a ``manual`` trigger).
Some actions also take an ``action.params`` object keyed by a ``@type`` protobuf
URL — the :func:`build_*` helpers below assemble those payloads.

Automation lives on the ``automation`` gateway (the same host as Device
Management, resolved by ``cli.py`` as ``api_url``/``automation_url``, override
``ESET_AUTOMATION_URL``). The client only needs that base URL and a Bearer token.
"""

from __future__ import annotations

import argparse
from typing import Any, Iterable, Iterator

from _client import TOKEN_PARENT, ApiError, BaseClient
from skill_env import ConfigError


#: task.action.name -> human label (complete list from the Automation docs).
TASK_ACTIONS: dict[str, str] = {
    "StartNetworkIsolation": "Isolate computer from network",
    "EndNetworkIsolation": "End computer isolation from network",
    "OnDemandScan": "On-demand scan",
    "ShutdownComputer": "Shut down computer",
    "StopManaging": "Stop managing (Uninstall ESET Management Agent)",
    "ThirdPartyAVRemove": "Software Uninstall (Third-party antivirus software)",
    "SystemUpdate": "Operating system update",
    "RunCommand": "Run command",
    "KillProcessByPid": "Kill process by PID",
    "LogOffComputerUser": "Log Out",
    "InitiateVulnerabilityScan": "Initiate Vulnerability Scan",
    "ApplyApplicationPatch": "Apply Application Patch",
}

#: ``postpone`` durations accepted by the power/reboot action objects.
POSTPONE_VALUES = (
    "Cannot",
    "OneHour",
    "ThreeHours",
    "FiveHours",
    "OneDay",
    "ThreeDays",
    "SevenDays",
    "FifteenDays",
    "TwentyDays",
    "ThirtyDays",
)

#: ``scanProfile`` values accepted by the OnDemandScan params.
SCAN_PROFILES = ("InDepth", "Smart", "ContextMenu", "MyProfile", "Custom")

# protobuf ``@type`` URLs for action.params payloads.
_TYPE_SHUTDOWN = "type.googleapis.com/Era.Common.DataDefinition.Task.OS.ShutdownComputer"
_TYPE_SCAN = "type.googleapis.com/Era.Common.DataDefinition.Task.ESS.OnDemandScan"
_TYPE_SYSTEM_UPDATE = "type.googleapis.com/Era.Common.DataDefinition.Task.OS.SystemUpdate"
_TYPE_RUN_COMMAND = "type.googleapis.com/Era.Common.DataDefinition.Task.OS.RunCommand"
_TYPE_KILL_PROCESS = "type.googleapis.com/eset.dotnod.os_integration.v1.KillProcessByPidRequest"
_TYPE_VULN_SCAN = "type.googleapis.com/eset.dotnod.vulnerability_management.v1.ScanRequest"
_TYPE_APPLY_PATCH = "type.googleapis.com/eset.dotnod.patch_management.v1.ApplyApplicationPatchRequest"



def build_targets(
    devices: Iterable[str] | None = None,
    groups: Iterable[str] | None = None,
) -> dict:
    """Build a task ``targets`` object from device and/or device-group UUIDs.

    At least one device or group must be supplied.
    """
    device_uuids = list(devices or [])
    group_uuids = list(groups or [])
    if not device_uuids and not group_uuids:
        raise ValueError("at least one device UUID or device-group UUID is required")
    targets: dict = {}
    if device_uuids:
        targets["devicesUuids"] = device_uuids
    if group_uuids:
        targets["deviceGroupsUuids"] = group_uuids
    return targets


def build_manual_trigger(expire_time: str | None = None) -> dict:
    """Build a single ``manual`` trigger, optionally with an ``expireTime``.

    *expire_time* is an RFC 3339 / UTC timestamp (e.g. ``2026-03-21T11:30:34Z``).
    Omit it to trigger the task as soon as possible with no expiry.
    """
    manual: dict = {}
    if expire_time:
        manual["expireTime"] = expire_time
    return {"manual": manual}


def build_task(
    action_name: str,
    *,
    targets: dict,
    display_name: str | None = None,
    description: str | None = None,
    params: dict | None = None,
    triggers: list[dict] | None = None,
    expire_time: str | None = None,
) -> dict:
    """Assemble a full ``{"task": {...}}`` request body for ``create_task``.

    *action_name* is one of :data:`TASK_ACTIONS`. *targets* comes from
    :func:`build_targets`. *params* (when required by the action) must already
    include its ``@type`` key. If *triggers* is omitted a single ``manual``
    trigger is created (using *expire_time* when given).
    """
    action: dict = {"name": action_name}
    if params is not None:
        action["params"] = params

    task: dict = {"targets": targets, "action": action}
    if display_name is not None:
        task["displayName"] = display_name
    if description is not None:
        task["description"] = description
    task["triggers"] = triggers if triggers is not None else [
        build_manual_trigger(expire_time)
    ]
    return {"task": task}


def _power_actions(cancel_action: bool | None, postpone: str | None) -> dict | None:
    actions: dict = {}
    if cancel_action is not None:
        actions["cancelAction"] = cancel_action
    if postpone is not None:
        actions["postpone"] = postpone
    return actions or None


def build_shutdown_params(
    *,
    restart: bool = False,
    cancel_action: bool | None = None,
    postpone: str | None = None,
) -> dict:
    """ShutdownComputer params. ``restart=True`` reboots; ``False`` shuts down."""
    params: dict = {"@type": _TYPE_SHUTDOWN, "restart": restart}
    actions = _power_actions(cancel_action, postpone)
    if actions is not None:
        params["actions"] = actions
    return params


def build_scan_params(
    *,
    scan_profile: str = "InDepth",
    custom_profile_name: str = "",
    scan_targets: Iterable[str] | None = None,
    cleaning_enabled: bool = False,
    shutdown_enabled: bool = False,
    shutdown_locked: bool = False,
    cancel_action: bool | None = None,
    postpone: str | None = None,
) -> dict:
    """OnDemandScan params.

    An empty *scan_targets* (or ``["eset://AllTargets"]``) means a full scan.
    """
    params: dict = {
        "@type": _TYPE_SCAN,
        "scanProfile": scan_profile,
        "customProfileName": custom_profile_name,
        "scanTargets": list(scan_targets) if scan_targets is not None else [""],
        "cleaningEnabled": cleaning_enabled,
        "shutdownEnabled": shutdown_enabled,
        "shutdownLocked": shutdown_locked,
    }
    actions = _power_actions(cancel_action, postpone)
    if actions is not None:
        params["powerActions"] = actions
    return params


def build_system_update_params(
    *,
    accept_eula: bool = False,
    install_optional_updates: bool = False,
    allow_reboot: bool = False,
    cancel_action: bool | None = None,
    postpone: str | None = None,
) -> dict:
    """SystemUpdate params (Windows EULA / optional-update / reboot flags)."""
    params: dict = {
        "@type": _TYPE_SYSTEM_UPDATE,
        "acceptEula": accept_eula,
        "installOptionalUpdates": install_optional_updates,
        "allowReboot": allow_reboot,
    }
    actions = _power_actions(cancel_action, postpone)
    if actions is not None:
        params["rebootActions"] = actions
    return params


def build_run_command_params(command_line: str, current_directory: str = "") -> dict:
    """RunCommand params (platform-dependent command line + working directory)."""
    return {
        "@type": _TYPE_RUN_COMMAND,
        "commandLine": command_line,
        "currentDirectory": current_directory,
    }


def build_kill_process_params(
    *,
    pid: int,
    executable_hash_sha1: str = "",
    executable_hash_sha2_256: str = "",
) -> dict:
    """KillProcessByPid params.

    At least one of *executable_hash_sha1* / *executable_hash_sha2_256* must be
    set, otherwise the API returns 400 BAD REQUEST.
    """
    if not executable_hash_sha1 and not executable_hash_sha2_256:
        raise ValueError(
            "provide executable_hash_sha1 and/or executable_hash_sha2_256"
        )
    return {
        "@type": _TYPE_KILL_PROCESS,
        "pid": pid,
        "executableHashSha1": executable_hash_sha1,
        "executableHashSha2_256": executable_hash_sha2_256,
    }


def build_vulnerability_scan_params() -> dict:
    """InitiateVulnerabilityScan params (no extra fields)."""
    return {"@type": _TYPE_VULN_SCAN}


def build_apply_patch_params(application_uuid: str) -> dict:
    """ApplyApplicationPatch params (UUID of the application to patch)."""
    return {"@type": _TYPE_APPLY_PATCH, "application_uuid": application_uuid}


class AutomationError(ApiError):
    """Raised when an Automation API call fails."""

    label = "Automation API"


class AutomationClient(BaseClient):
    """Thin client over the ESET Connect Automation (Device tasks) REST API."""

    error_class = AutomationError
    url_key = "automation_url"


    def list_tasks(
        self, *, page_size: int | None = None, page_token: str | None = None
    ) -> dict:
        """GET /v1/device_tasks — List device tasks."""
        return self._request(
            "GET", "/v1/device_tasks", params=self._page_params(page_size, page_token)
        )

    def create_task(self, body: dict) -> dict:
        """POST /v1/device_tasks — Create a device task.

        *body* is a full ``{"task": {...}}`` payload (see :func:`build_task`).
        """
        return self._request("POST", "/v1/device_tasks", json_body=body)

    def get_task(self, task_uuid: str) -> dict:
        """GET /v1/device_tasks/{taskUuid} — Get a device task."""
        return self._request("GET", f"/v1/device_tasks/{task_uuid}")

    def delete_task(self, task_uuid: str) -> dict:
        """DELETE /v1/device_tasks/{taskUuid} — Delete a device task."""
        return self._request("DELETE", f"/v1/device_tasks/{task_uuid}")

    def list_task_runs(
        self,
        task_uuid: str,
        *,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> dict:
        """GET /v1/device_tasks/{taskUuid}/runs — List runs of a device task."""
        return self._request(
            "GET",
            f"/v1/device_tasks/{task_uuid}/runs",
            params=self._page_params(page_size, page_token),
        )

    def update_task_targets(
        self,
        task_uuid: str,
        targets: dict | None = None,
        *,
        body: dict | None = None,
    ) -> dict:
        """POST /v1/device_tasks/{taskUuid}:updateTaskTargets — Update targets.

        Pass *targets* (from :func:`build_targets`, sent as ``{"targets": ...}``)
        or a raw *body* dict to override the payload.
        """
        payload = body if body is not None else {"targets": targets}
        return self._request(
            "POST",
            f"/v1/device_tasks/{task_uuid}:updateTaskTargets",
            json_body=payload,
        )

    def update_task_triggers(
        self,
        task_uuid: str,
        triggers: list[dict] | None = None,
        *,
        body: dict | None = None,
    ) -> dict:
        """POST /v1/device_tasks/{taskUuid}:updateTaskTriggers — Update triggers.

        Pass *triggers* (a list, sent as ``{"triggers": ...}``) or a raw *body*
        dict to override the payload.
        """
        payload = body if body is not None else {"triggers": triggers}
        return self._request(
            "POST",
            f"/v1/device_tasks/{task_uuid}:updateTaskTriggers",
            json_body=payload,
        )


    def iter_tasks(self, *, page_size: int | None = None) -> Iterator[dict]:
        """Yield every device task, following ``nextPageToken`` pagination."""
        token: str | None = None
        while True:
            page = self.list_tasks(page_size=page_size, page_token=token)
            for task in page.get("tasks", []) or []:
                yield task
            token = page.get("nextPageToken")
            if not token:
                break

    def iter_task_runs(
        self, task_uuid: str, *, page_size: int | None = None
    ) -> Iterator[dict]:
        """Yield every run of a device task, following ``nextPageToken``."""
        token: str | None = None
        while True:
            page = self.list_task_runs(
                task_uuid, page_size=page_size, page_token=token
            )
            for run in page.get("taskRuns", []) or []:
                yield run
            token = page.get("nextPageToken")
            if not token:
                break

    def _task_kwargs(self, args: argparse.Namespace) -> dict:
        return {
            "targets": build_targets(devices=args.device, groups=args.group),
            "display_name": args.display_name,
            "description": args.description,
            "expire_time": args.expire_time,
        }

    def _create_named(
        self, args: argparse.Namespace, action_name: str, params: dict | None = None
    ) -> None:
        self.dump(
            self.create_task(
                build_task(action_name, params=params, **self._task_kwargs(args))
            )
        )
        return None

    def cmd_list(self, args: argparse.Namespace) -> None:
        self.dump(
            self.list_tasks(page_size=args.page_size, page_token=args.page_token)
        )
        return None

    def cmd_get(self, args: argparse.Namespace) -> None:
        self.dump(self.get_task(args.task_uuid))
        return None

    def cmd_delete(self, args: argparse.Namespace) -> None:
        self.dump(self.delete_task(args.task_uuid))
        return None

    def cmd_runs(self, args: argparse.Namespace) -> None:
        self.dump(
            self.list_task_runs(
                args.task_uuid, page_size=args.page_size, page_token=args.page_token
            )
        )
        return None

    def cmd_update_targets(self, args: argparse.Namespace) -> None:
        if args.file:
            self.dump(
                self.update_task_targets(
                    args.task_uuid, body=self.load_json_file(args.file)
                )
            )
        else:
            self.dump(
                self.update_task_targets(
                    args.task_uuid,
                    build_targets(devices=args.device, groups=args.group),
                )
            )
        return None

    def cmd_update_triggers(self, args: argparse.Namespace) -> None:
        if args.file:
            self.dump(
                self.update_task_triggers(
                    args.task_uuid, body=self.load_json_file(args.file)
                )
            )
        else:
            self.dump(
                self.update_task_triggers(
                    args.task_uuid, [build_manual_trigger(args.expire_time)]
                )
            )
        return None

    def cmd_create(self, args: argparse.Namespace) -> None:
        if args.file:
            self.dump(self.create_task(self.load_json_file(args.file)))
            return None
        if not args.action:
            raise ConfigError("create requires --action NAME (or --file body.json)")
        params = (
            self.load_json_file(args.params_file) if args.params_file else None
        )
        self.dump(
            self.create_task(
                build_task(args.action, params=params, **self._task_kwargs(args))
            )
        )
        return None

    def cmd_isolate(self, args: argparse.Namespace) -> None:
        return self._create_named(args, "StartNetworkIsolation")

    def cmd_end_isolation(self, args: argparse.Namespace) -> None:
        return self._create_named(args, "EndNetworkIsolation")

    def cmd_stop_managing(self, args: argparse.Namespace) -> None:
        return self._create_named(args, "StopManaging")

    def cmd_av_remove(self, args: argparse.Namespace) -> None:
        return self._create_named(args, "ThirdPartyAVRemove")

    def cmd_logout(self, args: argparse.Namespace) -> None:
        return self._create_named(args, "LogOffComputerUser")

    def cmd_vulnerability_scan(self, args: argparse.Namespace) -> None:
        return self._create_named(
            args, "InitiateVulnerabilityScan", build_vulnerability_scan_params()
        )

    def cmd_scan(self, args: argparse.Namespace) -> None:
        return self._create_named(
            args,
            "OnDemandScan",
            build_scan_params(
                scan_profile=args.scan_profile,
                custom_profile_name=args.custom_profile or "",
                scan_targets=args.scan_target or None,
                cleaning_enabled=args.cleaning,
                shutdown_enabled=args.shutdown,
                postpone=args.postpone,
            ),
        )

    def cmd_shutdown(self, args: argparse.Namespace) -> None:
        return self._create_named(
            args,
            "ShutdownComputer",
            build_shutdown_params(restart=args.restart, postpone=args.postpone),
        )

    def cmd_os_update(self, args: argparse.Namespace) -> None:
        return self._create_named(
            args,
            "SystemUpdate",
            build_system_update_params(
                accept_eula=args.accept_eula,
                install_optional_updates=args.optional_updates,
                allow_reboot=args.allow_reboot,
                postpone=args.postpone,
            ),
        )

    def cmd_run_command(self, args: argparse.Namespace) -> None:
        return self._create_named(
            args,
            "RunCommand",
            build_run_command_params(
                args.command_line, args.current_directory or ""
            ),
        )

    def cmd_kill_process(self, args: argparse.Namespace) -> None:
        return self._create_named(
            args,
            "KillProcessByPid",
            build_kill_process_params(
                pid=args.pid,
                executable_hash_sha1=args.sha1 or "",
                executable_hash_sha2_256=args.sha256 or "",
            ),
        )

    def cmd_apply_patch(self, args: argparse.Namespace) -> None:
        return self._create_named(
            args,
            "ApplyApplicationPatch",
            build_apply_patch_params(args.application_uuid),
        )

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = AutomationClient()
        p = sub.add_parser(
            "tasks", parents=[TOKEN_PARENT], help="Automation (Device tasks)"
        )
        tasks = p.add_subparsers(required=True)

        t_list = tasks.add_parser("list", help="GET /v1/device_tasks")
        BaseClient.add_paging(t_list)
        t_list.set_defaults(func=client.cmd_list)

        t_get = tasks.add_parser("get", help="GET /v1/device_tasks/{taskUuid}")
        t_get.add_argument("task_uuid", help="Device task UUID")
        t_get.set_defaults(func=client.cmd_get)

        t_delete = tasks.add_parser("delete", help="DELETE /v1/device_tasks/{taskUuid}")
        t_delete.add_argument("task_uuid", help="Device task UUID")
        t_delete.set_defaults(func=client.cmd_delete)

        t_runs = tasks.add_parser("runs", help="GET /v1/device_tasks/{taskUuid}/runs")
        t_runs.add_argument("task_uuid", help="Device task UUID")
        BaseClient.add_paging(t_runs)
        t_runs.set_defaults(func=client.cmd_runs)

        t_utargets = tasks.add_parser(
            "update-targets",
            help="POST /v1/device_tasks/{taskUuid}:updateTaskTargets",
        )
        t_utargets.add_argument("task_uuid", help="Device task UUID")
        t_utargets.add_argument(
            "--device",
            action="append",
            default=[],
            metavar="UUID",
            help="Target device UUID (repeatable)",
        )
        t_utargets.add_argument(
            "--group",
            action="append",
            default=[],
            metavar="UUID",
            help="Target device-group UUID (repeatable)",
        )
        t_utargets.add_argument(
            "--file",
            help="JSON file with the full targets body (overrides --device/--group)",
        )
        t_utargets.set_defaults(func=client.cmd_update_targets)

        t_utriggers = tasks.add_parser(
            "update-triggers",
            help="POST /v1/device_tasks/{taskUuid}:updateTaskTriggers",
        )
        t_utriggers.add_argument("task_uuid", help="Device task UUID")
        t_utriggers.add_argument(
            "--expire-time",
            metavar="RFC3339",
            help="Manual trigger expireTime (e.g. 2026-03-21T11:30:34Z)",
        )
        t_utriggers.add_argument(
            "--file",
            help="JSON file with the full triggers body (overrides --expire-time)",
        )
        t_utriggers.set_defaults(func=client.cmd_update_triggers)

        task_common = argparse.ArgumentParser(add_help=False)
        task_common.add_argument(
            "--device",
            action="append",
            default=[],
            metavar="UUID",
            help="Target device UUID (repeatable)",
        )
        task_common.add_argument(
            "--group",
            action="append",
            default=[],
            metavar="UUID",
            help="Target device-group UUID (repeatable)",
        )
        task_common.add_argument("--display-name", help="Task display name")
        task_common.add_argument("--description", help="Task description")
        task_common.add_argument(
            "--expire-time",
            metavar="RFC3339",
            help="Manual trigger expireTime (e.g. 2026-03-21T11:30:34Z)",
        )

        t_create = tasks.add_parser(
            "create",
            parents=[task_common],
            help="POST /v1/device_tasks (generic create)",
        )
        t_create.add_argument(
            "--action", choices=sorted(TASK_ACTIONS), help="task.action.name"
        )
        t_create.add_argument(
            "--params-file",
            help="JSON file for action.params (must include @type)",
        )
        t_create.add_argument(
            "--file",
            help="JSON file with the full {'task': {...}} body (overrides all other flags)",
        )
        t_create.set_defaults(func=client.cmd_create)

        tasks.add_parser(
            "isolate", parents=[task_common], help="Create StartNetworkIsolation task"
        ).set_defaults(func=client.cmd_isolate)
        tasks.add_parser(
            "end-isolation",
            parents=[task_common],
            help="Create EndNetworkIsolation task",
        ).set_defaults(func=client.cmd_end_isolation)
        tasks.add_parser(
            "stop-managing", parents=[task_common], help="Create StopManaging task"
        ).set_defaults(func=client.cmd_stop_managing)
        tasks.add_parser(
            "av-remove",
            parents=[task_common],
            help="Create ThirdPartyAVRemove task",
        ).set_defaults(func=client.cmd_av_remove)
        tasks.add_parser(
            "logout", parents=[task_common], help="Create LogOffComputerUser task"
        ).set_defaults(func=client.cmd_logout)
        tasks.add_parser(
            "vulnerability-scan",
            parents=[task_common],
            help="Create InitiateVulnerabilityScan task",
        ).set_defaults(func=client.cmd_vulnerability_scan)

        t_scan = tasks.add_parser(
            "scan", parents=[task_common], help="Create OnDemandScan task"
        )
        t_scan.add_argument(
            "--scan-profile",
            choices=SCAN_PROFILES,
            default="InDepth",
            help="Scan profile",
        )
        t_scan.add_argument(
            "--custom-profile",
            help="Custom profile name (for scan-profile Custom)",
        )
        t_scan.add_argument(
            "--scan-target",
            action="append",
            default=[],
            metavar="TARGET",
            help="Scan target (repeatable; empty = eset://AllTargets)",
        )
        t_scan.add_argument("--cleaning", action="store_true", help="Enable cleaning")
        t_scan.add_argument(
            "--shutdown", action="store_true", help="Shut down after scan"
        )
        t_scan.add_argument(
            "--postpone",
            choices=POSTPONE_VALUES,
            help="Allowed user postpone duration",
        )
        t_scan.set_defaults(func=client.cmd_scan)

        t_shutdown = tasks.add_parser(
            "shutdown", parents=[task_common], help="Create ShutdownComputer task"
        )
        t_shutdown.add_argument(
            "--restart", action="store_true", help="Restart instead of shutting down"
        )
        t_shutdown.add_argument(
            "--postpone",
            choices=POSTPONE_VALUES,
            help="Allowed user postpone duration",
        )
        t_shutdown.set_defaults(func=client.cmd_shutdown)

        t_osupd = tasks.add_parser(
            "os-update", parents=[task_common], help="Create SystemUpdate task"
        )
        t_osupd.add_argument(
            "--accept-eula",
            action="store_true",
            help="Accept EULA automatically (Windows)",
        )
        t_osupd.add_argument(
            "--optional-updates",
            action="store_true",
            help="Install optional updates (Windows)",
        )
        t_osupd.add_argument(
            "--allow-reboot",
            action="store_true",
            help="Allow reboot if an update requests it",
        )
        t_osupd.add_argument(
            "--postpone",
            choices=POSTPONE_VALUES,
            help="Allowed user postpone duration",
        )
        t_osupd.set_defaults(func=client.cmd_os_update)

        t_run = tasks.add_parser(
            "run-command", parents=[task_common], help="Create RunCommand task"
        )
        t_run.add_argument("--command-line", required=True, help="Command line to execute")
        t_run.add_argument(
            "--current-directory", help="Working directory for the script"
        )
        t_run.set_defaults(func=client.cmd_run_command)

        t_kill = tasks.add_parser(
            "kill-process", parents=[task_common], help="Create KillProcessByPid task"
        )
        t_kill.add_argument("--pid", type=int, required=True, help="Local process ID")
        t_kill.add_argument("--sha1", help="SHA1 hash of the process executable")
        t_kill.add_argument(
            "--sha256", help="SHA2-256 hash of the process executable"
        )
        t_kill.set_defaults(func=client.cmd_kill_process)

        t_patch = tasks.add_parser(
            "apply-patch",
            parents=[task_common],
            help="Create ApplyApplicationPatch task",
        )
        t_patch.add_argument(
            "--application-uuid",
            required=True,
            help="UUID of the application to patch",
        )
        t_patch.set_defaults(func=client.cmd_apply_patch)
