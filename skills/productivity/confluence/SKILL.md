---
name: confluence
description: >-
  Confluence via confluence-cli (read, search, create, update, move, delete,
  attachments, comments). Shared npm CLI; per-workspace .env via SkillCred.
  Always load credentials with `python scripts/cli.py env` / `env-check` first.
  Use when the user mentions Confluence, wiki pages, CQL search, or
  /confluence_*.
disable-model-invocation: true
---

# confluence

## When to use

Use for Atlassian Confluence page/space work. Triggers: "Confluence page", "wiki",
"search Confluence", "create page", `/confluence_*`.

Confirm with the user before **write** ops (create, update, move, delete, upload).
Prefer `CONFLUENCE_READ_ONLY=true` for research-only agents.

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
cd ~/.meta-skills/skills/productivity/confluence/scripts
```

Prefer `~/.meta-skills/.venv/bin/python`. First deps:
`cd ~/.meta-skills/skills/productivity/confluence && ~/.meta-skills/install.sh pip init .`

Register = copy **only** `SKILL.md` (+ `.env.example` → `.env`). Do **not** copy the full tree.

## Install CLI (once per machine)

```bash
npm install -g confluence-cli
confluence --version
```

## Credentials — SkillCred `.env` (required)

`.env` is next to the **registered** skill, resolved by
`SkillCred("confluence", [".env"])` under `$CURRENT_SKILL_DIRECTORY`
(via `scripts/env_load.py`).

**Agents must load the `.env` through this skill’s Python CLI before any
`confluence …` call** — do not assume credentials are already in the shell.

| Variable | Example |
|----------|---------|
| `CONFLUENCE_DOMAIN` | `company.atlassian.net` |
| `CONFLUENCE_API_PATH` | `/wiki/rest/api` (Cloud) or `/rest/api` (Server/DC) |
| `CONFLUENCE_AUTH_TYPE` | `basic` or `bearer` |
| `CONFLUENCE_EMAIL` | `user@company.com` (required when `basic`) |
| `CONFLUENCE_API_TOKEN` | API token / PAT |

Optional: `CONFLUENCE_PROFILE`, `CONFLUENCE_READ_ONLY=true`, `CONFLUENCE_FORCE_CLOUD`,
`CONFLUENCE_LINK_STYLE`, `CONFLUENCE_ENV_PATH` (absolute override path to a `.env`).

```bash
cp ~/.meta-skills/skills/productivity/confluence/.env.example "{SKILL_PATH}/.env"
# edit CONFLUENCE_DOMAIN / CONFLUENCE_EMAIL / CONFLUENCE_API_TOKEN / …
```

## How to run (agent)

Python is **only** for resolving / checking / exporting the `.env`. All Confluence
work uses **`confluence-cli` directly** after env is loaded.

```bash
export CURRENT_SKILL_DIRECTORY="{SKILL_PATH}"
cd ~/.meta-skills/skills/productivity/confluence/scripts

# 1) Required — load + verify .env + confluence-cli on PATH
python cli.py env-check
# or just load: python cli.py env

# 2) Export credentials into the shell (pick one)
eval "$(python cli.py print-exports)"
# or: set -a && source "$(python cli.py env-path)" && set +a

# 3) Run confluence-cli
confluence read 123456789 --format markdown
confluence search "deployment pipeline" --limit 20
```

If `env-check` already succeeded in this shell and vars were exported, you may
call `confluence …` directly. Otherwise run `env` / `env-check` / `print-exports`
again — **never skip the load step on a fresh shell**.

## Slash commands

Map `/confluence_<action>` → `confluence <action> …` (**after** env is loaded).
Use `python cli.py env` / `env-check` / `env-path` / `print-exports` for setup only.

### Setup (Python — load `.env` first)

| Slash | CLI | Description |
|-------|-----|-------------|
| `/confluence_env` | `python cli.py env` | Load `.env` into process env; show paths |
| `/confluence_env-check` | `python cli.py env-check` | Verify required keys + `confluence` on PATH |
| `/confluence_env-path` | `python cli.py env-path` | Print `.env` path |
| `/confluence_print-exports` | `python cli.py print-exports` | `export` lines for `eval` |

### Read / search (`confluence`)

| Slash | CLI | Description |
|-------|-----|-------------|
| `/confluence_read` | `confluence read <pageId\|URL> [--format markdown\|text\|storage\|html]` | Read page |
| `/confluence_info` | `confluence info <pageId> [--format json]` | Metadata |
| `/confluence_find` | `confluence find "Title" [--space KEY]` | Find by title |
| `/confluence_search` | `confluence search "query" [--limit N] [--cql]` | Search / CQL |
| `/confluence_spaces` | `confluence spaces` | List spaces |
| `/confluence_children` | `confluence children <pageId> [--recursive] [--format json\|tree]` | Children |
| `/confluence_comments` | `confluence comments <pageId> [--format json] [--all]` | List comments |
| `/confluence_attachments` | `confluence attachments <pageId> [--download] [--dest DIR]` | List / download |
| `/confluence_export` | `confluence export <pageId> [--format markdown] [--dest DIR]` | Export |

### Write (`confluence` — confirm first; `--yes` on deletes)

| Slash | CLI | Description |
|-------|-----|-------------|
| `/confluence_create` | `confluence create "Title" SPACE [--file path\|--content …] [--format markdown]` | Create page |
| `/confluence_create-child` | `confluence create-child "Title" <parentId> [--file …] [--format markdown]` | Child page |
| `/confluence_update` | `confluence update <pageId> [--title …] [--file …] [--format markdown]` | Update |
| `/confluence_move` | `confluence move <pageId> <newParentId> [--title …]` | Move (same space) |
| `/confluence_delete` | `confluence delete <pageId> --yes` | Trash page |
| `/confluence_edit` | `confluence edit <pageId> [--output page.xml]` | Fetch storage XML |
| `/confluence_comment` | `confluence comment <pageId> --content "…" [--location footer]` | Add comment |
| `/confluence_comment-delete` | `confluence comment-delete <id> --yes` | Delete comment |
| `/confluence_attachment-upload` | `confluence attachment-upload <pageId> --file path [--replace]` | Upload |
| `/confluence_attachment-delete` | `confluence attachment-delete <pageId> <attId> --yes` | Delete attachment |
| `/confluence_copy-tree` | `confluence copy-tree <src> <parent> [title] [--dry-run]` | Copy page tree |

### Profiles / misc

| Slash | CLI | Description |
|-------|-----|-------------|
| `/confluence_profile_list` | `confluence profile list` | List profiles |
| `/confluence_profile_use` | `confluence profile use <name>` | Switch profile |
| `/confluence_convert` | `confluence convert -i in.md -o out.xml --input-format markdown --output-format storage` | Offline convert |
| `/confluence_api` | `confluence api <endpoint> …` | Raw REST helper |

Global: `confluence --profile staging <command>`.

## Page IDs

Accept numeric IDs or Confluence URLs (`?pageId=`, `/pages/<id>/…`). Prefer ID or
`/pages/<id>` over `/display/<space>/<title>`.

## List all pages in a space

**Do not** paginate with `confluence search … --start N` (or `content/search?…&start=N`)
on Confluence Cloud — the offset is often ignored → same page of results forever →
infinite loops / huge delays.

Use the content list API and bump `start` while `len(results) == limit`:

```bash
confluence api "content?spaceKey=KEY&type=page&limit=50&start=0"
confluence api "content?spaceKey=KEY&type=page&limit=50&start=50"
# … until fewer than 50 results
```

If you must use `content/search`, follow `_links.next` (cursor), never a bare `start`.

## Agent tips

- **Always** run `python cli.py env` or `env-check` (then `print-exports`) before
  `confluence …` when credentials are not already in the process env.
- Destructive commands: always pass `--yes`.
- Prefer `--format markdown` for agent text; `--format json` for parsing.
- Read-only agents: `CONFLUENCE_READ_ONLY=true` in the workspace `.env`.
- Folders have no body — use `info`, not `read`/`edit`.
- **Never** use `confluence search --start` to crawl a whole space — see
  [List all pages in a space](#list-all-pages-in-a-space).
- Full reference: `confluence --help` / [confluence-cli](https://www.npmjs.com/package/confluence-cli).

## Files

```
~/.meta-skills/skills/productivity/confluence/
├── SKILL.md
├── ORIGIN.md
├── .env.example
├── requirements.txt
└── scripts/
    ├── cli.py          # env / env-check / env-path / print-exports
    └── env_load.py     # SkillCred + dotenv
```
