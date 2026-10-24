---
name: meta-skills
description: >-
  Install or update Meta-Skills into Cursor, Claude, Hermes, OpenCode, or OpenClaw.
  Clone/pull this repo into ~/.meta-skills (shared library), auto-detect the tool via
  TERMINAL_ENV / CLAUDECODE / OPENCODE_, ask target + scope, then register chosen
  skills — copy the `### TO COPY`
  slice from each SKILL.md (substitute placeholders), link the library canonical
  SKILL.md under ~/.meta-skills. External git skills clone ONCE into ~/.meta-skills/ext
  via `install.sh fetch`; each skill installs its OWN deps on first run via
  `install.sh pip init` / `npm init` into ~/.meta-skills/.venv. Use when
  installing/refreshing skills, adding a skill from a git URL, or running /meta-skills.
disable-model-invocation: true
---

# Meta-Skills — the skill installer (Cursor / Claude / Hermes / OpenCode / OpenClaw)

This skill **is** the installer. Code and Python/npm deps live **once** in the shared library
`$META_SKILLS_HOME` (default `~/.meta-skills`); each tool only gets a registered `SKILL.md`
(the skill's `### TO COPY` slice + a link back to the library). Credentials stay next to the
registered `SKILL.md`, per project / profile.

## Read on demand

Open only the file needed for the current step (all under `~/.meta-skills/meta-skill-doc/`):

| File | When |
|------|------|
| `installer/architecture.md` | Shared library vs local credentials, `CURRENT_SKILL_DIRECTORY`, authoring |
| `installer/placeholders.md` | Substituting `{IS_GLOBAL}` / `{TYPE_OF_AI_TOOLS}` / `{SKILL_PATH}` / `{PROJECT_PATH}`, library reference |
| `installer/register.md` | `install.sh` commands, resolving `SRC`, registering standard / hub skills, copy map |
| `installer/examples.md` | End-to-end examples per tool |
| `<category>.md` | Skills of one category (see catalog below) |

## 0) Clone / pull the library

```bash
if [ -d ~/.meta-skills/.git ]; then git -C ~/.meta-skills pull --ff-only
else git clone https://github.com/Acher1234/Meta-Skills.git ~/.meta-skills; fi
```

## 1) Detect the tool

From the env vars of the **running** agent (not from `~/.cursor` / `~/.claude` existing):

- `$CLAUDECODE` or `$CLAUDE_CODE_ENTRYPOINT` → **Claude Code**
- any `$OPENCODE_*` (CLI sets `OPENCODE_PID`) → **OpenCode**
- `$TERMINAL_ENV` non-empty → **Hermes**
- `$CURSOR_AGENT` / `$CURSOR_TRACE_ID` (fallback `$TERM_PROGRAM` = `vscode`/`cursor`) → **Cursor**
- none / several → ask which tool(s). **OpenClaw** (WIP) only when asked explicitly.

## 2) Ask the scope → `DEST`

| Tool | Scope | `DEST` |
|------|-------|--------|
| cursor / claude / openclaw | `global` / `project` | `~/.<tool>/skills` / `./.<tool>/skills` |
| opencode | `global` / `project` | `${OPENCODE_CONFIG_DIR:-~/.config/opencode}/skills` / `./.opencode/skills` |
| hermes | `all` / `profile` | `~/.hermes/skills` / `$HERMES_HOME/skills` (ask if unset) |

Never write into `~/.cursor/skills-cursor/` (Cursor built-ins).

## 3) Ask which skills

A **built-in** skill (catalog below), an **external git URL** (cloned once into
`~/.meta-skills/ext/<name>`), or a **local path**. Install only what the user asks for. Never
re-install `meta-skills` itself (global-only, via `~/.meta-skills/INSTALL_PROMPT.md`).

### Skills catalog (show this to the user)

One file per category under `~/.meta-skills/meta-skill-doc/`, with each skill's **Folder**
(`SRC`), purpose and `SKILL.md` path. Read only the category the user needs.

| Category | Catalog | Skills |
|----------|---------|--------|
| Agent | `agent.md` | `hermes-all-message-read` |
| Database | `db.md` | `elastic` |
| Design | `design.md` | `gif-creator` |
| DevOps / DNS | `devops.md` | `godaddy` |
| MDM & Antivirus | `mdm-antivirus.md` | `eset`, `hexnode` |
| Productivity | `productivity.md` | `confluence`, `fathom`, `google-workspace`, `jira`, `pc-report`, `youtrack` |
| Security | `security.md` | `bitwarden`, `folder-crypt`, `zscaler` |

## 4) Register — checklist

1. Resolve `SRC` (external → `./install.sh fetch <url> [name]`; built-in → `~/.meta-skills/<Folder>`;
   local → given path). Register under `$DEST/<basename of SRC>/` — `installer/register.md`.
2. Standard skill: frontmatter + `### TO COPY` slice + library reference. Hub `meta-{domain}`: stubs
   only (`META_SKILL_TEMPLATE.md`). Legacy (no markers): copy the file.
3. Substitute placeholders; project scope in git → literal `$(git rev-parse --show-toplevel)/…` path
   (`{PROJECT_PATH}` → `$(git rev-parse --show-toplevel)`, else `$PWD`) and add `.<tool>/skills/*/.env` (+ token files) to `.gitignore` — `installer/placeholders.md`.
4. Copy `.env.example` → `$DEST/<name>/.env` when the skill needs credentials.
5. Do **not** install deps: each skill runs `./install.sh pip init .` / `npm init .` on first run
   (shared `~/.meta-skills/.venv`, with `common`; Windows: `install.ps1`, `.venv\Scripts\python.exe`).
6. Tell the user to reload the tool (or restart the Hermes agent). Later: `git pull` refreshes library
   `SKILL.md` bodies; re-run `/meta-skills` to add or re-register skills.

Repo: [Acher1234/Meta-Skills](https://github.com/Acher1234/Meta-Skills.git)
