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

from typing import Any, Iterable, Iterator

from _client import ApiError, BaseClient


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
