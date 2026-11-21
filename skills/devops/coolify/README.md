# coolify

[Coolify](https://coolify.io) (cloud or self-hosted) via the official
[`coolify`](https://github.com/coollabsio/coolify-cli) CLI.
Command index: [`SKILL.md`](SKILL.md). Domains under `command.md/`, workflows under `exemple.md/`.

1. Install the CLI and the shared venv: [`install.md`](install.md).
2. Copy `.env.example` to `.env` next to the registered skill and fill `COOLIFY_URL`,
   `COOLIFY_TOKEN` (keep or change `COOLIFY_CONTEXT`).
3. Connect: see [`SKILL.md`](SKILL.md) — `eval skill_env.py`, then `coolify context add` / `update`.
