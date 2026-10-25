# AGENTS.md — Meta-Skills

Guide for any AI agent (Claude Code, Cursor, Codex, OpenCode, Hermes…) working in this repo.

## What this repo is

**Meta-Skills** is the upstream, community library of CLI *skills* for AI agents plus a
**meta-installer** (`/meta-skills`) that registers them into Cursor, Claude Code, Hermes,
OpenCode and OpenClaw (WIP).

- Users clone it once to `~/.meta-skills` (`$META_SKILLS_HOME`).
- Code and Python deps live **once** on the machine (`~/.meta-skills/.venv`).
- Each tool only receives a lightweight registered `SKILL.md` (the `### TO COPY` slice,
  placeholders substituted, plus a link back to the library `SKILL.md`).
- Credentials live next to the **registered** `SKILL.md` (per project / profile), never in
  the library.

## Layout

| Path | Role |
|------|------|
| `SKILL.md` | The `/meta-skills` installer (global-only): short decision flow + catalog index, details in `meta-skill-doc/installer/` |
| `INSTALL_PROMPT.md` | Prompt pasted into an agent chat to bootstrap the installer |
| `install.sh` / `install.ps1` | Exactly 3 commands: `fetch <git-url> [name]`, `pip init [dir]`, `npm init [dir]` |
| `setup.sh` | Sets `core.hooksPath=.githooks` and checks `gitleaks` |
| `.githooks/pre-commit` | `gitleaks` scan of staged changes — blocks secrets |
| `meta-skill-common/` | Shared Python package, pip-installed (editable) as `common` — see below |
| `meta-skill-doc/` | Skill catalog (one file per category) + `installer/` details, both pointed to from the root `SKILL.md` |
| `skills/<category>/…/<name>/` | One skill per folder (see catalog in `SKILL.md`) |
| `SKILL_TEMPLATE.md`, `META_SKILL_TEMPLATE.md`, `ORIGIN_TEMPLATE.md` | Templates for new skills, hub meta-skills, provenance |
| `devops/count_md_tokens.py` | Token counter for Markdown files (`tiktoken`) |
| `todo.md` | Backlog (token budget CI, ruff linter, deps doc, license blurbs) |
| `.cursor/rules/` | Conventional commits + minimal English comments |

Skills: see the catalog table in `SKILL.md` → `meta-skill-doc/<category>.md`.

### `meta-skill-common` (import as `common`)

One folder per helper, one class per file; each folder `__init__.py` only re-exports.

| Module | Provides |
|--------|----------|
| `common.skill_env` | `SkillCred` (config files under `$CURRENT_SKILL_DIRECTORY`), `SkillEnv` base (`.env` parsing, `verify()`, shell exports) |
| `common.proxy` | `Proxy`, `resolve_proxy`, `ProxySkillEnv` — DataImpulse / `PROXY_URL` (http, socks5) |
| `common.http` | `HttpClient`, `HttpSkillEnv` — REST client (timeouts, retries, throttle, download, proxy); needs `requests` in the skill deps |
| `common.browser` | `Browser`, `BrowserSkillEnv` — Camoufox browser automation (headless, proxy) |

`SkillEnv` subclasses are cooperative mixins (`class MySkillEnv(HttpSkillEnv, BrowserSkillEnv)`);
every `verify()` returns `{**super().verify(values), **own_keys}`. `PROXY_*` / `HTTP_*` / browser keys
are optional. New REST skills use `HttpClient` instead of their own `requests` wrapper. New helper
folder → add it to `packages` in `meta-skill-common/pyproject.toml`.

## Anatomy of a skill

```
skills/<category>/<name>/
├── SKILL.md            frontmatter + ### TO COPY … ##### END TO COPY slice + full docs
├── ORIGIN.md           provenance (ORIGIN_TEMPLATE.md)
├── README.md           human doc (optional)
├── .env.example        keys the user fills in the registered skill dir
├── requirements.txt    Python deps → installed into the shared venv
├── command.md/         optional: one <name>-<domain>.command.md per command group
└── scripts/
    ├── cli.py          argparse, one subcommand per /<skill>_<action>, JSON on stdout
    └── skill_env.py    SkillEnv / HttpSkillEnv / BrowserSkillEnv subclass with verify()
```

## Conventions

- Start new skills from `SKILL_TEMPLATE.md`; keep the `### TO COPY` / `##### END TO COPY`
  markers and the `{IS_GLOBAL}`, `{TYPE_OF_AI_TOOLS}`, `{SKILL_PATH}` placeholders (bash **and**
  PowerShell variants).
- Read credentials only through `SkillCred` / `SkillEnv` (`$CURRENT_SKILL_DIRECTORY`).
  Never `source .env`, never commit `.env`, tokens or real secrets — the pre-commit hook runs gitleaks.
- CLI output: JSON on stdout, logs/debug on stderr. Confirm with the user before side effects
  (send, delete, write…).
- Python: `~/.meta-skills/.venv/bin/python` (Windows: `.venv\Scripts\python.exe`); install deps
  with `./install.sh pip init <skill dir>`. Code style: `from __future__ import annotations`,
  type hints, short docstrings, minimal English comments.
- `SKILL.md`, `.env.example`, code and commit messages in **English**. `README-FR.md` is the French mirror of `README.md`.
- Commits: Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`…), branches `feat/…`, `fix/…`, `docs/…`.
- No test suite yet: validate with a quick import / smoke run outside the repo.
- Do only what is asked; don't refactor unrelated skills; never commit or push unless asked.
- Never name repos that fork or build on this one: only a child repo names its `upstream`.

## Keep files minimal — point, don't inline

- Every file an agent loads (`SKILL.md`, `AGENTS.md`, `rules.md`, `CLAUDE.md`, command docs) stays
  short: only what is needed to decide the next step.
- Prefer a **pointer** to another file over copying its content (`see meta-skill-doc/<category>.md`,
  `details: command.md/<x>.command.md`). One fact lives in one file.
- Split big docs by topic (one file per category / command group) and keep an index with one line
  per file, so an agent opens only the part it needs.
- Root `SKILL.md` = decision flow + one catalog row per category (`meta-skill-doc/<category>.md`); installer
  details live in `meta-skill-doc/installer/`. Pointers use `~/.meta-skills/…` paths (the installer `SKILL.md` is
  copied out of the repo, so relative links break). A skill's
  `SKILL.md` = `### TO COPY` slice + a short command index; long references go to `command.md/` or
  `references/`.
- New skill → add its row to `meta-skill-doc/<category>.md` (create the file for a new category) and
  its name to the catalog table in `SKILL.md`.
- Token budget (see `todo.md`): root `SKILL.md` ≤ 2500, skill `SKILL.md` ≤ 2000, `TO COPY` slice ≤ 500.
  Check with `python devops/count_md_tokens.py <path>`.

## Useful commands

```bash
./setup.sh                                   # enable gitleaks pre-commit hook
./install.sh pip init skills/db/elastic      # shared venv + common + skill deps
~/.meta-skills/.venv/bin/python skills/db/elastic/scripts/cli.py --help
python devops/count_md_tokens.py skills      # check SKILL.md token sizes
```

License: PolyForm Noncommercial 1.0.0 (`LICENSE`).
