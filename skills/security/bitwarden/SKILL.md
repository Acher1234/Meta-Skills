---
name: bitwarden
description: >-
  Bitwarden / Vaultwarden vault via the bw CLI — session, vault read/write,
  Send. Self-hosted, API key login then unlock from .env. Use when the user
  mentions Bitwarden, a vault password, TOTP, a Send, or invokes /bitwarden_*.
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
eval "$(~/.meta-skills/.venv/bin/python ~/.meta-skills/skills/security/bitwarden/scripts/session.py)"
```

Never print a vault secret unless the user asked — prefer clipboard / file.

##### END TO COPY

# bitwarden — Command Index

Router to `bw` command domains. References live in `command.md/` and `exemple.md/`
under the **shared library** (`~/.meta-skills/skills/security/bitwarden/`).

## Prerequisites

This skill documents the official **`bw` CLI** ([docs](https://bitwarden.com/help/cli/)).
Pin it once in the skill dir:

```bash
cd ~/.meta-skills/skills/security/bitwarden
~/.meta-skills/install.sh npm init .
```

Credentials in `{SKILL_PATH}/.env` (`BW_SERVER`, `BW_CLIENTID`, `BW_CLIENTSECRET`,
`BW_PASSWORD`). Then unlock and call `bw` / `$BW` directly:

```bash
export CURRENT_SKILL_DIRECTORY="{SKILL_PATH}"
eval "$(~/.meta-skills/.venv/bin/python ~/.meta-skills/skills/security/bitwarden/scripts/session.py)"
$BW list items --search github
```

`session.py` loads `.env`, runs `bw login --apikey` only if `unauthenticated`, then
`bw unlock --passwordenv BW_PASSWORD`, and prints shell exports (`BW_SESSION`, `BW`, …).

## When to use

Trigger phrases: "what's my password for X", "store this in Bitwarden", "create a login",
"Bitwarden Send", `/bitwarden_*`.

## bitwarden-session

Connect once: status, API-key login, unlock, lock, logout, sync.
Use before any vault or Send write/read that needs decryption.

Commands → `~/.meta-skills/skills/security/bitwarden/command.md/bitwarden-session.command.md`
Examples → `~/.meta-skills/skills/security/bitwarden/exemple.md/bitwarden-session.exemple.md`

---

## bitwarden-vault-read

List / get items, folders, attachments, generate passwords.
Secrets: prefer clipboard; print only if the user asked.

Commands → `~/.meta-skills/skills/security/bitwarden/command.md/bitwarden-vault-read.command.md`
Examples → `~/.meta-skills/skills/security/bitwarden/exemple.md/bitwarden-vault-read.exemple.md`

---

## bitwarden-vault-write

Create / edit / delete / restore items, folders, attachments, collections.
Confirm with the user before every write.

Commands → `~/.meta-skills/skills/security/bitwarden/command.md/bitwarden-vault-write.command.md`
Examples → `~/.meta-skills/skills/security/bitwarden/exemple.md/bitwarden-vault-write.exemple.md`

---

## bitwarden-send

Ephemeral Bitwarden Send (text/file). The `accessUrl` is the secret.

Commands → `~/.meta-skills/skills/security/bitwarden/command.md/bitwarden-send.command.md`
Examples → `~/.meta-skills/skills/security/bitwarden/exemple.md/bitwarden-send.exemple.md`

---

## Safety

- Confirm before create / edit / delete / send.
- Never commit `.env` or `.bw-appdata/`.
- Do not echo secrets into chat unless the user asked.
