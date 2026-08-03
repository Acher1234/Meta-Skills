---
name: meta-jira
description: >-
  Meta-skill that installs Jira sub-skills (issue, search, agile, admin, …) into
  Cursor / Claude / Hermes / OpenClaw. Ask scope (project vs global) and which
  sub-skills to register, then copy each sub-skill SKILL.md + shared credentials
  via SkillCred `.env`. Use when the user mentions Jira skills, /meta-jira,
  or wants to install jira-issue / jira-search / etc.
disable-model-invocation: true
---

# meta-jira

Installer meta-skill for Jira. It does **not** implement Jira APIs itself — it
registers one or more **sub-skills** from `sub_skills/` into the AI tool skills
directory, and shares one `.env` (Jira Cloud credentials) resolved by SkillCred.

Upstream docs live under `sub_skills/` (vendored from
[grandcamel/JIRA-Assistant-Skills](https://github.com/grandcamel/JIRA-Assistant-Skills.git)).
See [ORIGIN.md](ORIGIN.md).

## When to use

- User wants Jira automation skills installed or refreshed
- User asks for `/meta-jira`, "install jira skill", "add jira-issue", etc.
- User needs Jira Cloud credentials wired for those sub-skills

## Ask first (required)

Before copying anything, ask the user (same pattern as `/meta-skills`):

1. **Target tool** (if not obvious from the environment): `cursor` | `claude` | `hermes` | `openclaw`
2. **Scope** — where skills are installed:

| Tool | Scope | Skills directory (`$DEST`) |
|------|-------|----------------------------|
| cursor | **project** (local) | `./.cursor/skills/<name>/` |
| cursor | **global** | `~/.cursor/skills/<name>/` |
| claude | **project** (local) | `./.claude/skills/<name>/` |
| claude | **global** | `~/.claude/skills/<name>/` |
| hermes | **all** | `~/.hermes/skills/<name>/` |
| hermes | **profile** | `${HERMES_HOME}/skills/<name>/` |
| openclaw | **project** / **global** | `./.openclaw/skills/<name>/` or `~/.openclaw/skills/<name>/` |

3. **Which sub-skills** to install — do **not** install all by default. List the
   catalog below and let the user pick one, several, or all.

Also register **`meta-jira` itself** (this `SKILL.md`) into `$DEST/meta-jira/` so
credentials and the installer stay discoverable. Sub-skills install as **flat**
basenames under `$DEST` (e.g. `$DEST/jira-issue/`), same as other Meta-Skills.

## Sub-skills catalog

Source tree (library): `~/.meta-skills/skills/productivity/meta-jira/sub_skills/<id>/`

| Sub-skill | Goal |
|-----------|------|
| `jira-assistant` | Hub / router — picks the right specialized skill; does not call Jira itself |
| `jira-issue` | Core issue CRUD (create, read, update, delete tickets) |
| `jira-search` | Find issues with JQL; filters, export, discovery |
| `jira-lifecycle` | Workflow transitions and status / lifecycle changes |
| `jira-agile` | Epics, sprints, backlogs, story points |
| `jira-collaborate` | Comments, attachments, watchers, notifications |
| `jira-relationships` | Issue links, blockers, dependency analysis |
| `jira-bulk` | Bulk ops at scale (10+ issues): transition, assign, clone, delete |
| `jira-time` | Worklogs, time tracking, timesheets / reports |
| `jira-fields` | Custom field discovery and screen / field configuration |
| `jira-dev` | Git / PR / CI / smart-commit developer integration |
| `jira-jsm` | Jira Service Management — ITSM / ITIL workflows |
| `jira-admin` | Project & system admin: permissions, users, screens, workflows, automation |
| `jira-ops` | Cache, batching, health / operational utilities |

`sub_skills/shared/` is shared reference material (not a standalone installable skill).

## How to install

Placeholders filled when copying (NAME => value):

IS_GLOBAL => {IS_GLOBAL}
TYPE_OF_AI_TOOLS => {TYPE_OF_AI_TOOLS}
SKILL_PATH => {SKILL_PATH}

For **meta-jira** (credentials home):

```bash
mkdir -p "$DEST/meta-jira"
cp ~/.meta-skills/skills/productivity/meta-jira/SKILL.md "$DEST/meta-jira/SKILL.md"
# substitute {IS_GLOBAL}, {TYPE_OF_AI_TOOLS}, {SKILL_PATH} → absolute path of $DEST/meta-jira
cp ~/.meta-skills/skills/productivity/meta-jira/.env.example "$DEST/meta-jira/.env"
# edit JIRA_SITE_URL / JIRA_EMAIL / JIRA_API_TOKEN
```

For **each chosen sub-skill** `<id>`:

```bash
mkdir -p "$DEST/<id>"
cp ~/.meta-skills/skills/productivity/meta-jira/sub_skills/<id>/SKILL.md "$DEST/<id>/SKILL.md"
# substitute placeholders; set {SKILL_PATH} to $DEST/<id>
# Point CURRENT_SKILL_DIRECTORY at $DEST/meta-jira for shared credentials
# (sub-skills load env via meta-jira CLI — see Prerequisite in each sub-skill)
```

Do **not** copy the full `sub_skills/<id>/` tree into `$DEST` unless the user
explicitly wants docs/references locally — default register is **SKILL.md only**.

Remind the user to reload the agent / skills after install.

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
cd ~/.meta-skills/skills/productivity/meta-jira/scripts
```

Prefer `~/.meta-skills/.venv/bin/python`. First deps:
`cd ~/.meta-skills/skills/productivity/meta-jira && ~/.meta-skills/install.sh pip init .`

When a **sub-skill** is active, still load credentials from the registered
**meta-jira** dir (shared `.env`), then run:

```bash
export CURRENT_SKILL_DIRECTORY="$DEST/meta-jira"   # where .env lives
cd ~/.meta-skills/skills/productivity/meta-jira/scripts
python cli.py env
# or: python cli.py env-check
```

## Credentials — SkillCred `.env`

`.env` lives next to the **registered** `meta-jira` skill, resolved by
`SkillCred("meta-jira", [".env"])` under `$CURRENT_SKILL_DIRECTORY`.

| Variable | Notes |
|----------|--------|
| `JIRA_SITE_URL` | Atlassian site, e.g. `https://company.atlassian.net` |
| `JIRA_EMAIL` | Atlassian account email |
| `JIRA_API_TOKEN` | [API token](https://id.atlassian.com/manage-profile/security/api-tokens) |

```bash
cp ~/.meta-skills/skills/productivity/meta-jira/.env.example "{SKILL_PATH}/.env"
# edit values
python cli.py env          # load into process env
python cli.py env-check    # verify required keys
```

## Slash commands

### Installer / env

| Slash | CLI | Description |
|-------|-----|-------------|
| `/meta-jira_install` | (agent flow) | Ask tool + scope + sub-skills; `cp` SKILL.md files |
| `/meta-jira_env` | `python cli.py env` | Load `.env` into the process environment |
| `/meta-jira_env_check` | `python cli.py env-check` | Verify Jira credentials are present |

## How to run

1. Ask tool, scope, and which sub-skills (see [Ask first](#ask-first-required)).
2. Register `meta-jira` + chosen sub-skills into `$DEST` (see [How to install](#how-to-install)).
3. Copy `.env.example` → `$DEST/meta-jira/.env` and fill credentials.
4. `cd` to the [working directory](#working-directory); run `python cli.py env-check`.
5. Use the installed sub-skill `SKILL.md` for the user’s Jira task.

## Notes

- Confirm with the user before installing into **global** scope or overwriting existing skills.
- Never commit `.env`, tokens, or client secrets.
- Sub-skill bodies under `sub_skills/` are upstream documentation; keep local behavior (env CLI, SkillCred) in this meta-skill.
