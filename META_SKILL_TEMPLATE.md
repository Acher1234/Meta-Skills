# Meta-skill template (`SKILL.md`)

Use this instead of [`SKILL_TEMPLATE.md`](SKILL_TEMPLATE.md) when the skill is an
**installer / hub**: it registers several **sub-skills** into Cursor / Claude /
Hermes / OpenClaw, and usually shares one credential `.env` via SkillCred.

Reference implementation: [`skills/productivity/meta-jira/SKILL.md`](skills/productivity/meta-jira/SKILL.md).

Also add [`ORIGIN.md`](ORIGIN_TEMPLATE.md) (vendored upstream or API docs).

## Layout

```
skills/<category>/…/meta-{domain}/
├── SKILL.md              # this meta-skill (installer)
├── ORIGIN.md
├── .env.example          # shared credentials for all sub-skills
├── requirements.txt
├── scripts/              # shared CLI (at least env / env-check)
│   ├── cli.py
│   └── env_load.py
└── sub_skills/
    ├── <sub-a>/SKILL.md  # installable unit
    ├── <sub-b>/SKILL.md
    └── shared/           # optional docs — not a standalone install target
```

## Rules

1. The meta-skill **does not** replace `/meta-skills` — it installs **domain**
   sub-skills after Meta-Skills is already on the machine.
2. **Ask first** (same as `/meta-skills`): target tool → scope (project/local vs
   global) → **which** sub-skills (never install all by default).
3. Register the **meta-skill itself** into `$DEST/meta-{domain}/` (credentials
   home) **and** each chosen sub-skill as a **flat** `$DEST/<sub-id>/`.
4. Default register = **`cp` `SKILL.md` only** (+ substitute placeholders). Do
   not copy full `sub_skills/<id>/` trees unless the user asks.
5. Shared secrets live next to the registered meta-skill
   (`SkillCred("meta-{domain}", [".env"])`). Sub-skills link to the meta-skill
   **Working directory** — do not repeat shell `.env` loading in each sub-skill.
6. List every installable sub-skill in a **catalog table** (id + one-line goal).
7. Add the meta-skill to the root [`SKILL.md`](SKILL.md) built-in catalog.

## `SKILL.md` body to copy

Replace `{…}` placeholders. Keep section order.

```markdown
---
name: meta-{domain}
description: >-
  Meta-skill that installs {Domain} sub-skills ({examples…}) into Cursor /
  Claude / Hermes / OpenClaw. Ask scope (project vs global) and which
  sub-skills to register, then copy each sub-skill SKILL.md + shared
  credentials via SkillCred `.env`. Use when the user mentions {Domain}
  skills, /meta-{domain}, or wants to install {sub-example}.
disable-model-invocation: true
---

# meta-{domain}

Installer meta-skill for {Domain}. It does **not** implement the product APIs
itself — it registers one or more **sub-skills** from `sub_skills/` into the AI
tool skills directory, and shares one `.env` resolved by SkillCred.

Upstream / provenance: see [ORIGIN.md](ORIGIN.md).

## When to use

- User wants {Domain} skills installed or refreshed
- User asks for `/meta-{domain}`, "install {domain} skill", "add {sub-example}", etc.
- User needs shared credentials wired for those sub-skills

## Ask first (required)

Before copying anything, ask the user (same pattern as `/meta-skills`):

1. **Target tool** (if not obvious): `cursor` | `claude` | `hermes` | `openclaw`
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

3. **Which sub-skills** to install — do **not** install all by default. Show the
   catalog below and let the user pick one, several, or all.

Also register **`meta-{domain}` itself** into `$DEST/meta-{domain}/` so
credentials and the installer stay discoverable. Sub-skills install as **flat**
basenames under `$DEST`.

## Sub-skills catalog

Source tree (library): `~/.meta-skills/skills/<category>/…/meta-{domain}/sub_skills/<id>/`

| Sub-skill | Goal |
|-----------|------|
| `{sub-a}` | {one-line goal} |
| `{sub-b}` | {one-line goal} |

Optional `sub_skills/shared/` is reference material only (not installable alone).

## How to install

Placeholders filled when copying (NAME => value):

IS_GLOBAL => {IS_GLOBAL}
TYPE_OF_AI_TOOLS => {TYPE_OF_AI_TOOLS}
SKILL_PATH => {SKILL_PATH}

For **meta-{domain}** (credentials home):

```bash
mkdir -p "$DEST/meta-{domain}"
cp ~/.meta-skills/skills/<category>/…/meta-{domain}/SKILL.md "$DEST/meta-{domain}/SKILL.md"
# substitute {IS_GLOBAL}, {TYPE_OF_AI_TOOLS}, {SKILL_PATH} → absolute $DEST/meta-{domain}
cp ~/.meta-skills/skills/<category>/…/meta-{domain}/.env.example "$DEST/meta-{domain}/.env"
# edit credential keys
```

For **each chosen sub-skill** `<id>`:

```bash
mkdir -p "$DEST/<id>"
cp ~/.meta-skills/skills/<category>/…/meta-{domain}/sub_skills/<id>/SKILL.md "$DEST/<id>/SKILL.md"
# substitute placeholders; {SKILL_PATH} → $DEST/<id>
# Credentials: CURRENT_SKILL_DIRECTORY=$DEST/meta-{domain} + meta CLI env
```

Default register is **SKILL.md only**. Remind the user to reload skills after install.

## Working directory

Placeholders changed by `/meta-skills` at copy time (NAME => {PLACEHOLDER}):

IS_GLOBAL => {IS_GLOBAL}
TYPE_OF_AI_TOOLS => {TYPE_OF_AI_TOOLS}
SKILL_PATH => {SKILL_PATH}

Point SkillCred at the registered meta-skill dir (credentials live in `{SKILL_PATH}/.env`):

```bash
export CURRENT_SKILL_DIRECTORY="{SKILL_PATH}"
~/.meta-skills/.venv/bin/python ~/.meta-skills/skills/<category>/…/meta-{domain}/scripts/cli.py env
```

Do **not** load `.env` via shell (`source`, `set -a`, `[ -f … ]`) — that is bash-specific and breaks on Windows / PowerShell / other shells. Let Python resolve credentials through `SkillCred` / `env_load.py` (cross-platform).

Prefer `~/.meta-skills/.venv/bin/python`. First deps:
`cd ~/.meta-skills/skills/<category>/…/meta-{domain} && ~/.meta-skills/install.sh pip init .`

When a **sub-skill** is active, set `CURRENT_SKILL_DIRECTORY` to the registered meta dir (`$DEST/meta-{domain}`), then run the meta CLI:

```bash
export CURRENT_SKILL_DIRECTORY="$DEST/meta-{domain}"
~/.meta-skills/.venv/bin/python ~/.meta-skills/skills/<category>/…/meta-{domain}/scripts/cli.py env-check
```

## Credentials — SkillCred `.env`

`.env` next to the registered **meta-{domain}** skill:
`SkillCred("meta-{domain}", [".env"])` under `$CURRENT_SKILL_DIRECTORY`.

| Variable | Notes |
|----------|--------|
| `{ENV_KEY}` | {what it is} |

```bash
cp ~/.meta-skills/skills/<category>/…/meta-{domain}/.env.example "{SKILL_PATH}/.env"
~/.meta-skills/.venv/bin/python ~/.meta-skills/skills/<category>/…/meta-{domain}/scripts/cli.py env-check
```

## Slash commands

### Installer / env

| Slash | CLI | Description |
|-------|-----|-------------|
| `/meta-{domain}_install` | (agent flow) | Ask tool + scope + sub-skills; `cp` SKILL.md files |
| `/meta-{domain}_env` | `python cli.py env` | Load `.env` into the process environment |
| `/meta-{domain}_env_check` | `python cli.py env-check` | Verify required credential keys |

## How to run

1. Ask tool, scope, and which sub-skills.
2. Register `meta-{domain}` + chosen sub-skills into `$DEST`.
3. Copy `.env.example` → `$DEST/meta-{domain}/.env` and fill credentials.
4. Run `python cli.py env-check`.
5. Follow the installed sub-skill `SKILL.md` for the user’s task.

## Notes

- Confirm before **global** installs or overwrites.
- Never commit `.env`, tokens, or client secrets.
- Keep product docs under `sub_skills/`; keep install + env CLI in the meta-skill.
```

## Checklist when authoring

- [ ] Folder `skills/<category>/…/meta-{domain}/` + `sub_skills/<id>/SKILL.md`
- [ ] Meta `SKILL.md` from this template (catalog complete)
- [ ] Each sub-skill `SKILL.md` links to meta **Working directory** (no shell `.env` loading)
- [ ] `.env.example` + `scripts/env_load.py` + `scripts/cli.py` (`env`, `env-check`)
- [ ] `ORIGIN.md` from [`ORIGIN_TEMPLATE.md`](ORIGIN_TEMPLATE.md)
- [ ] Row added to root [`SKILL.md`](SKILL.md) skills catalog
- [ ] `requirements.txt` if Python deps are needed
