---
name: folder-crypt
description: >-
  Encrypt or decrypt a folder with a password via a Python CLI (AES-256-GCM).
  Password and folder can be prompted, passed as args, or read from SkillCred
  .env. Use when the user asks to password-protect a folder, encrypt a directory,
  decrypt a .fcr archive, or invokes /folder-crypt_*.
disable-model-invocation: true
---

### TO COPY

# folder-crypt

Per-workspace registration slice. Credentials live in `{SKILL_PATH}/.env`.

## Working directory

Placeholders changed by `/meta-skills` at copy time (NAME => {PLACEHOLDER}):

IS_GLOBAL => {IS_GLOBAL}
TYPE_OF_AI_TOOLS => {TYPE_OF_AI_TOOLS}
SKILL_PATH => {SKILL_PATH}

```bash
export CURRENT_SKILL_DIRECTORY="{SKILL_PATH}"
~/.meta-skills/.venv/bin/python ~/.meta-skills/skills/security/folder-crypt/scripts/cli.py env
```

##### END TO COPY

# folder-crypt

Password-protect a folder: pack it as tar.gz, encrypt with **AES-256-GCM**
(key from PBKDF2-HMAC-SHA256). Decrypt restores the folder.

`skill_env.py` loads `.env` via SkillCred — do not `source` it in the shell.
`CURRENT_SKILL_DIRECTORY` is the only required export.

Prefer `~/.meta-skills/.venv/bin/python` from
`~/.meta-skills/skills/security/folder-crypt/`.

## When to use

Trigger phrases: "encrypt this folder", "password-protect a directory",
"decrypt the .fcr archive", `/folder-crypt_*`.

Confirm with the user before **encrypt --remove** (deletes the original folder).

## Prerequisites

```bash
cd ~/.meta-skills/skills/security/folder-crypt
~/.meta-skills/install.sh pip init .
```

## Credentials — SkillCred `.env` (optional)

Both keys are optional. When omitted, the CLI prompts (TTY) or requires flags.

| Variable | Notes |
|----------|--------|
| `FOLDER` | Default folder (encrypt) or folder / `.fcr` path (decrypt) |
| `PASSWORD` | Default password — never print it |

```bash
cp ~/.meta-skills/skills/security/folder-crypt/.env.example "{SKILL_PATH}/.env"
python scripts/cli.py env    # prints resolved .env path; PASSWORD is only "set"/"missing"
```

Interactive (no `.env`):

```bash
python scripts/cli.py encrypt
# Folder: /path/to/secret
# Password: ********
# Confirm password: ********
```

Non-interactive (`.env` or args):

```bash
python scripts/cli.py encrypt /path/to/secret
python scripts/cli.py decrypt /path/to/secret.fcr
python scripts/cli.py encrypt   # uses FOLDER + PASSWORD from .env
```

Prefer `.env` or the prompt over `--password` (avoids shell history).

## Slash commands

| Slash | CLI | Description |
|-------|-----|-------------|
| `/folder-crypt_env` | `python scripts/cli.py env` | Resolve `.env` (does not print the password) |
| `/folder-crypt_encrypt` | `python scripts/cli.py encrypt [FOLDER] [-o ARCHIVE.fcr] [--remove]` | Encrypt folder → `.fcr` |
| `/folder-crypt_decrypt` | `python scripts/cli.py decrypt [ARCHIVE.fcr\|FOLDER] [-o DEST]` | Decrypt `.fcr` → folder |

Default archive path: `<folder>.fcr` next to the folder. Default decrypt dest: archive name without `.fcr`.

Stdout is JSON.

## How to run

1. `export CURRENT_SKILL_DIRECTORY="{SKILL_PATH}"`
2. `cd ~/.meta-skills/skills/security/folder-crypt`
3. First run: `~/.meta-skills/install.sh pip init .`
4. `~/.meta-skills/.venv/bin/python scripts/cli.py …`

## Safety

- Confirm before `--remove`.
- Do not overwrite: encrypt fails if the `.fcr` exists; decrypt fails if the dest exists.
- Never commit `.env` or print `PASSWORD`.
- Never put the output `.fcr` inside the folder being encrypted.
- Wrong password → JSON error, no files written.
