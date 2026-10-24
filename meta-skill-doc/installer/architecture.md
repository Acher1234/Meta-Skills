# Installer — architecture (shared library, local secrets)

Heavy things live **once** under `$META_SKILLS_HOME` (default `~/.meta-skills`); each tool only
gets a lightweight registered `SKILL.md`.

```
~/.meta-skills/                 shared library root (this repo, or $META_SKILLS_HOME)
├── install.sh                  fetch / pip init / npm init  (see register.md)
├── meta-skill-common/          shared Python package (import as ``common``)
├── meta-skill-doc/             skill catalog (one file per category) + installer docs
├── skills/<category>/…/<name>/ built-in skills (CLI + SKILL.md)
├── ext/<name>/                 external skill repos, cloned ONCE
└── .venv/                      shared Python venv — every Python skill reuses it

        │ register = TO COPY slice + link to library SKILL.md; credentials next to it ↓
~/.cursor/skills/<name>/{SKILL.md,.env}   (flat by skill basename; or ./.cursor/skills/<name>/)
```

| Layer             | Location                                                        | Shared?                                  |
| ----------------- | --------------------------------------------------------------- | ---------------------------------------- |
| CLI / Python code | `~/.meta-skills/skills/<category>/…/<name>/` (or `ext/<name>/`) | **Yes**                                  |
| Shared helpers    | `~/.meta-skills/meta-skill-common/` (pip-installed as `common`) | **Yes**                                  |
| Python deps       | `~/.meta-skills/.venv`                                          | **Yes**                                  |
| Registered skill  | `$DEST/<name>/SKILL.md` — **TO COPY** slice + library link      | Lightweight; body updates via `git pull` |
| Credentials       | `$DEST/<name>/` (`.env`, tokens, `config.json`, …)              | **No** — per workspace / profile         |

- Never put secrets only under the shared library skill tree (that forces one account for every
  project). Register `SKILL.md` only, not the full skill tree (unless a skill documents an exception).
- `CURRENT_SKILL_DIRECTORY` must point at the directory holding the **registered** `SKILL.md`
  (where credentials live). Skills export it in their Working directory block before running CLIs;
  `SkillCred` / `SkillEnv` (`from common.skill_env import …`) read it. Unset → process cwd.
- Authoring: start from `~/.meta-skills/SKILL_TEMPLATE.md` (or `META_SKILL_TEMPLATE.md` for hub
  skills); provenance in `ORIGIN_TEMPLATE.md`.

```bash
mkdir -p ./.cursor/skills/my-skill                       # register (+ substitute placeholders)
cp ~/.meta-skills/skills/my-skill/.env.example ./.cursor/skills/my-skill/.env
cd ~/.meta-skills/skills/my-skill && ~/.meta-skills/.venv/bin/python scripts/cli.py …
```
