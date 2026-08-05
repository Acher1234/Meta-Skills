---
name: bitwarden
description: >-
  Bitwarden vault via the bw CLI — read, create, edit and delete items, folders
  and attachments, plus Bitwarden Send. Secrets are masked unless --reveal is
  passed. Use when the user mentions Bitwarden, a vault, a stored password,
  TOTP, a Send, or invokes /bitwarden_*.
disable-model-invocation: true
---

### TO COPY

# bitwarden

Per-workspace registration slice. Credentials live in `{SKILL_PATH}/.env`.

## Working directory

Placeholders changed by `/meta-skills` at copy time (NAME => {PLACEHOLDER}):

IS_GLOBAL => {IS_GLOBAL}
TYPE_OF_AI_TOOLS => {TYPE_OF_AI_TOOLS}
SKILL_PATH => {SKILL_PATH}

```bash
export CURRENT_SKILL_DIRECTORY="{SKILL_PATH}"
~/.meta-skills/.venv/bin/python ~/.meta-skills/skills/security/bitwarden/scripts/cli.py env
```

Never print a vault secret unless the user explicitly asked for its value — prefer
`--clipboard` or `--output` over `--reveal`. On `"code": "locked"`, do not retry: hand
the user the `unlock_command` from the response and wait.

Full command reference: `~/.meta-skills/skills/security/bitwarden/SKILL.md`

##### END TO COPY

# bitwarden

Python CLI wrapping the [Bitwarden CLI](https://bitwarden.com/help/cli/) (`bw`): JSON
output, cached session key, and **secrets masked by default**. See [`ORIGIN.md`](ORIGIN.md).

## When to use

Trigger phrases: "what's my password for X", "store this credential in Bitwarden",
"create a login item", "generate a password and save it", "share this file securely",
"list my vault items", `/bitwarden_*`.

## Install — three commands

```bash
cd ~/.meta-skills/skills/security/bitwarden
~/.meta-skills/install.sh pip init . && ~/.meta-skills/install.sh npm init .
CURRENT_SKILL_DIRECTORY="{SKILL_PATH}" python scripts/cli.py setup
```

`setup` is **user-run** (it prompts): it asks for the server and the auth method, writes
`{SKILL_PATH}/.env` at `chmod 600`, optionally arms the macOS keychain, then verifies by
unlocking. Nothing to copy by hand. `python scripts/cli.py env` reports the resolved
state at any time.

## Credentials — SkillCred `.env`

Two auth methods, pick one — `env` reports which via `auth_method`.

| Variable | Notes |
|----------|-------|
| `BW_EMAIL` | Method A — account email. `bw login` then also unlocks, so no API key needed |
| `BW_CLIENTID` / `BW_CLIENTSECRET` | Method B — personal API key. Web Vault → **Account settings → Security → Keys** ([docs](https://bitwarden.com/help/personal-api-key/)) |
| `BW_SERVER` | Default `https://vault.bitwarden.com` (EU: `https://vault.bitwarden.eu`, or self-hosted) |
| `BW_SESSION_TTL` | Minutes a cached session stays valid (default `15`) |
| `BW_PASSWORD_KEYCHAIN_SERVICE` | Optional, macOS — enables silent unlock (set by `keychain set`) |
| `BW_PASSWORD_KEYCHAIN_ACCOUNT` | Optional — defaults to `BW_EMAIL` |
| `NODE_EXTRA_CA_CERTS` | Only behind a TLS-inspecting proxy or a private CA |

Method A is simpler; method B is the one that survives **two-step login**, which blocks a
non-interactive `bw login`. On `"code": "twofa_required"`, tell the user to re-run
`unlock --code 123456` (add `--method email|yubikey` if not an authenticator app) or to
switch to an API key. Never put credentials in chat.

## Session model — read this before anything else

Vault data needs a session key, and producing it always requires the **master password**.

1. **Method A** — `bw login <email>` returns the session key directly: login and unlock
   are one gesture, done by `unlock`.
   **Method B** — the API key logs in automatically but does **not** unlock; `unlock`
   is still needed.
2. `unlock` caches the session key in `{SKILL_PATH}/.bw_session` (`chmod 600`, expires
   after `BW_SESSION_TTL`).
3. Every other command reuses that cache.

Where the master password comes from depends on the setup:

- **macOS keychain configured** (`keychain set`) — unlocking is silent and automatic,
  including from the agent. Nothing else to do.
- **Otherwise** — only the user can type it. On `"code": "locked"`, do not retry: give
  them the `unlock_command` from the response, wait, then resume.

An expired session behaves the same way: the cache self-destructs and the next command
either re-unlocks from the keychain or reports `locked`.

Login state is isolated per registered skill dir (`BITWARDENCLI_APPDATA_DIR`), so
different workspaces can hold different accounts.

## Session

| Slash | CLI |
|-------|-----|
| `/bitwarden_setup` | `python scripts/cli.py setup` — **user-run**, guided first-run config |
| `/bitwarden_env` | `python scripts/cli.py env` |
| `/bitwarden_status` | `python scripts/cli.py status` |
| `/bitwarden_login` | `python scripts/cli.py login` — API key only |
| `/bitwarden_unlock` | `python scripts/cli.py unlock [--code 123456 --method authenticator\|email\|yubikey]` — **user-run**, prompts for the master password |
| `/bitwarden_keychain` | `python scripts/cli.py keychain set\|status\|clear` — **`set` is user-run** (macOS prompts on a terminal) |
| `/bitwarden_lock` | `python scripts/cli.py lock` |
| `/bitwarden_logout` | `python scripts/cli.py logout` |
| `/bitwarden_sync` | `python scripts/cli.py sync [--last]` |

## Read

| Slash | CLI |
|-------|-----|
| `/bitwarden_list` | `python scripts/cli.py list items\|folders\|collections\|organizations\|org-collections\|org-members [--search X] [--folderid ID] [--collectionid ID] [--organizationid ID] [--url URL] [--trash] [--archived] [--limit N]` |
| `/bitwarden_get` | `python scripts/cli.py get item\|username\|password\|uri\|totp\|notes\|exposed\|folder\|collection\|organization\|org-collection\|template\|fingerprint <id-or-search>` |
| `/bitwarden_get_attachment` | `python scripts/cli.py get-attachment FILENAME --itemid ID --output DIR/` |
| `/bitwarden_generate` | `python scripts/cli.py generate [--length 20 -ulns] [--passphrase --words 4 --separator -]` |

`get` accepts a search term instead of an id, but returns `"code": "ambiguous"` when
several objects match — narrow the term, or use `list --search` first to pick an id from
the names.

A **folder** is private to the user; a **collection** belongs to an organization and is
visible to everyone with access to it. Say which one is meant before creating either.

### Getting a secret out

Secrets come back as `{"masked": true, "length": …, "sha256_8": …}`. Three ways to
obtain the real value, in order of preference:

- `--clipboard` — copies it, prints nothing sensitive (best default for a human).
- `--output FILE` — writes it to a `chmod 600` file.
- `--reveal` — prints it in clear text, which lands in the chat transcript. Only when
  the user explicitly asked to see it.

## Write

| Slash | CLI |
|-------|-----|
| `/bitwarden_create_item` | `python scripts/cli.py create item --name X [--type login\|note\|card\|identity] [--username U] [--generate\|--password-stdin\|--password P] [--uri URL] [--totp SECRET] [--notes N] [--folderid ID] [--field k=v] [--hidden-field k=v]` |
| `/bitwarden_create_folder` | `python scripts/cli.py create folder --name X` |
| `/bitwarden_create_collection` | `python scripts/cli.py create org-collection --name X --organizationid ID [--external-id E] [--manage-user MEMBER_ID]` |
| `/bitwarden_create_attachment` | `python scripts/cli.py create attachment --file PATH --itemid ID` |
| `/bitwarden_edit_item` | `python scripts/cli.py edit item ID [--name X] [--username U] [--generate] [--totp S] [--uri URL] [--notes N]` |
| `/bitwarden_edit_folder` | `python scripts/cli.py edit folder ID --name X` |
| `/bitwarden_delete` | `python scripts/cli.py delete item\|attachment\|folder\|org-collection ID --yes [--itemid ID] [--permanent --i-understand-this-is-irreversible]` |
| `/bitwarden_restore` | `python scripts/cli.py restore ID` |

Prefer `--generate` over `--password`: it never puts the secret in the command line.
Item payloads are piped through stdin for the same reason.

## Send ([docs](https://bitwarden.com/help/send-cli/))

| Slash | CLI |
|-------|-----|
| `/bitwarden_send_create` | `python scripts/cli.py send create --name X (--text "…" [--hidden] \| --file PATH) [--days 7] [--max-access N] [--password P]` |
| `/bitwarden_send_list` | `python scripts/cli.py send list` |
| `/bitwarden_send_get` | `python scripts/cli.py send get ID` |
| `/bitwarden_send_delete` | `python scripts/cli.py send delete ID --yes` |
| `/bitwarden_receive` | `python scripts/cli.py receive URL [--password P]` |

`send create` returns the `accessUrl` — that URL **is** the secret, treat it as one.

## Important — Safety rules

- Confirm with the user before every `create`, `edit`, `delete`, and `send`.
- `delete` needs `--yes`; `delete --permanent` also needs
  `--i-understand-this-is-irreversible` and destroys the item for good (no trash).
- Never echo a revealed secret back in a summary, and never write one into a file the
  user did not ask for.
- Never commit `.env`, `.bw_session`, or `.bw-appdata/`.
- A cached session key decrypts the whole vault: run `lock` when finished with a
  sensitive batch.

## How to run

1. Export `CURRENT_SKILL_DIRECTORY` → registered skill dir (holds `.env`).
2. `cd ~/.meta-skills/skills/security/bitwarden`, run `python scripts/cli.py …`.
3. stdout is JSON; errors are `{"error": true, "code": …, "message": …}` with exit 1.

Error codes worth branching on: `locked` (ask the user to run `unlock_command`),
`missing_credentials` (`.env` incomplete — point at `setup`), `twofa_required` (re-run
`unlock --code`), `ambiguous` (the search term matches several objects — narrow it),
`binary_missing` (run `install.sh npm init .`), `no_tty` (the command needs a real
terminal, hand it to the user), `confirmation_required` (a destructive flag is missing),
`server_mismatch` (`logout` first).
