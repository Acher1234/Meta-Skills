# Origin

Bitwarden Password Manager **CLI** (`bw`) — vault read/write and Send. The skill
documents `bw` commands; `scripts/skill_env.py` exports `.env`, then SKILL.md
runs `bw login --apikey` / `bw unlock`.

- CLI: [bitwarden.com/help/cli](https://bitwarden.com/help/cli/)
- Personal API key: [bitwarden.com/help/personal-api-key](https://bitwarden.com/help/personal-api-key/)
- Send: [bitwarden.com/help/send-cli](https://bitwarden.com/help/send-cli/)
- npm: [@bitwarden/cli](https://www.npmjs.com/package/@bitwarden/cli)

Binary pinned in `package.json` → `node_modules/.bin/bw` via `install.sh npm init`.

Auth: `bw login --apikey` only when `unauthenticated`, then
`bw unlock --passwordenv BW_PASSWORD`.
