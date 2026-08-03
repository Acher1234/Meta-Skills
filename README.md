<div align="center">

<img src="assets/logo.png" alt="Meta-Skills" width="640" />

# Meta-Skills

**A shared library of CLI _skills_ for AI agents — installable on Cursor, Claude, Hermes & OpenClaw.**

*by the community* · [github.com/Acher1234/Meta-Skills](https://github.com/Acher1234/Meta-Skills.git)

</div>

---

## 🧭 What is this?

**Meta-Skills** is a collection of _skills_ (shell / Python / Node CLI scripts) that AI agents
can use, plus a **meta-installer** that registers them in any tool.

The key idea: **one shared library + one Python/npm environment** on the machine.
We **do not re-clone** and we **do not reinstall** dependencies for every project — the heavy
parts live once; each tool only gets the `SKILL.md`.

| | |
|---|---|
| 🎯 **Multi-target** | Cursor · Claude · Hermes · OpenClaw *(OpenClaw in progress)* |
| 🌐 **External skills** | Can install **any** git skill repo, not only the ones here |
| ♻️ **Shared env** | One Python venv (`~/.meta-skills/.venv`) + global npm; **each skill installs its own deps there** (once, not per project) |
| 📦 **Shared cache** | External repos cloned **once** under `~/.meta-skills/ext/` |

## 🏛️ Architecture

The heavy parts are shared under `~/.meta-skills`; each tool only receives the `SKILL.md`.

```
~/.meta-skills/                       shared library ($META_SKILLS_HOME)
├── install.sh                      the meta-installer (driven by /meta-skills)
├── skills/<category>/…/<name>/     built-in skills (nested by domain)
├── ext/<repo>/                     external git skills, cloned ONCE
|__ .venv/                          shared Python venv (all Python skills)

npm i -g <pkg>                      shared global Node CLIs (agent-browser, …)

        │ we ONLY copy SKILL.md into each tool (flat by skill basename) ↓
~/.cursor/skills/<name>/SKILL.md     ~/.claude/skills/<name>/SKILL.md
~/.hermes/skills/<name>/SKILL.md     ~/.openclaw/skills/<name>/SKILL.md
```

Each `SKILL.md` points to its working directory under `~/.meta-skills/…`: the agent `cd`s there and
runs the code / venv installed **once**.

## 🚀 Installation

### 1. Clone the shared library (once)

```bash
git clone https://github.com/Acher1234/Meta-Skills.git ~/.meta-skills
cd ~/.meta-skills && ./setup.sh          # enable the pre-commit hook (gitleaks)
```

### 2. Prepare the shared environment

```bash
cd ~/.meta-skills
./install.sh --help     # lists the 3 commands: fetch, pip init, npm init
```

### 3. Install skills

Paste the install prompt into an **Agent** chat, then run `/meta-skills`.
Flow: **1)** pick the tool (Cursor / Claude / Hermes / OpenClaw) → **2)** the scope
(global / project / profile) → **3)** what to install (external git URL, built-in skill, or local path).

## 🪄 Meta-skills (installers)

| Meta-skill | Slash | Role |
|-----------|-------|------|
| `meta-skills` | `/meta-skills` | **The installer**: installs any skill (external git / built-in / local) on **Cursor / Claude / Hermes / OpenClaw**, with a **shared** Python/npm env. See [`SKILL.md`](SKILL.md) + [`install.sh`](install.sh). |

### `/meta-skills` — the installer

`install.sh` has **3 commands**: `fetch`, `pip init`, `npm init`. Registering a skill in a
tool is a simple `cp` of the `SKILL.md`.

```bash
cd ~/.meta-skills

# external git skill → cloned ONCE into the shared cache
SRC=$(./install.sh fetch https://github.com/some/cool-skill.git cool-skill)

# register = cp SKILL.md into the tool (Claude global, then Cursor project)
mkdir -p ~/.claude/skills/cool-skill && cp "$SRC/SKILL.md" ~/.claude/skills/cool-skill/SKILL.md
mkdir -p ./.cursor/skills/cool-skill && cp "$SRC/SKILL.md" ./.cursor/skills/cool-skill/SKILL.md

# the skill installs ITS OWN deps (first run) into the shared venv
./install.sh pip init "$SRC"                    # or, from the skill folder: ./install.sh pip init .
```

> The installer **does not** run `pip install` for you: `fetch` (clone) + `cp` (register).
> Each skill installs **its own** dependencies via `pip init` / `npm init` on first run,
> into the shared venv (`~/.meta-skills/.venv`) — once per machine, reused across all projects.

| Target (`tool` / `scope`) | Install folder |
|--------------------------|-------------------|
| `cursor` / `global` | `~/.cursor/skills/<name>/` |
| `cursor` / `project` | `./.cursor/skills/<name>/` |
| `claude` / `global` | `~/.claude/skills/<name>/` |
| `claude` / `project` | `./.claude/skills/<name>/` |
| `hermes` / `all` | `~/.hermes/skills/<name>/` |
| `hermes` / `profile` | `${HERMES_HOME}/skills/<name>/` |
| `openclaw` / `global` | `~/.openclaw/skills/<name>/` *(WIP)* |
| `openclaw` / `project` | `./.openclaw/skills/<name>/` *(WIP)* |

> **Claude Code** is fully supported (detected via `$CLAUDECODE`). **OpenClaw** is still
> **in progress**: the paths above are defaults and may change once its conventions settle.

## 📦 Built-in skills

**Root (Meta-Skills)**


## 🔒 Security — git hooks

A `pre-commit` hook (`.githooks/`) runs **gitleaks** to block any commit containing a key or
token. Enable it once after cloning:

```bash
./setup.sh
```

> `git` does not apply `core.hooksPath` automatically on clone (security), hence this one-time step.
> `setup.sh` runs `git config core.hooksPath .githooks` and checks that `gitleaks` is installed.
> Details: [`dependencies.md`](dependencies.md).

Secrets live in the tool `.env` (`~/.cursor/.env`, `~/.claude/.env`, `$HERMES_HOME/.env`,
`~/.openclaw/.env`) — **never** inside a skill.

## 🧩 Create a new skill

See **[`SKILL_TEMPLATE.md`](SKILL_TEMPLATE.md)**, **[`META_SKILL_TEMPLATE.md`](META_SKILL_TEMPLATE.md)** (for installer meta-skills), and **[`ORIGIN_TEMPLATE.md`](ORIGIN_TEMPLATE.md)** (structure, `SKILL.md`, slash `/{skill}_{command}`,
conventions, security). Each sub-project contains:

- a **`SKILL.md`** (EN) — agent skill + `/{skill}_{command}` actions;
- a **`README.md`** / **`README.fr.md`**;
- a **`dependencies.md`**;
- a **`config.example.json`** / **`.env.example`** (real secrets are gitignored);
- the executable **script**.

A Python skill should target the **shared** interpreter `~/.meta-skills/.venv/bin/python` rather than
a per-project venv.

---

*Maintained by the community.*

> French version: [`README-FR.md`](README-FR.md)
