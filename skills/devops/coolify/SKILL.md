---
name: coolify
description: >-
  Coolify (cloud or self-hosted) via the official coolify CLI — servers, projects,
  applications, databases, services, deployments, logs, environment variables,
  backups. Loads URL + token from .env into a dedicated CLI context. Use when the
  user mentions Coolify, deploying or restarting an app on Coolify, or invokes /coolify_*.
disable-model-invocation: true
---

### TO COPY

# coolify

Per-workspace registration slice. Credentials live in `{SKILL_PATH}/.env`.

## Working directory

Placeholders changed by `/meta-skills` at copy time (NAME => {PLACEHOLDER}):

IS_GLOBAL => {IS_GLOBAL}
TYPE_OF_AI_TOOLS => {TYPE_OF_AI_TOOLS}
SKILL_PATH => {SKILL_PATH}

Bash / zsh:

```bash
export CURRENT_SKILL_DIRECTORY="{SKILL_PATH}"
eval "$(~/.meta-skills/.venv/bin/python ~/.meta-skills/skills/devops/coolify/scripts/skill_env.py)"
coolify context add "$COOLIFY_CONTEXT" "$COOLIFY_URL" "$COOLIFY_TOKEN" >/dev/null
coolify context update "$COOLIFY_CONTEXT" --url "$COOLIFY_URL" --token "$COOLIFY_TOKEN" >/dev/null
```

PowerShell (Windows):

```powershell
$env:CURRENT_SKILL_DIRECTORY = "{SKILL_PATH}"
& "$HOME/.meta-skills/.venv/Scripts/python.exe" "$HOME/.meta-skills/skills/devops/coolify/scripts/skill_env.py" --shell powershell | Out-String | Invoke-Expression
coolify context add $env:COOLIFY_CONTEXT $env:COOLIFY_URL $env:COOLIFY_TOKEN | Out-Null
coolify context update $env:COOLIFY_CONTEXT --url $env:COOLIFY_URL --token $env:COOLIFY_TOKEN | Out-Null
```

Then **every** command: `coolify --context "$COOLIFY_CONTEXT" --format json …` — never rely on
the default context. Confirm with the user before any write, deploy or delete.

##### END TO COPY

# coolify — Command Index

Router to `coolify` command domains. References live in `command.md/` and `exemple.md/`
under the **shared library** (`~/.meta-skills/skills/devops/coolify/`).

## Prerequisites

Official **`coolify` CLI** on `PATH` + shared venv: `~/.meta-skills/skills/devops/coolify/install.md`.

Credentials in `{SKILL_PATH}/.env` (copy `.env.example`): `COOLIFY_URL`, `COOLIFY_TOKEN`,
`COOLIFY_CONTEXT` (default `skill-coolify`).

## Connect (every session)

1. `eval` `skill_env.py` — checks `.env` and exports the three variables.
2. `context add` creates the context when it is missing (no-op otherwise); `context update`
   then aligns its URL and token with `.env`. Both are needed: `add --force` keeps the old URL.
3. Run commands with `--context "$COOLIFY_CONTEXT"`. The CLI reports connection or token
   errors itself; `coolify --context "$COOLIFY_CONTEXT" context verify` checks on demand.

Exported variables do not survive a new shell: re-run the block (or chain commands in one call).
The token is also stored by the CLI in its per-user `config.json`.

## When to use

Trigger phrases: "deploy on Coolify", "restart the app", "Coolify logs", "add an env var on
Coolify", "back up the database", `/coolify_*`.

Start from `coolify … resource list` to find a UUID. Resources use UUIDs; teams use numeric IDs.

## Domains

| Domain | Scope | Commands |
|--------|-------|----------|
| `coolify-context` | Contexts, CLI version, config path | `command.md/coolify-context.command.md` |
| `coolify-instance` | Teams, audit log, instance email, notifications | `command.md/coolify-instance.command.md` |
| `coolify-servers` | Servers, proxy, registries, destinations, private keys | `command.md/coolify-servers.command.md` |
| `coolify-projects` | Projects, environments, inventory, tags, shared env | `command.md/coolify-projects.command.md` |
| `coolify-apps` | Applications: create, update, lifecycle, logs, previews, tasks | `command.md/coolify-apps.command.md` |
| `coolify-databases` | Databases: create, lifecycle, backups, restore | `command.md/coolify-databases.command.md` |
| `coolify-services` | One-click services and their applications / databases | `command.md/coolify-services.command.md` |
| `coolify-env-storage` | Env vars and storages of apps / databases / services, S3 | `command.md/coolify-env-storage.command.md` |
| `coolify-deploy` | Deploy, deployment logs, cancel, rollback | `command.md/coolify-deploy.command.md` |
| `coolify-integrations` | GitHub / GitLab Apps, secret managers | `command.md/coolify-integrations.command.md` |

Paths are relative to `~/.meta-skills/skills/devops/coolify/`. Workflows →
`exemple.md/coolify-workflows.exemple.md`. Any flag → `coolify <command> --help`.

## Safety

- **Read** (`list`, `get`, `logs`, `verify`): free.
- **Write** (`create`, `update`, `env`, `start`, `stop`, `restart`, `deploy`): confirm first,
  naming the resource and the instance.
- **Destructive** (`delete`, `remove`, `import`): explicit confirmation. Deleting a database or a
  service also deletes its volumes by default. Pass `-f` / `--force` only after the user said
  yes — the interactive prompt would otherwise block.
- **Secrets**: no `-s` / `--show-sensitive` unless asked. Send secrets on stdin
  (`--password-stdin`, `--provider-token-stdin`) or through `env sync -f <file>`, not as arguments.
- **Logs**: use `-n <lines>`; `-f` / `--follow` never returns.
- **Never**: `context use`, `context set-default` (they change the user's default context).
  `coolify update` only when the user asks.
- **Out of scope**: buying servers from a provider (`server hetzner|digitalocean|vultr|hostinger`,
  `cloud-token`, `cloud-init`) and `mcp` — do not run them.
- Never commit `.env`.
