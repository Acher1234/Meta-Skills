---
name: google-workspace
description: >-
  Gmail, Calendar, Drive, Docs, Sheets, Contacts, and Google Chat via OAuth and
  the bundled Python CLI (scripts/google_api.py). Use when the user mentions
  Gmail, Google Calendar, Drive, Sheets, Docs, Chat, Workspace, or invokes
  /google-workspace_*.
disable-model-invocation: true
---

# google-workspace

## When to use

Use for Google Workspace API work. Trigger phrases: "check my email", "create calendar event", "upload to Drive", "update Sheet", "Google Docs", "Google Chat", "Chat space", `/google-workspace_gmail_*`, `/google-workspace_calendar_*`, `/google-workspace_chat_*`.

## Working directory

Placeholders changed by `/meta-skills` at copy time (NAME => {PLACEHOLDER}):

IS_GLOBAL => {IS_GLOBAL}
TYPE_OF_AI_TOOLS => {TYPE_OF_AI_TOOLS}
SKILL_PATH => {SKILL_PATH}

Before `cd`, export the local skill directory and source `.env` files (shared library, then this skill dir):

```bash
export CURRENT_SKILL_DIRECTORY="{SKILL_PATH}"
export IS_GLOBAL="{IS_GLOBAL}"
export TYPE_OF_AI_TOOLS="{TYPE_OF_AI_TOOLS}"
[ -f "$HOME/.meta-skills/.env" ] && set -a && . "$HOME/.meta-skills/.env" && set +a
[ -f "{SKILL_PATH}/.env" ] && set -a && . "{SKILL_PATH}/.env" && set +a
cd "{SKILL_PATH}"
```

Always `cd` into `{SKILL_PATH}` before running scripts. Prefer the shared interpreter: `~/.meta-skills/.venv/bin/python` (run from the library skill tree when scripts live there).
## Slash commands

### Setup

| Slash | CLI | Description |
|-------|-----|-------------|
| `/google-workspace_setup_check` | `python scripts/setup.py --check` | Auth status |
| `/google-workspace_setup_client-secret` | `python scripts/setup.py --client-secret PATH` | Store OAuth client JSON |
| `/google-workspace_setup_auth-url` | `python scripts/setup.py --auth-url [--services …] --format json` | Print OAuth URL |
| `/google-workspace_setup_auth-code` | `python scripts/setup.py --auth-code CODE --format json` | Exchange code for token |
| `/google-workspace_setup_revoke` | `python scripts/setup.py --revoke` | Revoke + delete token |
| `/google-workspace_setup_install-deps` | `python scripts/setup.py --install-deps` | Install Python deps |

### Gmail

| Slash | CLI | Description |
|-------|-----|-------------|
| `/google-workspace_gmail_search` | `python scripts/google_api.py gmail search QUERY [--max N]` | Search messages |
| `/google-workspace_gmail_get` | `python scripts/google_api.py gmail get MESSAGE_ID` | Read message |
| `/google-workspace_gmail_send` | `python scripts/google_api.py gmail send --to … --subject … --body …` | Send email |
| `/google-workspace_gmail_reply` | `python scripts/google_api.py gmail reply MESSAGE_ID --body …` | Reply in thread |
| `/google-workspace_gmail_labels` | `python scripts/google_api.py gmail labels` | List labels |
| `/google-workspace_gmail_modify` | `python scripts/google_api.py gmail modify MESSAGE_ID [--add-labels …] [--remove-labels …]` | Change labels |

### Calendar

| Slash | CLI | Description |
|-------|-----|-------------|
| `/google-workspace_calendar_list` | `python scripts/google_api.py calendar list [--start …] [--end …]` | List events |
| `/google-workspace_calendar_create` | `python scripts/google_api.py calendar create --summary … --start … --end …` | Create event |
| `/google-workspace_calendar_delete` | `python scripts/google_api.py calendar delete EVENT_ID` | Delete event |

### Drive

| Slash | CLI | Description |
|-------|-----|-------------|
| `/google-workspace_drive_search` | `python scripts/google_api.py drive search QUERY [--max N]` | Search files |
| `/google-workspace_drive_get` | `python scripts/google_api.py drive get FILE_ID` | File metadata |
| `/google-workspace_drive_upload` | `python scripts/google_api.py drive upload PATH [--name …] [--parent ID]` | Upload |
| `/google-workspace_drive_download` | `python scripts/google_api.py drive download FILE_ID [--output PATH]` | Download / export |
| `/google-workspace_drive_create-folder` | `python scripts/google_api.py drive create-folder NAME [--parent ID]` | Create folder |
| `/google-workspace_drive_share` | `python scripts/google_api.py drive share FILE_ID --email … --role reader` | Share |
| `/google-workspace_drive_delete` | `python scripts/google_api.py drive delete FILE_ID [--permanent]` | Trash / delete |

### Contacts / Sheets / Docs

| Slash | CLI | Description |
|-------|-----|-------------|
| `/google-workspace_contacts_list` | `python scripts/google_api.py contacts list [--max N]` | List contacts |
| `/google-workspace_sheets_get` | `python scripts/google_api.py sheets get SHEET_ID RANGE` | Read range |
| `/google-workspace_sheets_update` | `python scripts/google_api.py sheets update SHEET_ID RANGE --values '[[…]]'` | Write range |
| `/google-workspace_sheets_append` | `python scripts/google_api.py sheets append SHEET_ID RANGE --values '[[…]]'` | Append rows |
| `/google-workspace_sheets_create` | `python scripts/google_api.py sheets create --title …` | New spreadsheet |
| `/google-workspace_docs_get` | `python scripts/google_api.py docs get DOC_ID` | Read doc |
| `/google-workspace_docs_create` | `python scripts/google_api.py docs create --title … [--body …]` | New doc |
| `/google-workspace_docs_append` | `python scripts/google_api.py docs append DOC_ID --text …` | Append text |

### Google Chat

| Slash | CLI | Description |
|-------|-----|-------------|
| `/google-workspace_chat_spaces` | `python scripts/google_api.py chat spaces [--max N] [--filter …]` | List spaces / teams |
| `/google-workspace_chat_get-space` | `python scripts/google_api.py chat get-space SPACE_ID` | Space details |
| `/google-workspace_chat_messages` | `python scripts/google_api.py chat messages SPACE_ID [--max N]` | List messages |
| `/google-workspace_chat_get-message` | `python scripts/google_api.py chat get-message SPACE_ID MESSAGE_ID` | Read one message |
| `/google-workspace_chat_send` | `python scripts/google_api.py chat send SPACE_ID --text …` | Send a message |

Named teams only: `--filter 'spaceType = "SPACE"'`. Enable the **Google Chat API** in Cloud Console before first use. After adding Chat scopes, re-run OAuth (`--auth-url` / `--auth-code`).

## How to run

1. `cd` to the [working directory](#working-directory) that exists on this machine.
2. First use: `/google-workspace_setup_check`. If not authenticated, run setup below.
3. Run the CLI for the slash command; parse JSON output.

### First-time OAuth (agent-driven)

1. Ask which services: `email`, `calendar`, `drive`, `sheets`, `docs`, `chat`, or `all`.
2. User creates a Desktop OAuth client in [Google Cloud Console](https://console.cloud.google.com/apis/credentials), enables the needed APIs (**including Google Chat API** if using Chat), downloads `client_secret.json`.
3. `python scripts/setup.py --client-secret /path/to/client_secret.json`
4. `python scripts/setup.py --auth-url --format json` → send `auth_url` to the user.
5. User pastes redirect URL or code → `python scripts/setup.py --auth-code "…" --format json`
6. `python scripts/setup.py --check` → expect `AUTHENTICATED`

Gmail search operators: see local `references/gmail-search-syntax.md` in this skill folder.

## Notes

- Confirm with the user before **send/reply**, **calendar create/delete**, **Drive share/delete**, **Sheets/Docs write**, or **Chat send**.
- Calendar times must be ISO 8601 with timezone offset or `Z`.
- Prefer trash (`drive delete`) over `--permanent`.
- Chat space ids accept bare ids (`AAAA`) or resource names (`spaces/AAAA`).
- Optional: if `gws` is on `PATH`, `google_api.py` may use it; same token file next to `SKILL.md`.
- Never commit `google_token.json` / `google_client_secret.json` / `google_oauth_pending.json`.
