# 📦 Dependencies — bitwarden

| Package | Version | Install | Usage |
|---------|---------|---------|-------|
| `node` | `~22` (v20 works) | [nodejs.org](https://nodejs.org) / `brew install node` | Runtime of `bw` |
| `npm` | `~10` | ships with node | Installs pinned `bw` |
| `@bitwarden/cli` | locked in `package-lock.json` | `~/.meta-skills/install.sh npm init .` | `bw` binary |
| `jq` | any | `brew install jq` | JSON edits for `create` / `edit` |
| `meta-skill-common` | repo | `~/.meta-skills/install.sh pip init .` | `SkillEnv` for `skill_env.py` |

Agent runs `bw` directly. `scripts/skill_env.py` exports `.env`; login/unlock are documented in `SKILL.md`.

## Where things land

`npm init` → `~/.meta-skills/skills/security/bitwarden/node_modules/` (gitignored).

Runtime next to the registered skill (`$CURRENT_SKILL_DIRECTORY`): `.env`, `.bw-appdata/`
(gitignored).
