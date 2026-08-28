---
name: logo-dev-finder
description: >-
  Search logo.dev by company name or domain and download logos into a folder.
  Use when the user asks for a company logo, logo.dev search, or invokes
  /logo-dev-finder_*.
disable-model-invocation: true
---

### TO COPY

# logo-dev-finder

Per-workspace registration slice. Credentials live in `{SKILL_PATH}/.env`.

## Working directory

Placeholders changed by `/meta-skills` at copy time (NAME => {PLACEHOLDER}):

IS_GLOBAL => {IS_GLOBAL}
TYPE_OF_AI_TOOLS => {TYPE_OF_AI_TOOLS}
SKILL_PATH => {SKILL_PATH}

```bash
export CURRENT_SKILL_DIRECTORY="{SKILL_PATH}"
~/.meta-skills/.venv/bin/python ~/.meta-skills/skills/design/logo.dev-finder/scripts/cli.py env
```

##### END TO COPY

# logo-dev-finder

Search [logo.dev](https://www.logo.dev/docs/api-reference/introduction) by company name or domain, then download each logo into a folder.

## When to use

Trigger phrases: "find this logo", "logo.dev", "download company logos", "logo for this domain", `/logo-dev-finder_*`.

`skill_env.py` loads `.env` via SkillCred — do not `source` it in the shell. `CURRENT_SKILL_DIRECTORY` is the only required export.

Prefer `~/.meta-skills/.venv/bin/python` from `~/.meta-skills/skills/design/logo.dev-finder/`.

## Credentials — SkillCred `.env`

`.env` is next to the **registered** skill, resolved by `SkillCred("logo-dev-finder", [".env"])`.

| Variable | Notes |
|----------|--------|
| `API_KEY` | logo.dev **secret** key (`sk_…`). `Authorization: Bearer` on `api.logo.dev` |

```bash
cp ~/.meta-skills/skills/design/logo.dev-finder/.env.example "{SKILL_PATH}/.env"
# edit API_KEY
python scripts/cli.py env
```

## Slash commands

`{QUERY}` is a company name **or** a domain. **If the user did not specify a folder, ask for `{FOLDER}` before running.** Confirm before `--force`.

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/design/logo.dev-finder`.

| Slash | CLI | Description |
|-------|-----|-------------|
| `/logo-dev-finder_env` | `python scripts/cli.py env` | Validate `.env` (no network) |
| `/logo-dev-finder_search` | `python scripts/cli.py search {QUERY} --folder {FOLDER}` | Search and download logos |

Placeholders: `{QUERY}`, `{FOLDER}`. Optional: `--force`.

## How to run

1. `export CURRENT_SKILL_DIRECTORY="{SKILL_PATH}"` then `cd ~/.meta-skills/skills/design/logo.dev-finder`.
2. Ensure `.env` exists next to the registered skill; `/logo-dev-finder_env`.
3. Map `/logo-dev-finder_<…>` → `~/.meta-skills/.venv/bin/python scripts/cli.py …`; return JSON.

## Notes

- Ask for `{FOLDER}` when it is missing. Confirm before `--force` overwrite.
- Never commit `.env` or echo `API_KEY`.
- Docs: [logo.dev API](https://www.logo.dev/docs/api-reference/introduction).
