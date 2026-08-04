# eset-automation — Commands

API docs: [Automation](https://help.eset.com/eset_connect/en-US/automation.html)

Targets are device and/or device-group UUIDs (from Device Management). Omitted `--expire-time` runs the task ASAP.

### Task lifecycle (`tasks`)

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/eset_tasks_list` | `python cli.py tasks list [--page-size N] [--page-token T]` | `GET /v1/device_tasks` |
| `/eset_tasks_get` | `python cli.py tasks get TASK_UUID` | `GET /v1/device_tasks/{taskUuid}` |
| `/eset_tasks_delete` | `python cli.py tasks delete TASK_UUID` | `DELETE /v1/device_tasks/{taskUuid}` |
| `/eset_tasks_runs` | `python cli.py tasks runs TASK_UUID [--page-size N]` | `GET /v1/device_tasks/{taskUuid}/runs` |
| `/eset_tasks_create` | `python cli.py tasks create --action NAME --device UUID [--params-file p.json]` / `--file body.json` | `POST /v1/device_tasks` |
| `/eset_tasks_update-targets` | `python cli.py tasks update-targets TASK_UUID --device UUID [--group UUID]` / `--file body.json` | `POST /v1/device_tasks/{taskUuid}:updateTaskTargets` |
| `/eset_tasks_update-triggers` | `python cli.py tasks update-triggers TASK_UUID --expire-time RFC3339` / `--file body.json` | `POST /v1/device_tasks/{taskUuid}:updateTaskTriggers` |

### Convenience builders

All accept `--device` / `--group` targets plus `--display-name`, `--description`, `--expire-time`.

| Slash | CLI | `task.action.name` |
|-------|-----|--------------------|
| `/eset_tasks_isolate` | `python cli.py tasks isolate --device UUID` | `StartNetworkIsolation` |
| `/eset_tasks_end-isolation` | `python cli.py tasks end-isolation --device UUID` | `EndNetworkIsolation` |
| `/eset_tasks_scan` | `python cli.py tasks scan --device UUID [--scan-profile InDepth] [--scan-target T] [--cleaning] [--shutdown] [--postpone V]` | `OnDemandScan` |
| `/eset_tasks_shutdown` | `python cli.py tasks shutdown --device UUID [--restart] [--postpone V]` | `ShutdownComputer` |
| `/eset_tasks_stop-managing` | `python cli.py tasks stop-managing --device UUID` | `StopManaging` |
| `/eset_tasks_av-remove` | `python cli.py tasks av-remove --device UUID` | `ThirdPartyAVRemove` |
| `/eset_tasks_os-update` | `python cli.py tasks os-update --device UUID [--accept-eula] [--optional-updates] [--allow-reboot] [--postpone V]` | `SystemUpdate` |
| `/eset_tasks_run-command` | `python cli.py tasks run-command --device UUID --command-line "call script.bat" [--current-directory DIR]` | `RunCommand` |
| `/eset_tasks_kill-process` | `python cli.py tasks kill-process --device UUID --pid N (--sha1 H \| --sha256 H)` | `KillProcessByPid` |
| `/eset_tasks_logout` | `python cli.py tasks logout --device UUID` | `LogOffComputerUser` |
| `/eset_tasks_vulnerability-scan` | `python cli.py tasks vulnerability-scan --device UUID` | `InitiateVulnerabilityScan` |
| `/eset_tasks_apply-patch` | `python cli.py tasks apply-patch --device UUID --application-uuid UUID` | `ApplyApplicationPatch` |

`--postpone` values: `Cannot` `OneHour` `ThreeHours` `FiveHours` `OneDay` `ThreeDays` `SevenDays` `FifteenDays` `TwentyDays` `ThirtyDays`.

For actions without a convenience flag, use `tasks create --action NAME --params-file params.json` or `--file body.json`.

**`RunCommand` + MFA:** HTTP 400/500 usually means MFA must be enabled for this action in ESET PROTECT — not a bad CLI payload.
