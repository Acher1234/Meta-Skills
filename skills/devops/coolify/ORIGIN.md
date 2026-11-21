# Origin

Coolify **CLI** (`coolify`) — servers, projects, applications, databases, services,
deployments. The skill documents `coolify` commands; `scripts/skill_env.py` exports
`.env`, then SKILL.md saves them as a dedicated CLI context (`coolify context add` / `update`).

- CLI: [coollabsio/coolify-cli](https://github.com/coollabsio/coolify-cli) (MIT)
- Quick reference: [llms.txt](https://github.com/coollabsio/coolify-cli/blob/main/llms.txt)
- Full command and flag catalog: [llms-full.txt](https://github.com/coollabsio/coolify-cli/blob/main/llms-full.txt)
- Releases: [coolify-cli/releases](https://github.com/coollabsio/coolify-cli/releases)
- API spec: [coolify openapi.json](https://github.com/coollabsio/coolify/blob/v4.x/openapi.json)

Command tables written from `llms-full.txt` at tag `v1.11.0`; the CLI is not pinned, so
a newer or older binary may differ — `coolify <command> --help` is authoritative.

Base URL: `<COOLIFY_URL>/api/v1/`  
Auth: `Authorization: Bearer <COOLIFY_TOKEN>` (sent by the CLI from the saved context)
