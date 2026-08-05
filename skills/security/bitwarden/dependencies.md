# 📦 Dependencies — bitwarden

| Package | Version | Install | Usage |
|---------|---------|---------|-------|
| `node` | `~22` (v20 works) | [nodejs.org](https://nodejs.org) / `brew install node` | Runtime of the `bw` CLI |
| `npm` | `~10` | ships with node | Installs the pinned `bw` |
| `@bitwarden/cli` | `2026.7.0` (locked) | `~/.meta-skills/install.sh npm init .` | The `bw` binary — vault, Send, generator |
| `meta-skill-common` | repo | `~/.meta-skills/install.sh pip init .` | `SkillCred` — resolves `{SKILL_PATH}/.env` |
| `security` | macOS built-in | — | Optional: silent unlock via `keychain set` |

No third-party Python package: `scripts/` uses the standard library only and shells out
to `bw`, so `requirements.txt` is empty by design.

## Node version

`@bitwarden/cli` declares `engines: { node: "~22" }`. On Node 20 `npm install` prints
`EBADENGINE` warnings but installs and runs fine. Upgrade to Node 22 to silence them.

## Where things land

`npm init` installs into the **shared library dir**
(`~/.meta-skills/skills/security/bitwarden/node_modules/`, ~84 MB, gitignored), once per
machine rather than once per project. `bw.py` prefers `node_modules/.bin/bw` and falls
back to any `bw` on `PATH`, so a system-wide install (`brew install bitwarden-cli`) also
works and lets you skip `npm init` entirely.

Runtime state stays in the **registered skill dir** (`CURRENT_SKILL_DIRECTORY`):
`.env`, `.bw_session`, and `.bw-appdata/` — all gitignored, none shared between projects.
