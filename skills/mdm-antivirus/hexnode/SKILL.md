---
name: hexnode
description: >-
  Hexnode MDM REST API via a Python CLI (API key auth). Devices, users, apps,
  policies, and device groups against https://<portal>.hexnodemdm.com/api/v1.
  Use when the user mentions Hexnode, Hexnode MDM/UEM, or invokes /hexnode_*.
disable-model-invocation: true
---

# hexnode

Hexnode MDM API CLI ([developers](https://www.hexnode.com/mobile-device-management/developers/)).

## When to use

Trigger phrases: "Hexnode devices", "Hexnode users", "Hexnode apps",
"Hexnode policies", "device groups", "enrollment request", "Hexnode MDM API",
`/hexnode_*`.

## Working directory

Placeholders changed by `/meta-skills` at copy time (NAME => {PLACEHOLDER}):

IS_GLOBAL => {IS_GLOBAL}
TYPE_OF_AI_TOOLS => {TYPE_OF_AI_TOOLS}
SKILL_PATH => {SKILL_PATH}

```bash
export CURRENT_SKILL_DIRECTORY="{SKILL_PATH}"
export IS_GLOBAL="{IS_GLOBAL}"
export TYPE_OF_AI_TOOLS="{TYPE_OF_AI_TOOLS}"
[ -f "$HOME/.meta-skills/.env" ] && set -a && . "$HOME/.meta-skills/.env" && set +a
[ -f "{SKILL_PATH}/.env" ] && set -a && . "{SKILL_PATH}/.env" && set +a
cd ~/.meta-skills/skills/mdm-antivirus/hexnode
```

Prefer `~/.meta-skills/.venv/bin/python`. First deps:
`cd ~/.meta-skills/skills/mdm-antivirus/hexnode && ~/.meta-skills/install.sh pip init .`

## Credentials — SkillCred `.env`

You can authenticate with the Hexnode MDM API by providing your secret API key with each request. The API uses HTTP Basic Authentication to receive your API key. It will look for your API key in the Authentication field.

Prior to authentication, enable API access in Hexnode MDM (**Admin → API → Enable API Access**), then copy the key.

| Variable | Notes |
|----------|--------|
| `HEXNODE_API_KEY` | Required — secret API key from Admin → API |
| `HEXNODE_PORTAL` | Portal subdomain → `https://<portal>.hexnodemdm.com/api/v1` |
| `HEXNODE_BASE_URL` | Optional full API base (overrides portal) |

```bash
cp ~/.meta-skills/skills/mdm-antivirus/hexnode/.env.example "{SKILL_PATH}/.env"
# edit HEXNODE_API_KEY + HEXNODE_PORTAL
python scripts/cli.py env
```

Working request format (same as Hexnode curl examples): send the **raw API key** as the `Authorization` header value (no `Bearer` / `Basic` prefix). Docs: [Authentication](https://www.hexnode.com/mobile-device-management/developers/setting-up-an-api/authentication/) · [Retrieve API Key](https://www.hexnode.com/mobile-device-management/developers/setting-up-an-api/retrieve-api-key/).

## Devices ([API docs](https://www.hexnode.com/mobile-device-management/developers/devices/))

Implemented in `scripts/devices.py` (`DevicesClient` extends `HexnodeClient`).

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/hexnode_env` | `python scripts/cli.py env` | Validate `.env` (no network) |
| `/hexnode_devices_list` | `python scripts/cli.py devices list [--platform ios\|android\|windows] [--active\|--inactive] [--order-by asc\|desc] [--page N] [--per-page N]` | [`GET /devices/`](https://www.hexnode.com/mobile-device-management/developers/devices/list-all-devices/) |
| `/hexnode_devices_get` | `python scripts/cli.py devices get DEVICE_ID` | [`GET /devices/{id}/`](https://www.hexnode.com/mobile-device-management/developers/devices/retrieve-device-details/) |
| `/hexnode_devices_policies` | `python scripts/cli.py devices policies DEVICE_ID [--page N] [--per-page N]` | [`GET /devices/{id}/policies/`](https://www.hexnode.com/mobile-device-management/developers/devices/list-device-policies/) |
| `/hexnode_devices_applications` | `python scripts/cli.py devices applications DEVICE_ID [--page N] [--per-page N]` | [`GET /devices/{id}/applications/`](https://www.hexnode.com/mobile-device-management/developers/devices/list-all-applications/) |
| `/hexnode_devices_locations` | `python scripts/cli.py devices locations DEVICE_ID [--page N] [--per-page N]` | [`GET /devices/{id}/locations/`](https://www.hexnode.com/mobile-device-management/developers/devices/list-device-locations/) |

`--per-page` max is **250** on list / applications.

## Users ([API docs](https://www.hexnode.com/mobile-device-management/developers/users/))

Implemented in `scripts/users.py` (`UsersClient` extends `HexnodeClient`).

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/hexnode_users_list` | `python scripts/cli.py users list [--order-by asc\|desc] [--user-type local\|"active directory"] [--enrollment-status enrolled\|unenrolled] [--page N] [--per-page N]` | [`GET /users/`](https://www.hexnode.com/mobile-device-management/developers/users/list-all-users/) |
| `/hexnode_users_create` | `python scripts/cli.py users create --name NAME --email EMAIL [--phoneno N] [--password P]` | [`POST /users/`](https://www.hexnode.com/mobile-device-management/developers/users/create-user/) |
| `/hexnode_users_get` | `python scripts/cli.py users get USER_ID` | [`GET /users/{id}/`](https://www.hexnode.com/mobile-device-management/developers/users/retrieve-user-details/) |
| `/hexnode_users_edit` | `python scripts/cli.py users edit USER_ID --name NAME --email EMAIL [--phoneno N] [--password P]` | [`PUT /users/{id}/`](https://www.hexnode.com/mobile-device-management/developers/users/edit-user/) |
| `/hexnode_users_delete` | `python scripts/cli.py users delete USER_ID` | [`DELETE /users/{id}/`](https://www.hexnode.com/mobile-device-management/developers/users/delete-user/) |
| `/hexnode_users_send-enrollment` | `python scripts/cli.py users send-enrollment USER_ID --ownership personal\|corporate\|user_choice` | [`POST /users/{id}/send_request/`](https://www.hexnode.com/mobile-device-management/developers/users/send-enrollment-request/) |

**Destructive:** `users delete` also **disenrolls all devices** for that user — confirm with the user first. Prefer confirming `create` / `edit` / `send-enrollment` before running.

## Applications ([API docs](https://www.hexnode.com/mobile-device-management/developers/applications/))

Implemented in `scripts/application.py` (`ApplicationClient` extends `HexnodeClient`). Portal app catalog (distinct from `devices applications`, which lists apps *on a device*).

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/hexnode_apps_list` | `python scripts/cli.py apps list [--app-type store\|web\|enterprise] [--platform ios\|android] [--order-by asc\|desc] [--page N] [--per-page N]` | [`GET /applications/`](https://www.hexnode.com/mobile-device-management/developers/applications/list-all-apps/) |
| `/hexnode_apps_search` | `python scripts/cli.py apps search --keyword NAME --platform ios\|android [--country us]` | [`GET /applications/searchapp/`](https://www.hexnode.com/mobile-device-management/developers/applications/search-app/) |
| `/hexnode_apps_add` | `python scripts/cli.py apps add --file app.json` / `apps add --name N --app-type store\|web --platform ios\|android --category C --icon URL …` | [`POST /applications/`](https://www.hexnode.com/mobile-device-management/developers/applications/add-app-to-list/) |
| `/hexnode_apps_get` | `python scripts/cli.py apps get APP_ID` | [`GET /applications/{id}/`](https://www.hexnode.com/mobile-device-management/developers/applications/retrieve-app-details/) |

For `apps add`, prefer `--file` when iOS store fields (`appstore_id`, `bundle_size`, …) are required. Confirm before adding.

## Policies ([API docs](https://www.hexnode.com/mobile-device-management/developers/policies/))

Implemented in `scripts/policy.py` (`PolicyClient` extends `HexnodeClient`). Portal policies (distinct from `devices policies`, which lists policies *on a device*). Platform payload schemas: [`references/policy-platforms.md`](references/policy-platforms.md).

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/hexnode_policies_list` | `python scripts/cli.py policies list [--page N] [--per-page N]` | [`GET /policy/`](https://www.hexnode.com/mobile-device-management/developers/policies/list-policies/) |
| `/hexnode_policies_create` | `python scripts/cli.py policies create --file policy.json` / `policies create --name NAME [--description D]` | [`POST /policy/`](https://www.hexnode.com/mobile-device-management/developers/policies/create-policy/) |
| `/hexnode_policies_get` | `python scripts/cli.py policies get POLICY_ID` | [`GET /policy/{id}/`](https://www.hexnode.com/mobile-device-management/developers/policies/policy-details/) |
| `/hexnode_policies_edit` | `python scripts/cli.py policies edit POLICY_ID --file policy.json` | [`PUT /policy/{id}/`](https://www.hexnode.com/mobile-device-management/developers/policies/edit-policy/) |
| `/hexnode_policies_archive` | `python scripts/cli.py policies archive POLICY_ID` | [`DELETE /policy/{id}/`](https://www.hexnode.com/mobile-device-management/developers/policies/archive-policy/) |

Platform dictionaries for create/edit (not separate CLI commands): [iOS](https://www.hexnode.com/mobile-device-management/developers/policies/ios-policies/), [Android](https://www.hexnode.com/mobile-device-management/developers/policies/android-policies/), [macOS](https://www.hexnode.com/mobile-device-management/developers/policies/macos-policies/), [Windows](https://www.hexnode.com/mobile-device-management/developers/policies/windows-policies/). Prefer `--file` for full payloads. **Archive** dissociates the policy from all devices — confirm first.

## Device groups ([API docs](https://www.hexnode.com/mobile-device-management/developers/device-groups/))

Implemented in `scripts/device_groups.py` (`DeviceGroupsClient` extends `HexnodeClient`).

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/hexnode_device-groups_list` | `python scripts/cli.py device-groups list [--page N] [--per-page N]` | [`GET /devicegroups/`](https://www.hexnode.com/mobile-device-management/developers/device-groups/list-device-groups/) |
| `/hexnode_device-groups_create` | `python scripts/cli.py device-groups create --name NAME --description D [--device ID …]` | [`POST /devicegroups/`](https://www.hexnode.com/mobile-device-management/developers/device-groups/create-device-group/) |
| `/hexnode_device-groups_get` | `python scripts/cli.py device-groups get GROUP_ID` | [`GET /devicegroups/{id}/`](https://www.hexnode.com/mobile-device-management/developers/device-groups/retrieve-device-group-details/) |
| `/hexnode_device-groups_update` | `python scripts/cli.py device-groups update GROUP_ID --name NAME --description D [--device ID …]` | [`PUT /devicegroups/{id}/`](https://www.hexnode.com/mobile-device-management/developers/device-groups/update-device-group/) |
| `/hexnode_device-groups_add-remove` | `python scripts/cli.py device-groups add-remove GROUP_ID [--add ID …] [--remove ID …]` | [`POST /devicegroups/{id}/`](https://www.hexnode.com/mobile-device-management/developers/device-groups/add-remove-devices/) |
| `/hexnode_device-groups_delete` | `python scripts/cli.py device-groups delete GROUP_ID` | [`DELETE /devicegroups/{id}/`](https://www.hexnode.com/mobile-device-management/developers/device-groups/delete-device-group/) |

Confirm before `create` / `update` / `add-remove` / `delete`.

## How to run

1. `export CURRENT_SKILL_DIRECTORY="{SKILL_PATH}"` then `cd ~/.meta-skills/skills/mdm-antivirus/hexnode`.
2. Ensure `.env` exists next to the registered skill; `/hexnode_env`.
3. Map `/hexnode_<…>` → `~/.meta-skills/.venv/bin/python scripts/cli.py …`; return JSON.
4. Never log or echo `HEXNODE_API_KEY`.

### Examples

```bash
python scripts/cli.py env
python scripts/cli.py devices list --per-page 50
python scripts/cli.py devices get 5
python scripts/cli.py devices policies 5
python scripts/cli.py devices applications 5 --per-page 100
python scripts/cli.py devices locations 5
python scripts/cli.py users list --per-page 50
python scripts/cli.py users get 1
python scripts/cli.py users create --name "Neil" --email neil@example.com
python scripts/cli.py users edit 13 --name "Neil" --email neil@example.com
python scripts/cli.py users send-enrollment 13 --ownership personal
# confirm before: python scripts/cli.py users delete 13
python scripts/cli.py apps list --app-type store --platform ios
python scripts/cli.py apps search --keyword youtube --platform android --country us
python scripts/cli.py apps get 1
# python scripts/cli.py apps add --file app.json
python scripts/cli.py policies list
python scripts/cli.py policies get 129
python scripts/cli.py policies create --file policy.json
python scripts/cli.py policies edit 129 --file policy.json
# confirm before: python scripts/cli.py policies archive 129
python scripts/cli.py device-groups list
python scripts/cli.py device-groups get 1
python scripts/cli.py device-groups create --name "iOS devices" --description "Group of iOS devices" --device 1 --device 2
python scripts/cli.py device-groups add-remove 1 --add 3 --remove 2
# confirm before: python scripts/cli.py device-groups delete 1
```

## Notes

- Confirm with the user before destructive Hexnode actions (wipe, lock, …) if those are added later.
- Credentials live next to the registered `SKILL.md` (`$CURRENT_SKILL_DIRECTORY`).
- Never commit `.env` or API keys.
