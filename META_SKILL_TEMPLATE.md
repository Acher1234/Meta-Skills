# Meta-skill template (`SKILL.md`)

Use this instead of [`SKILL_TEMPLATE.md`](SKILL_TEMPLATE.md) when the skill is an
**installer / hub**: it registers several **sub-skills** into Cursor / Claude /
Hermes / OpenClaw, and usually shares one credential `.env` via SkillCred.

Reference implementation: [`skills/productivity/meta-jira/SKILL.md`](skills/productivity/meta-jira/SKILL.md).

Also add [`ORIGIN.md`](ORIGIN_TEMPLATE.md) (vendored upstream or API docs).

## Layout

```
skills/<category>/…/meta-{domain}/
├── SKILL.md              # canonical doc (library — never copied wholesale)
├── ORIGIN.md
├── .env.example          # shared credentials for all sub-skills
├── requirements.txt
├── scripts/
│   └── skill_env.py      # SkillEnv subclass (verify only)
└── sub_skills/
    ├── <sub-a>/SKILL.md  # canonical sub-skill doc
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
4. **Do not `cp` library `SKILL.md` files** — write a **stub** in `$DEST` that
   sets `CURRENT_SKILL_DIRECTORY` / placeholders and **links** the canonical file
   under `~/.meta-skills/…`. `git pull` updates behavior without re-registering.
5. Shared secrets live next to the registered meta-skill stub
   (`SkillCred("meta-{domain}", [".env"])`). Sub-skills point credentials at
   `$DEST/meta-{domain}/`, not their own stub dir.
6. List every installable sub-skill in a **catalog table** (id + one-line goal).
7. Add the meta-skill to the root [`SKILL.md`](SKILL.md) built-in catalog.

## Registration stubs (not full copy)

When installing, **write** these minimal files. Substitute `{IS_GLOBAL}`,
`{TYPE_OF_AI_TOOLS}`, `{SKILL_PATH}`, `{META_SKILL_PATH}`, `{LIB_*}` with real paths.

### Meta-skill stub → `$DEST/meta-{domain}/SKILL.md`

```markdown
---
name: meta-{domain}
description: >-
  Meta-skill hub for {Domain} — read the library SKILL.md for install flow and sub-skills.
disable-model-invocation: true
---

# meta-{domain}

Shared credentials: `{SKILL_PATH}/.env`

```bash
export CURRENT_SKILL_DIRECTORY="{SKILL_PATH}"
export IS_GLOBAL="{IS_GLOBAL}"
export TYPE_OF_AI_TOOLS="{TYPE_OF_AI_TOOLS}"
```

---

## Library reference

`{LIB_META_SKILL}`
```

`{SKILL_PATH}` = absolute `$DEST/meta-{domain}`.  
`{LIB_META_SKILL}` = `~/.meta-skills/skills/<category>/…/meta-{domain}/SKILL.md`.

### Sub-skill stub → `$DEST/<sub-id>/SKILL.md`

```markdown
---
name: {sub-id}
description: >-
  {Domain} {sub-id} — read the library SKILL.md for commands and examples.
disable-model-invocation: true
---

# {sub-id}

Shared credentials: `{META_SKILL_PATH}/.env`

```bash
export CURRENT_SKILL_DIRECTORY="{META_SKILL_PATH}"
export IS_GLOBAL="{IS_GLOBAL}"
export TYPE_OF_AI_TOOLS="{TYPE_OF_AI_TOOLS}"
```

---

## Library reference

`{LIB_SUB_SKILL}`
```

`{META_SKILL_PATH}` = absolute `$DEST/meta-{domain}`.  
`{LIB_SUB_SKILL}` = `~/.meta-skills/skills/<category>/…/meta-{domain}/sub_skills/<sub-id>/SKILL.md`.

Agents **must read** the library path for slash commands, catalogs, and examples.

## `SKILL.md` body (library — canonical)

Replace `{…}` placeholders. This file lives only under `~/.meta-skills/…` — it is
**not** copied into `$DEST`. Keep section order.

```markdown
---
name: meta-{domain}
description: >-
  Meta-skill that installs {Domain} sub-skills ({examples…}) into Cursor /
  Claude / Hermes / OpenClaw. Ask scope (project vs global) and which
  sub-skills to register. Use when the user mentions {Domain}
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

Before registering anything, ask the user (same pattern as `/meta-skills`):

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

Also register **`meta-{domain}` itself** into `$DEST/meta-{domain}/` (credentials
home + stub). Sub-skills install as **flat** basenames under `$DEST` (stub only).

## Sub-skills catalog

Source tree (library): `~/.meta-skills/skills/<category>/…/meta-{domain}/sub_skills/<id>/`

| Sub-skill | Goal |
|-----------|------|
| `{sub-a}` | {one-line goal} |
| `{sub-b}` | {one-line goal} |

Optional `sub_skills/shared/` is reference material only (not installable alone).

## How to install

Write **registration stubs** (see [Registration stubs](#registration-stubs-not-full-copy))
— do **not** copy this library file into `$DEST`.

```bash
LIB=~/.meta-skills/skills/<category>/…/meta-{domain}
META_DEST="$DEST/meta-{domain}"
mkdir -p "$META_DEST"
# write $META_DEST/SKILL.md stub → library link $LIB/SKILL.md
cp "$LIB/.env.example" "$META_DEST/.env"
# edit credential keys

# for each chosen sub-skill <id>:
SUB_DEST="$DEST/<id>"
mkdir -p "$SUB_DEST"
# write $SUB_DEST/SKILL.md stub → $LIB/sub_skills/<id>/SKILL.md
```

Remind the user to reload skills after install.

## Working directory

Credentials resolve from the **registered meta-skill dir** (`$DEST/meta-{domain}/`):

```bash
export CURRENT_SKILL_DIRECTORY="$DEST/meta-{domain}"
eval "$(~/.meta-skills/.venv/bin/python ~/.meta-skills/skills/<category>/…/meta-{domain}/scripts/skill_env.py)"
```

### How credentials reach commands

| Pattern | When | How the agent runs commands |
|---------|------|-----------------------------|
| **Python CLI** | Meta CLI wraps every API call | `python cli.py <subcommand> …` |
| **Python scripts** | Sub-skill ships its own script | `python scripts/<script>.py …` |
| **External CLI** | Sub-skill documents a third-party binary | `eval "$(python scripts/skill_env.py)"` then `<binary> <args>` |

Prefer `~/.meta-skills/.venv/bin/python`. First deps:
`cd ~/.meta-skills/skills/<category>/…/meta-{domain} && ~/.meta-skills/install.sh pip init .`

## Credentials — SkillCred `.env`

`.env` next to the registered **meta-{domain}** stub:
`SkillCred("meta-{domain}", [".env"])` under `$CURRENT_SKILL_DIRECTORY`.

| Variable | Notes |
|----------|--------|
| `{ENV_KEY}` | {what it is} |

## Slash commands

### Installer

| Slash | Action | Description |
|-------|--------|-------------|
| `/meta-{domain}_install` | (agent flow) | Ask tool + scope + sub-skills; write stubs + `.env` |

### Product (read library sub-skill `SKILL.md`)

{list sub-skill slashes here — agents follow `$LIB/sub_skills/<id>/SKILL.md`}

## How to run

1. Ask tool, scope, and which sub-skills.
2. Write stubs for `meta-{domain}` + chosen sub-skills into `$DEST`.
3. Copy `.env.example` → `$DEST/meta-{domain}/.env` and fill credentials.
4. Read the relevant **library** `SKILL.md` for the user’s task.

## Notes

- Confirm before **global** installs or overwrites.
- Never commit `.env`, tokens, or client secrets.
- Keep product docs under `sub_skills/`; keep install flow in this library file.
```

## Checklist when authoring

- [ ] Folder `skills/<category>/…/meta-{domain}/` + `sub_skills/<id>/SKILL.md`
- [ ] Library meta `SKILL.md` from this template (catalog complete)
- [ ] Each sub-skill library `SKILL.md` documents commands (no shell `.env` loading)
- [ ] `.env.example` + `scripts/skill_env.py`
- [ ] `ORIGIN.md` from [`ORIGIN_TEMPLATE.md`](ORIGIN_TEMPLATE.md)
- [ ] Row added to root [`SKILL.md`](SKILL.md) skills catalog
- [ ] `requirements.txt` if Python deps are needed
- [ ] Registration = **stub + library link** only (never `cp` full `SKILL.md`)
