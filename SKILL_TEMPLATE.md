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

Before `cd`, export the local skill directory and source `.env` files (shared library, then this skill dir):

```bash
export CURRENT_SKILL_DIRECTORY="{SKILL_PATH}"
export IS_GLOBAL="{IS_GLOBAL}"
export TYPE_OF_AI_TOOLS="{TYPE_OF_AI_TOOLS}"
[ -f "$HOME/.meta-skills/.env" ] && set -a && . "$HOME/.meta-skills/.env" && set +a
[ -f "{SKILL_PATH}/.env" ] && set -a && . "{SKILL_PATH}/.env" && set +a
cd "{SKILL_PATH}"
```

Always `cd` into `{SKILL_PATH}` before running scripts. Prefer the shared interpreter: `~/.meta-skills/.venv/bin/python` (run from the library skill tree when scripts live under `~/.meta-skills/skills/<category>/…/{SKILL_NAME}/`).

## Slash commands

### {Group}

| Slash | CLI | Description |
|-------|-----|-------------|
| `/{SKILL_NAME}_{action}` | `python scripts/cli.py {action} …` | {Short description} |

## How to run

1. `cd` to the [working directory](#working-directory) that exists on this machine (after exports).
2. Run the CLI for the slash command; parse JSON output when available.
3. First Python run from the **library** skill folder: `cd ~/.meta-skills/skills/<category>/…/{SKILL_NAME} && ~/.meta-skills/install.sh pip init .`

## Notes

- Confirm with the user before **destructive** or **side-effect** actions (send, delete, write, …).
- Credentials live next to the registered `SKILL.md` (`$CURRENT_SKILL_DIRECTORY`); resolve with `from common.skill_cred import SkillCred`.
- Never commit `.env`, tokens, or client secrets.
