---
name: {SKILL_NAME}
description: >-
  {One or two sentences: what this skill does, when to use it, and which
  slash prefixes / keywords trigger it (e.g. /{SKILL_NAME}_*).}
disable-model-invocation: true
---

# {SKILL_NAME}

## When to use

Use for {domain}. Trigger phrases: "{example phrase}", `/{SKILL_NAME}_*`.

## Working directory

Placeholders changed by `/meta-skills` at copy time (NAME => {PLACEHOLDER}):

IS_GLOBAL => {IS_GLOBAL}
TYPE_OF_AI_TOOLS => {TYPE_OF_AI_TOOLS}
SKILL_PATH => {SKILL_PATH}

Point SkillCred at the registered skill dir (credentials live in `{SKILL_PATH}/`):

```bash
export CURRENT_SKILL_DIRECTORY="{SKILL_PATH}"
~/.meta-skills/.venv/bin/python ~/.meta-skills/skills/<category>/…/{SKILL_NAME}/scripts/cli.py env
```

Do **not** load `.env` via shell (`source`, `set -a`, `[ -f … ]`) — that is bash-specific and breaks on Windows / PowerShell / other shells. Let Python resolve credentials through `SkillCred` / `env_load.py` (cross-platform).

Library scripts: `~/.meta-skills/skills/<category>/…/{SKILL_NAME}/`.

## Slash commands

### {Group}

| Slash | CLI | Description |
|-------|-----|-------------|
| `/{SKILL_NAME}_{action}` | `python scripts/cli.py {action} …` | {Short description} |

## How to run

1. Set `CURRENT_SKILL_DIRECTORY` to `{SKILL_PATH}`, then run from the library path above.
2. Run the CLI for the slash command; parse JSON output when available.
3. First Python run from the **library** skill folder: `cd ~/.meta-skills/skills/<category>/…/{SKILL_NAME} && ~/.meta-skills/install.sh pip init .`

## Notes

- Confirm with the user before **destructive** or **side-effect** actions (send, delete, write, …).
- Credentials live next to the registered `SKILL.md` (`$CURRENT_SKILL_DIRECTORY`); resolve with `from common.skill_cred import SkillCred`.
- Never commit `.env`, tokens, or client secrets.
