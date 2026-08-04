---
name: eset
description: >-
  Authenticate to ESET Connect (ESET Business Account IAM) and obtain an OAuth
  Bearer token via POST /oauth/token, using the bundled Python CLI (cli.py;
  OAuth logic in authentication.py). Shared CLI lib; per-workspace .env. Use when the user
  mentions ESET, ESET Connect, ESET PROTECT, an ESET API token, or invokes
  /eset_*.
disable-model-invocation: true
---

# eset

## When to use

Use to get an ESET Connect OAuth token (Bearer) for calling ESET Connect APIs.
Trigger phrases: "ESET token", "authenticate to ESET Connect", "ESET Business
Account login", `/eset_*`.

## Working directory

Placeholders changed by `/meta-skills` at copy time:

IS_GLOBAL => {IS_GLOBAL}
TYPE_OF_AI_TOOLS => {TYPE_OF_AI_TOOLS}
SKILL_PATH => {SKILL_PATH}

Point SkillCred at the registered skill dir (credentials live in `{SKILL_PATH}/.env`):

```bash
export CURRENT_SKILL_DIRECTORY="{SKILL_PATH}"
~/.meta-skills/.venv/bin/python ~/.meta-skills/skills/mdm-antivirus/eset/script/cli.py env-check
```

`env_load.py` loads `.env` via SkillCred — do not `source` it in the shell. `CURRENT_SKILL_DIRECTORY` is the only required export.

Prefer `~/.meta-skills/.venv/bin/python`. First deps:
`cd ~/.meta-skills/skills/mdm-antivirus/eset && ~/.meta-skills/install.sh pip init .`

## Credentials — SkillCred `.env`

`.env` is next to the **registered** skill, resolved by `SkillCred("eset", [".env"])`
under `$CURRENT_SKILL_DIRECTORY` (via `script/env_load.py`).

| Variable | Notes |
|----------|--------|
| `ESET_URL` | Region base **without** `/oauth/token` (`eu`/`us`/… or full URL) |
| `ESET_USERNAME` | IAM username |
| `ESET_PASSWORD` | IAM password |
| `ESET_ACCESS_TOKEN` | Written by `cli.py token` / first API call — reloaded automatically |
| `ESET_REFRESH_TOKEN` | Written on login — used to refresh without re-asking password |

```bash
cp ~/.meta-skills/skills/mdm-antivirus/eset/.env.example "{SKILL_PATH}/.env"
# edit ESET_URL / ESET_USERNAME / ESET_PASSWORD
python cli.py token          # POST /oauth/token → saves tokens into .env
python cli.py env-check
```

## Authentication

[`POST /oauth/token`](https://help.eset.com/eset_connect/en-US/authentication_oauth_token_post.html)
lives in `authentication.py` (`TOKEN_PATH = "/oauth/token"`).

Token resolution (inside each API request via `BaseClient`):

1. `--token` if passed (one-shot override)
2. else `ESET_ACCESS_TOKEN` from `.env`
3. else refresh via `ESET_REFRESH_TOKEN`
4. else password grant with `ESET_USERNAME` / `ESET_PASSWORD`

On **401**, the client forces a new token (refresh → password) and **retries the request once**.
Successful exchanges upsert `ESET_ACCESS_TOKEN` / `ESET_REFRESH_TOKEN` into the SkillCred `.env`.

## Slash commands

| Slash | CLI | Description |
|-------|-----|-------------|
| `/eset_env-check` | `python cli.py env-check` | Validate `.env` + show resolved paths (no network) |
| `/eset_token` | `python cli.py token` | Get a Bearer token (password grant) |
| `/eset_token_refresh` | `python cli.py token --refresh REFRESH_TOKEN` | Refresh with a refresh_token |
| `/eset_token_print-request` | `python cli.py token --print-request` | Dry run: print request (secrets masked) |
| `/eset_env-path` | `python cli.py env-check` | Print the resolved SkillCred `.env` path |

### Device Management ([API docs](https://help.eset.com/eset_connect/en-US/device_management.html))

These auto-acquire a token from the `.env` credentials (or pass `--token`, or set `ESET_ACCESS_TOKEN`). The API base URL is `ESET_API_URL` or `https://<region>.automation.eset.systems`.

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/eset_groups_list` | `python cli.py groups list [--page-size N] [--page-token T]` | `GET /v1/device_groups` |
| `/eset_groups_devices` | `python cli.py groups devices GROUP_UUID [--page-size N]` | `GET /v1/device_groups/{groupUuid}/devices` |
| `/eset_devices_list` | `python cli.py devices list [--page-size N] [--page-token T]` | `GET /v1/devices` |
| `/eset_devices_get` | `python cli.py devices get DEVICE_UUID` | `GET /v1/devices/{deviceUuid}` |
| `/eset_devices_move` | `python cli.py devices move DEVICE_UUID --group GROUP_UUID` | `POST /v1/devices/{deviceUuid}:move` |
| `/eset_devices_rename` | `python cli.py devices rename DEVICE_UUID --name NAME` | `POST /v1/devices/{deviceUuid}:rename` |
| `/eset_devices_batch-get` | `python cli.py devices batch-get UUID [UUID …]` | `GET /v1/devices:batchGet` |
| `/eset_devices_batch-import` | `python cli.py devices batch-import --file devices.json` | `POST /v1/devices:batchImport` |

### Application Management ([API docs](https://help.eset.com/eset_connect/en-US/application_management.html))

Executable (application) control. Same token handling as above; the gateway is a **different host** — `ESET_APP_URL` or `https://<region>.application-management.eset.systems`.

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/eset_executables_list` | `python cli.py executables list [--page-size N] [--page-token T]` | `GET /v1/executables` |
| `/eset_executables_get` | `python cli.py executables get EXECUTABLE_UUID` | `GET /v1/executables/{executableUuid}` |
| `/eset_executables_block` | `python cli.py executables block EXECUTABLE_UUID` | `POST /v1/executables/{executableUuid}:block` |
| `/eset_executables_unblock` | `python cli.py executables unblock EXECUTABLE_UUID` | `POST /v1/executables/{executableUuid}:unblock` |

### Asset Management ([API docs](https://help.eset.com/eset_connect/en-US/asset_management.html))

Group lifecycle (create / delete / move / rename). Same token handling as above; the gateway is `ESET_ASSET_URL` or `https://<region>.automation.eset.systems` (same host as Device Management — these are the same groups).

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/eset_assets_create` | `python cli.py assets create --name NAME [--parent PARENT_UUID]` | `POST /v1/groups` |
| `/eset_assets_delete` | `python cli.py assets delete GROUP_UUID` | `DELETE /v1/groups/{groupUuid}` |
| `/eset_assets_move` | `python cli.py assets move GROUP_UUID --parent PARENT_UUID` | `POST /v1/groups/{groupUuid}:move` |
| `/eset_assets_rename` | `python cli.py assets rename GROUP_UUID --name NAME` | `POST /v1/groups/{groupUuid}:rename` |

### Policy Management ([API docs](https://help.eset.com/eset_connect/en-US/policy_management.html))

Policies and policy assignments (API **v2**). Same token handling; gateway is `ESET_POLICY_URL` or `https://<region>.automation.eset.systems`.

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/eset_policies_list` | `python cli.py policies list [--page-size N] [--page-token T]` | `GET /v2/policies` |
| `/eset_policies_get` | `python cli.py policies get POLICY_UUID` | `GET /v2/policies/{policyUuid}` |
| `/eset_policies_create` | `python cli.py policies create --file policy.json` | `POST /v2/policies` |
| `/eset_policies_delete` | `python cli.py policies delete POLICY_UUID` | `DELETE /v2/policies/{policyUuid}` |
| `/eset_policy-assignments_list` | `python cli.py policy-assignments list [--page-size N]` | `GET /v2/policy-assignments` |
| `/eset_policy-assignments_get` | `python cli.py policy-assignments get ASSIGNMENT_UUID` | `GET /v2/policy-assignments/{assignmentUuid}` |
| `/eset_policy-assignments_assign` | `python cli.py policy-assignments assign --file assignment.json` | `POST /v2/policy-assignments` |
| `/eset_policy-assignments_unassign` | `python cli.py policy-assignments unassign ASSIGNMENT_UUID` | `DELETE /v2/policy-assignments/{assignmentUuid}` |
| `/eset_policy-assignments_update-ranking` | `python cli.py policy-assignments update-ranking ASSIGNMENT_UUID --ranking N` | `POST /v2/policy-assignments/{assignmentUuid}:updateRanking` |

### Incident Management ([API docs](https://help.eset.com/eset_connect/en-US/incident_management.html))

Detections, EDR rules/exclusions and incidents. Same token handling; gateway is a **different host** — `ESET_INCIDENT_URL` or `https://<region>.incident-management.eset.systems`. v1 detections work for ESET PROTECT; all other calls need an ESET Inspect subscription (v2 detections list is ESET Cloud Office Security).

#### Detections + DetectionGroups

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/eset_detections_list` | `python cli.py detections list [--version v1\|v2] [--device UUID] [--start-time T] [--end-time T] [--page-size N]` | `GET /{version}/detections` |
| `/eset_detections_get` | `python cli.py detections get DETECTION_UUID [--version v1\|v2]` | `GET /{version}/detections/{detectionUuid}` |
| `/eset_detections_resolve` | `python cli.py detections resolve DETECTION_UUID [--note TEXT]` | `POST /v2/detections/{detectionUuid}:resolve` |
| `/eset_detections_batch-get` | `python cli.py detections batch-get UUID [UUID …]` | `POST /v2/detections:batchGet` |
| `/eset_detection-groups_list` | `python cli.py detection-groups list [--page-size N]` | `GET /v2/detection-groups` |
| `/eset_detection-groups_get` | `python cli.py detection-groups get GROUP_UUID` | `GET /v2/detection-groups/{detectionGroupUuid}` |
| `/eset_detection-groups_resolve` | `python cli.py detection-groups resolve GROUP_UUID [--note TEXT]` | `POST /v2/detection-groups/{detectionGroupUuid}:resolve` |
| `/eset_detection-groups_search` | `python cli.py detection-groups search [--filter "resolved eq 0"] [--total-size]` | `POST /v2/detection-groups:search` |

#### EDR rules + exclusions

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/eset_edr-rules_list` | `python cli.py edr-rules list [--page-size N]` | `GET /v2/edr-rules` |
| `/eset_edr-rules_create` | `python cli.py edr-rules create --file rule.json` | `POST /v2/edr-rules` |
| `/eset_edr-rules_get` | `python cli.py edr-rules get RULE_UUID` | `GET /v2/edr-rules/{ruleUuid}` |
| `/eset_edr-rules_delete` | `python cli.py edr-rules delete RULE_UUID` | `DELETE /v2/edr-rules/{ruleUuid}` |
| `/eset_edr-rules_enable` | `python cli.py edr-rules enable RULE_UUID` | `POST /v2/edr-rules/{ruleUuid}:enable` |
| `/eset_edr-rules_disable` | `python cli.py edr-rules disable RULE_UUID` | `POST /v2/edr-rules/{ruleUuid}:disable` |
| `/eset_edr-rules_update-definition` | `python cli.py edr-rules update-definition RULE_UUID --xml-definition XML` | `POST /v2/edr-rules/{ruleUuid}:updateDefinition` |
| `/eset_edr-exclusions_list` | `python cli.py edr-exclusions list [--page-size N]` | `GET /v2/edr-rule-exclusions` |
| `/eset_edr-exclusions_create` | `python cli.py edr-exclusions create --file exclusion.json` | `POST /v2/edr-rule-exclusions` |
| `/eset_edr-exclusions_get` | `python cli.py edr-exclusions get EXCLUSION_UUID` | `GET /v2/edr-rule-exclusions/{exclusionUuid}` |
| `/eset_edr-exclusions_delete` | `python cli.py edr-exclusions delete EXCLUSION_UUID` | `DELETE /v2/edr-rule-exclusions/{exclusionUuid}` |
| `/eset_edr-exclusions_update-definition` | `python cli.py edr-exclusions update-definition EXCLUSION_UUID --xml-definition XML` | `POST /v2/edr-rule-exclusions/{exclusionUuid}:updateDefinition` |

#### Incidents + IncidentComments

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/eset_incidents_list` | `python cli.py incidents list [--page-size N]` | `GET /v2/incidents` |
| `/eset_incidents_get` | `python cli.py incidents get INCIDENT_UUID` | `GET /v2/incidents/{incidentUuid}` |
| `/eset_incidents_update-attributes` | `python cli.py incidents update-attributes INCIDENT_UUID [--assignee UUID] [--description D] [--name N] [--severity S]` | `POST /v2/incidents/{incidentUuid}/basic-attributes:update` |
| `/eset_incidents_close` | `python cli.py incidents close INCIDENT_UUID [--reason R] [--comment TEXT]` | `POST /v2/incidents/{incidentUuid}:close` |
| `/eset_incidents_reopen` | `python cli.py incidents reopen INCIDENT_UUID` | `POST /v2/incidents/{incidentUuid}:reopen` |
| `/eset_incident-comments_list` | `python cli.py incident-comments list INCIDENT_UUID [--page-size N]` | `GET /v2/incidents/{incidentUuid}/comments` |
| `/eset_incident-comments_create` | `python cli.py incident-comments create INCIDENT_UUID --text TEXT` | `POST /v2/incidents/{incidentUuid}/comments` |
| `/eset_incident-comments_get` | `python cli.py incident-comments get INCIDENT_UUID COMMENT_UUID` | `GET /v2/incidents/{incidentUuid}/comments/{commentUuid}` |
| `/eset_incident-comments_delete` | `python cli.py incident-comments delete INCIDENT_UUID COMMENT_UUID` | `DELETE /v2/incidents/{incidentUuid}/comments/{commentUuid}` |
| `/eset_incident-comments_update-text` | `python cli.py incident-comments update-text INCIDENT_UUID COMMENT_UUID --text TEXT` | `POST /v2/incidents/{incidentUuid}/comments/{commentUuid}/text:update` |

### Automation — Device tasks ([API docs](https://help.eset.com/eset_connect/en-US/automation.html))

Trigger actions on target devices ("Device tasks", called "Client tasks" in the ESET PROTECT Web Console). Same token handling; gateway is `ESET_AUTOMATION_URL` or `https://<region>.automation.eset.systems`. Targets are device and/or device-group UUIDs (from Device Management); an omitted `--expire-time` triggers the task as soon as possible.

Task lifecycle:

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/eset_tasks_list` | `python cli.py tasks list [--page-size N] [--page-token T]` | `GET /v1/device_tasks` |
| `/eset_tasks_get` | `python cli.py tasks get TASK_UUID` | `GET /v1/device_tasks/{taskUuid}` |
| `/eset_tasks_delete` | `python cli.py tasks delete TASK_UUID` | `DELETE /v1/device_tasks/{taskUuid}` |
| `/eset_tasks_runs` | `python cli.py tasks runs TASK_UUID [--page-size N]` | `GET /v1/device_tasks/{taskUuid}/runs` |
| `/eset_tasks_create` | `python cli.py tasks create --action NAME --device UUID [--params-file p.json]` / `--file body.json` | `POST /v1/device_tasks` |
| `/eset_tasks_update-targets` | `python cli.py tasks update-targets TASK_UUID --device UUID [--group UUID]` / `--file body.json` | `POST /v1/device_tasks/{taskUuid}:updateTaskTargets` |
| `/eset_tasks_update-triggers` | `python cli.py tasks update-triggers TASK_UUID --expire-time RFC3339` / `--file body.json` | `POST /v1/device_tasks/{taskUuid}:updateTaskTriggers` |

Convenience builders (one per documented `task.action.name`; all accept `--device`/`--group` targets plus `--display-name` / `--description` / `--expire-time`):

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

`--postpone` values: `Cannot` `OneHour` `ThreeHours` `FiveHours` `OneDay` `ThreeDays` `SevenDays` `FifteenDays` `TwentyDays` `ThirtyDays`. For any action not covered by a flag (or to send raw params), use `tasks create --action NAME --params-file params.json` or a full `--file body.json`.

**`RunCommand` + MFA:** if `tasks run-command` returns **HTTP 400 or 500**, the tenant usually needs **MFA enabled** for this action in ESET PROTECT / Business Account. Fix MFA first — do not treat it as a bad CLI payload.

### Patch Management ([API docs](https://help.eset.com/eset_connect/en-US/patch_management.html))

List pending patches (unpatched apps / OS / packages) per device. Gateway: `ESET_PATCH_URL` or `https://<region>.patch-management.eset.systems`. Apply uses the **Automation** gateway (`ApplyApplicationPatch`), same as `/eset_tasks_apply-patch`.

| Slash | CLI | Notes |
|-------|-----|--------|
| `/eset_patches_list` | `python cli.py patches list [--device UUID] [--group UUID] [--patch-type PATCH_TYPE_APPLICATION\|…] [--page-size N]` | pending patches |
| `/eset_patches_recent` | `python cli.py patches recent` | recent app patching details |
| `/eset_patches_details` | `python cli.py patches details [--page-size N]` | process details |
| `/eset_patches_apply` | `python cli.py patches apply --device UUID --application-uuid UUID [--display-name N] [--expire-time RFC3339]` | Automation `ApplyApplicationPatch` |

**UUID mapping:** from `patches list`, use **`devices[].uuid`** as `--application-uuid` (same value as `applicationUuid` in `patches recent` / `patches details`). It is *not* the device UUID. Prefer `--device` on list (unfiltered can timeout) and `--expire-time` on apply. Confirm target app + device with the user before applying. Equivalent: `/eset_tasks_apply-patch`.

## How to run

1. `export CURRENT_SKILL_DIRECTORY="{SKILL_PATH}"` then `cd ~/.meta-skills/skills/mdm-antivirus/eset/script`.
2. Ensure `.env` exists next to the registered skill; `/eset_env-check`.
3. Map `/eset_<…>` → `~/.meta-skills/.venv/bin/python cli.py …`; return JSON.
4. Tokens are stored in `.env` — do not log or echo them.

### Examples

```bash
python cli.py env-check
python cli.py token                 # login + save ESET_ACCESS_TOKEN / ESET_REFRESH_TOKEN
python cli.py token --token-only
python cli.py token --print-request
python cli.py token --refresh "<refresh_token>"
python cli.py devices list          # reuses ESET_ACCESS_TOKEN from .env
```

## Notes

- `authentication.py` owns `TOKEN_PATH=/oauth/token`, token exchange, and `.env` persistence.
- `env_load.py` resolves the SkillCred `.env` (`CURRENT_SKILL_DIRECTORY`).
- API clients keep only implemented endpoints; gateways: `automation` / `application-management` / `incident-management` / `patch-management`.
- Never commit `.env` or echo tokens.
- `202` = request cached; retry with `response-id`.
- Docs: [POST /oauth/token](https://help.eset.com/eset_connect/en-US/authentication_oauth_token_post.html).
