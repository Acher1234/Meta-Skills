# TODO

## SKILL.md token budget (CI + pre-commit)

Add automated checks so every `SKILL.md` stays under a token limit.

### Scope

- Scan all `**/*.md` in the repo (root installer + `skills/**`).
- Fail if estimated tokens exceed the configured limit.
- Optional: different limits per file type (e.g. root `SKILL.md` vs registered slice `### TO COPY` only).

### Suggested limits (to tune)

| File | Max tokens (estimate) |
|------|------------------------|
| Root `SKILL.md` (meta-skills installer) | 2500 |
| Standard skill library `SKILL.md` | 2000 |
| `### TO COPY` slice only | 500 |

---

## Python linter (CI + pre-commit)

Add a shared Python lint/format setup for `meta-skill-common/` and skill scripts under `skills/**`.

### Scope

- Pick one stack (e.g. **ruff** for lint + format, or **ruff** + **mypy** if type-checking is wanted).
- Config at repo root (`pyproject.toml` or `ruff.toml`) with sensible defaults for scripts/CLIs.
- **Pre-commit** — run on staged `.py` files (fast).
- **GitHub Action** — full-tree check on `pull_request` / `push` to `main`.
- Document how to run locally (`ruff check`, `ruff format --check`, etc.) in README or `setup.sh` output.

### Notes

- Respect existing style where possible; avoid a huge one-shot reformat unless agreed.
- Exclude vendored/generated paths if any appear later.

---

## Project dependencies

Centralize and document repo-wide dependencies (installer, shared venv, skills).

### Scope

- Root **`dependencies.md`** (or `project-dependencies.md`) listing:
  - shared Python packages (`meta-skill-common`, root `requirements` if any)
  - global npm tools used by the installer
  - system prerequisites (`git`, `python3`, `gitleaks`, etc.)
- Per-skill: keep or align existing `dependencies.md` / `requirements.txt` with a common template.
- Optional: script or CI check that `requirements.txt` files match what `install.sh pip init` expects.
- Link from root `README.md` / `SKILL.md` installer docs.

---

## License (repo + skills)

Make the PolyForm Noncommercial license visible and consistent across the project.

### Scope

- Root **`LICENSE`** is done — keep as source of truth.
- Add a short **License** blurb to root `SKILL.md` installer (and templates: `SKILL_TEMPLATE.md`, `ORIGIN_TEMPLATE.md`).
- Per-skill: optional `LICENSE` symlink or one-line pointer in `README.md` / `ORIGIN.md` (“same license as Meta-Skills root”).
- Optional: SPDX header in shared Python modules (`SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0`).
- Document commercial licensing contact path in README if offering paid use later.

---

## Skill upgrade request (server + all skills)

When a skill CLI fails or needs a library code change, the **skill itself** must tell the agent to request an upgrade — not patch `~/.meta-skills` in the current task.

Today that protocol lives only in the Cursor rule `meta-skills-upgrade-prompt.mdc` (this repo). Registered skills used in other workspaces never see it. Any AI tool (Cursor, Claude, Hermes, OpenClaw) should be able to **submit** the same request to a local Meta-Skills server.

### Opt-in (user must allow it)

Default **off**. Agents must not POST upgrade requests unless the user has enabled it.

Machine-wide flag in `~/.meta-skills/.env` (and documented in `.env.example`):

| Variable | Meaning |
|----------|---------|
| `META_SKILLS_UPGRADE_REQUESTS` | `true` / `1` / `yes` = allowed; unset / `false` = refuse and fall back to `prompt.md` |
| `META_SKILLS_UPGRADE_TOKEN` | Optional shared secret so the server can attribute and reject unauthenticated callers |
| `META_SKILLS_UPGRADE_URL` | Optional override (default `http://127.0.0.1:<port>`) |

Shared helper (e.g. `common.upgrade_request`) reads these via SkillCred / `~/.meta-skills/.env`. If the flag is off: do **not** call the server; write `prompt.md` and tell the user how to opt in.

### Upgrade request server

Local HTTP service under `~/.meta-skills` (localhost only). Any registered skill / any AI tool POSTs a change request; the user later applies them in a dedicated Meta-Skills agent chat.

#### Scope

- Bind **127.0.0.1** only (no LAN/WAN unless explicitly designed later).
- Persist a queue (e.g. `~/.meta-skills/upgrade-requests/*.json`).
- CLI: start / stop / status / list / show (via `install.sh` or `python -m common.upgrade_server`).
- Reject requests when `META_SKILLS_UPGRADE_REQUESTS` is off, or when the token does not match (if set).

#### Identify the sender

Every request must be attributable. The server records (and the CLI payload includes):

| Field | Source |
|-------|--------|
| `user` | OS user (`$USER` / uid) + optional `git config user.email` / `user.name` |
| `host` | hostname |
| `tool` | `$TYPE_OF_AI_TOOLS` (`CURSOR` / `CLAUDE` / `HERMES` / `OPENCLAW`) |
| `skill` | skill name + library path under `~/.meta-skills/skills/…` (or `ext/…`) |
| `workspace` | `$CURRENT_SKILL_DIRECTORY` (registered skill dir) |
| `is_global` | `$IS_GLOBAL` |
| `token_ok` | whether `META_SKILLS_UPGRADE_TOKEN` matched (never store the raw token in the queue) |

Reject or flag requests with missing identity. List/show output must make it obvious **who** asked for **which** skill.

### Skill docs (all skills)

- Add a short **Upgrade request** section to `SKILL_TEMPLATE.md` (and `META_SKILL_TEMPLATE.md` if needed), inside **`### TO COPY`** so it lands in every registered `$DEST/<skill>/SKILL.md`.
- Roll the same section into every existing skill `SKILL.md`.
- Keep the Cursor rule as the source of truth for work *inside* this repo; skills carry the copy that agents see elsewhere.

### Agent must

1. Finish what it can without editing skill code (credentials, queries, workspace docs).
2. If `META_SKILLS_UPGRADE_REQUESTS` is on: POST the upgrade payload to the local server (shared CLI helper — do not invent per-skill HTTP).
3. Else (or if the server is down): write a ready-to-paste upgrade prompt at the **workspace root** (`prompt.md`, or `prompt-<skill>.md` if another upgrade is already there).
4. Tell the user: request queued (with id + who) **or** attach `prompt.md` in a **dedicated Agent chat** against `~/.meta-skills`.

### Payload / `prompt.md` shape

```markdown
# Upgrade: <skill-name>

Shared library: ~/.meta-skills/skills/<path>
Registered skill dir: <CURRENT_SKILL_DIRECTORY>
Sender: <os user> @ <host> via <TYPE_OF_AI_TOOLS>

## Failure / gap
- Command: `…`
- Error: `…`
- What I needed: …

## Requested change
…

## Constraints
Hybrid model: CLI stays under ~/.meta-skills; credentials via SkillCred + CURRENT_SKILL_DIRECTORY.
Do not break existing slash/CLI commands. Update SKILL.md + command.md.
```

### Do not (in the consuming task)

- Patch the shared skill library.
- Invent a one-off workaround that belongs in the skill (`scripts/`, `cli.py`, `command.md`).
- Silently `pip install` / rewrite imports as a substitute for an upgrade.
- POST to the server when the user has not opted in.

