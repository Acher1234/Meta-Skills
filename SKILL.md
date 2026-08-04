---
name: meta-skills
description: >-
  Install or update Meta-Skills into Cursor, Claude, Hermes, or OpenClaw. Clone/pull
  this repo into ~/.meta-skills (shared library), auto-detect the tool via TERMINAL_ENV
  / CLAUDECODE, ask target + scope, then copy (cp) chosen SKILL.md files — replacing
  {IS_GLOBAL}, {TYPE_OF_AI_TOOLS}, {SKILL_PATH} at copy time. External git skills clone
  ONCE into ~/.meta-skills/ext via `install.sh fetch`; each skill installs its OWN deps
  on first run via `install.sh pip init` / `npm init` into ~/.meta-skills/.venv. Use when
  installing/refreshing skills, adding a skill from a git URL, or running /meta-skills.
disable-model-invocation: true
---

# Meta-Skills — the skill installer (Cursor / Claude / Hermes / OpenClaw)

This skill **is** the installer. It manages a **single shared library and a single
shared Python/npm environment** on the machine, then registers chosen skills into
any tool. Nothing is re-cloned or re-installed per project.

> **Targets:** `cursor`, `claude`, `hermes`, `openclaw`.

## Core idea — shared library, shared env

Heavy things live **once** under `$META_SKILLS_HOME` (default `~/.meta-skills`); each
tool only gets the lightweight `SKILL.md`.

```
~/.meta-skills/                 shared library root (this repo, or $META_SKILLS_HOME)
├── install.sh                  installer helper (fetch / pip init / npm init)
├── meta-skill-common/          shared Python package (import as ``common`` — SkillCred, …)
├── skills/<category>/…/<name>/ built-in skills (nested by domain; CLI + SKILL.md)
├── ext/<name>/                 external skill repos, cloned ONCE
├── .venv/                      shared Python venv — every python skill reuses it
└── .env                        optional machine-wide secrets (sourced by skills)

        │ register = cp ONLY SKILL.md (with placeholders filled); credentials next to it ↓
~/.cursor/skills/<name>/{SKILL.md,.env}   (flat by skill basename; or ./.cursor/skills/<name>/)
```

**Hybrid model:** CLI code is **shared** under `~/.meta-skills/…`; credentials
(`.env` / `config.json` / tokens) are **per registered skill dir**, resolved by
[`meta-skill-common/skill_cred.py`](meta-skill-common/skill_cred.py) via
`SkillCred("<skill-name>", […filenames…])` and `$CURRENT_SKILL_DIRECTORY`.

## Hybrid model — shared CLI, local secrets (`common.skill_cred`)

Do **not** put secrets only under the shared library skill tree (that would force one
account for every project). Do **not** copy the full skill tree into Cursor/Hermes for
Python CLIs that follow this pattern — register `SKILL.md` only (unless a skill
explicitly documents a full-tree exception).

| Layer | Location | Shared? |
|-------|----------|---------|
| CLI / Python code | `~/.meta-skills/skills/<category>/…/<name>/` (or `ext/<name>/`) | **Yes** |
| Shared helpers | `~/.meta-skills/meta-skill-common/` (pip-installed as `common`) | **Yes** |
| Python deps | `~/.meta-skills/.venv` | **Yes** |
| Registered skill | `$DEST/<name>/SKILL.md` only | Lightweight discovery copy |
| Credentials | `$DEST/<name>/` (`.env`, tokens, `config.json`, …) | **No** — per workspace / profile |

**Skill directory variable (`CURRENT_SKILL_DIRECTORY`)** — must point at the directory
that contains the **registered** `SKILL.md` (where credentials live). Skills export it
in their Working directory section before running CLIs. `SkillCred` reads that env
(see `meta-skill-common/skill_cred.py`); if unset, it falls back to the process cwd.

**Authoring a skill that uses it:** start from [`SKILL_TEMPLATE.md`](SKILL_TEMPLATE.md) (or [`META_SKILL_TEMPLATE.md`](META_SKILL_TEMPLATE.md) for installer/hub skills like meta-jira); document provenance with [`ORIGIN_TEMPLATE.md`](ORIGIN_TEMPLATE.md)
(same Working directory + placeholder block as `skills/productivity/google/google-workspace/SKILL.md`).

```python
from common.skill_cred import SkillCred

token = SkillCred("my-skill", ["token.json", ".env"])
path = token.file_path()
```

```bash
# Register (Cursor project = different account per repo)
mkdir -p ./.cursor/skills/my-skill
# copy SKILL.md AND substitute placeholders (see below)
cp ~/.meta-skills/skills/my-skill/.env.example ./.cursor/skills/my-skill/.env

# Run CLI from the shared library; credentials resolve via CURRENT_SKILL_DIRECTORY
cd ~/.meta-skills/skills/my-skill
~/.meta-skills/.venv/bin/python scripts/cli.py …
```

## Copy-time placeholders (required)

When registering a skill, **do not** copy `SKILL.md` verbatim if it contains
`{…}` placeholders. After `cp`, replace them with the real values for that install:

```
IS_GLOBAL => {IS_GLOBAL}                 # TRUE if tool-global, else FALSE
TYPE_OF_AI_TOOLS => {TYPE_OF_AI_TOOLS}   # CURSOR / HERMES / OPENCLAW / CLAUDE
SKILL_PATH => {SKILL_PATH}               # absolute path of $DEST/<name> (dir of SKILL.md)
```

These show up in skill Working directory blocks, e.g.:

```bash
export CURRENT_SKILL_DIRECTORY="{SKILL_PATH}"
export IS_GLOBAL="{IS_GLOBAL}"
export TYPE_OF_AI_TOOLS="{TYPE_OF_AI_TOOLS}"
```

Substitute so the registered file has concrete values, for example:

```bash
export CURRENT_SKILL_DIRECTORY="/Users/you/.cursor/skills/google-workspace"
export IS_GLOBAL="TRUE"
export TYPE_OF_AI_TOOLS="CURSOR"
```

Always set `{SKILL_PATH}` to the **destination** directory that contains the copied
`SKILL.md` (not the shared library path under `~/.meta-skills/skills/…`).

## Helper script — [`install.sh`](install.sh) (3 commands)

`~/.meta-skills/install.sh` has **exactly three** commands. They only manage the
**shared** cache/env — nothing per project:

```bash
./install.sh fetch <git-url> [name]   # clone/pull → ~/.meta-skills/ext/<name>
./install.sh pip init [dir]           # shared venv + install meta-skill-common + <dir> deps
./install.sh npm init [dir]           # install <dir> node deps (shared skill dir)
```

- **Registering** a skill into a tool is a plain `cp` of `SKILL.md` **plus** placeholder
  substitution (see above / [Copy map](#copy-map-reference)).
- **Dependencies are each skill's job.** A skill calls `install.sh pip init .` /
  `install.sh npm init .` from its own folder on **first run** — installed once into
  the shared venv (`~/.meta-skills/.venv`), reused across projects.

## Targets & scopes

| Tool | Scope | Skills directory |
|------|-------|------------------|
| **cursor** | `global` | `~/.cursor/skills/<name>/` |
| **cursor** | `project` | `./.cursor/skills/<name>/` |
| **claude** | `global` | `~/.claude/skills/<name>/` |
| **claude** | `project` | `./.claude/skills/<name>/` |
| **hermes** | `all` | `~/.hermes/skills/<name>/` |
| **hermes** | `profile` | `${HERMES_HOME}/skills/<name>/` |
| **openclaw** | `global` | `~/.openclaw/skills/<name>/` *(WIP)* |
| **openclaw** | `project` | `./.openclaw/skills/<name>/` *(WIP)* |

## Critical — ask the user first

**Do not copy every skill blindly.** After clone/pull, resolve the tool (auto-detect
first), then ask in this order:

### 0) Auto-detect the tool

Detect from the **env vars the running agent sets** — not from the mere presence of
`~/.cursor` / `~/.claude` (that only means a tool is *installed*, not that it is *running*).
Check in order:

- **`$CLAUDECODE` or `$CLAUDE_CODE_ENTRYPOINT` set** → **Claude Code**.
- **`$TERMINAL_ENV` set (non-empty)** → **Hermes**. Skip to the Hermes profile scope (step 2).
- **`$CURSOR_AGENT` or `$CURSOR_TRACE_ID` set** (fallback: `$TERM_PROGRAM` = `vscode`/`cursor`) → **Cursor**.
- **None matched / several** → ask the tool question (step 1).
- **OpenClaw** is chosen explicitly (WIP).

### 1) Target tool (only if not auto-detected)

> Install skills for **Cursor**, **Claude**, **Hermes**, and/or **OpenClaw**? (one or several)

### 2) Scope

- **Cursor / Claude / OpenClaw** → **global** (`~/.<tool>/skills`) or **this project** (`./.<tool>/skills`).
- **Hermes** → **all profiles** (`~/.hermes/skills`) or **this profile** (`$HERMES_HOME/skills`; resolve `HERMES_HOME`, ask if unset).

### 3) Which skills

Ask for any of:
- **built-in** skills from Meta-Skills (nested under `skills/<category>/…/<name>/`, catalog below),
- an **external git URL** (any skill repo), or
- a **local path** to a skill folder.

Do **not** re-install `meta-skills` here — the installer itself is **global only**
(see [`INSTALL_PROMPT.md`](INSTALL_PROMPT.md)). When registering catalog skills, copy
only the skills the user asked for. Use the **catalog Folder** as `SRC` (not a flat `skills/<name>`).
Register into `$DEST/<name>/` using the skill **basename** (destinations stay flat).

### Skills catalog (show this to the user)

**Built-in (`skills/` — nested by category)**

#### Productivity

| # | Name | Folder | What it does |
|---|------|--------|--------------|
| 1 | `google-workspace` | `skills/productivity/google/google-workspace/` | Gmail, Calendar, Drive, Docs, Sheets, Contacts, Chat |
| 2 | `pc-report` | `skills/productivity/pc/pc-report/` | Host monitoring report (Linux / macOS / Windows) |
| 3 | `fathom` | `skills/productivity/video-conf/fathom/` | Fathom meetings, transcripts, AI summaries, action items |
| 4 | `jira` | `skills/productivity/jira/` | Installs Jira sub-skills (issue, search, agile, admin, …) + shared SkillCred `.env` |
| 5 | `confluence` | `skills/productivity/confluence/` | Confluence via confluence-cli + SkillCred `.env` (read/search/write) |

#### DevOps / DNS

| # | Name | Folder | What it does |
|---|------|--------|--------------|
| 1 | `godaddy` | `skills/devops/dns/godaddy/` | GoDaddy v3 discovery, owned domains, DNS CLI |

#### MDM & Antivirus

| # | Name | Folder | What it does |
|---|------|--------|--------------|
| 1 | `eset` | `skills/mdm-antivirus/eset/` | ESET Connect OAuth + device / policy / incident / automation / patch APIs |

#### Design

| # | Name | Folder | What it does |
|---|------|--------|--------------|
| 1 | `gif-creator` | `skills/design/gif-creator/` | Animated GIFs with Pillow (toss, frames → GIF, inspect) |

**External** — any git URL (cloned into `~/.meta-skills/ext/<name>`).

## Flow (do this)

```
# 0) Shared library — clone/pull into ~/.meta-skills
If ~/.meta-skills exists:  cd ~/.meta-skills && git pull
Else:                      git clone https://github.com/Acher1234/Meta-Skills.git ~/.meta-skills

# 1) Detect tool from the running agent's env: $CLAUDECODE → Claude; $TERMINAL_ENV → Hermes;
#    $CURSOR_AGENT/$CURSOR_TRACE_ID → Cursor. OpenClaw only when explicitly asked.
# 2) Ask scope (see table). For Hermes-profile, resolve HERMES_HOME.
# 3) Ask what to install: built-in name(s), external git URL, or local path.

# 4a) EXTERNAL git skill → fetch once:
SRC=$(cd ~/.meta-skills && ./install.sh fetch <git-url> [name])
# 4b) BUILT-IN: SRC=~/.meta-skills/<catalog Folder>  (e.g. skills/mdm-antivirus/eset)
#     <name> for DEST = basename of that folder (eset), NOT the category path
# 4c) LOCAL: SRC is the given path

# 5) Register = copy ONLY the requested skill's SKILL.md into each chosen tool/scope,
#    then substitute {IS_GLOBAL}, {TYPE_OF_AI_TOOLS}, {SKILL_PATH}:
mkdir -p "$DEST/<name>"
cp "$SRC/SKILL.md" "$DEST/<name>/SKILL.md"
# replace placeholders in "$DEST/<name>/SKILL.md":
#   {IS_GLOBAL}        → TRUE|FALSE
#   {TYPE_OF_AI_TOOLS} → CURSOR|HERMES|OPENCLAW|CLAUDE
#   {SKILL_PATH}       → absolute path of $DEST/<name>
# Do NOT also copy meta-skills — that installer is global-only (INSTALL_PROMPT.md).

# 6) Reload Cursor / Claude / OpenClaw, or reload the Hermes agent.
# NOTE: installer does NOT install skill deps. Each skill runs
#       ./install.sh pip init . (or npm init .) on first run → ~/.meta-skills/.venv
#       (pip init also installs meta-skill-common as importable ``common``).
```

## Examples

```bash
cd ~/.meta-skills

# Built-in → Hermes (all profiles); SRC is nested, DEST stays flat by basename
mkdir -p ~/.hermes/skills/google-workspace
cp ~/.meta-skills/skills/productivity/google/google-workspace/SKILL.md \
  ~/.hermes/skills/google-workspace/SKILL.md
# then substitute {IS_GLOBAL}=TRUE, {TYPE_OF_AI_TOOLS}=HERMES,
# {SKILL_PATH}=$HOME/.hermes/skills/google-workspace in that file

# External git skill → Claude (global): fetch once, then cp + substitute
SRC=$(./install.sh fetch https://github.com/some/cool-skill.git cool-skill)
mkdir -p ~/.claude/skills/cool-skill
cp "$SRC/SKILL.md" ~/.claude/skills/cool-skill/SKILL.md
# substitute placeholders → SKILL_PATH=$HOME/.claude/skills/cool-skill, …

# Same skill into Cursor (this project) — no re-clone
mkdir -p ./.cursor/skills/cool-skill
cp "$SRC/SKILL.md" ./.cursor/skills/cool-skill/SKILL.md
# substitute → IS_GLOBAL=FALSE, TYPE_OF_AI_TOOLS=CURSOR, SKILL_PATH=$PWD/.cursor/skills/cool-skill

# Skill installs ITS OWN deps on first run (shared venv + common):
./install.sh pip init "$SRC"
```

## Agent checklist

1. Clone/pull `~/.meta-skills`.
2. Detect tool from the running agent's env (`$CLAUDECODE` → Claude; `$TERMINAL_ENV` → Hermes; `$CURSOR_AGENT`/`$CURSOR_TRACE_ID` → Cursor). Ask if ambiguous / several.
3. Ask scope; resolve `HERMES_HOME` for Hermes-profile.
4. Ask what to install (built-in / external git URL / local path). Don't copy all by default.
5. External repo → `./install.sh fetch <url> [name]` (clone once into `ext/`).
6. **Register = `cp` the `SKILL.md`** into `$DEST/<name>/` for each chosen target; **replace** `{IS_GLOBAL}`, `{TYPE_OF_AI_TOOLS}`, `{SKILL_PATH}`. Do **not** also copy `meta-skills` (global-only via [`INSTALL_PROMPT.md`](INSTALL_PROMPT.md)).
7. **Dependencies are each skill's responsibility** — the skill runs `./install.sh pip init .` / `npm init .` on first run into `~/.meta-skills/.venv`.
8. Remind: reload the tool(s).

## Copy map (reference)

Pick `DEST` from the [Targets table](#targets--scopes). Then `mkdir -p "$DEST/<name>"`,
`cp` the `SKILL.md`, and **substitute placeholders**.

| Source (`~/.meta-skills/…`) | Target |
|-----------------------------|--------|
| `skills/<category>/…/<name>/SKILL.md` | `$DEST/<name>/SKILL.md` (flat basename) |
| `ext/<name>/SKILL.md` | `$DEST/<name>/SKILL.md` |
| `SKILL.md` (this installer) | **global only** — `~/.<tool>/skills/meta-skills/SKILL.md` via [`INSTALL_PROMPT.md`](INSTALL_PROMPT.md); never into project `./.<tool>/skills/` as a side effect of installing other skills |

## After install

- CLI working dirs stay under the nested catalog path (e.g. `~/.meta-skills/skills/mdm-antivirus/eset`) or `~/.meta-skills/ext/<name>`.
- Python skills should use `~/.meta-skills/.venv/bin/python` (has `common` installed).
- Credentials / tokens resolve under `$CURRENT_SKILL_DIRECTORY` (the registered skill dir).
- Re-run `/meta-skills` anytime to **pull + ask targets/skills again + re-register**.

## Notes

- Override the shared library location with `META_SKILLS_HOME` (default `~/.meta-skills`).
- Never write into `~/.cursor/skills-cursor/` (Cursor built-ins only).
- Register with `cp` (copy, not move). Prefer **per-skill** credentials next to the
  registered `SKILL.md`. Use [`meta-skill-common/skill_cred.py`](meta-skill-common/skill_cred.py)
  (`from common.skill_cred import SkillCred`) from Python CLIs.
- OpenClaw support is **in progress** — adjust its paths in the Targets table if needed.
- Repo: [Acher1234/Meta-Skills](https://github.com/Acher1234/Meta-Skills.git)
