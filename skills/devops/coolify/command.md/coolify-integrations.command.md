# coolify-integrations — Commands

Git sources (GitHub / GitLab Apps) and external secret managers. Requires a connected context
(`--context "$COOLIFY_CONTEXT"`). All commands support `--help` and `--format json`.

## GitHub Apps

`<app_uuid>` also accepts the numeric ID.

| Command | Description |
|---------|-------------|
| `coolify github list` | GitHub App integrations |
| `coolify github get <app_uuid>` | One GitHub App |
| `coolify github repos <app_uuid>` | Repositories the app can access |
| `coolify github branches <app_uuid> <owner/repo>` | Branches of a repository |
| `coolify github create` | Register an existing GitHub App (`--name`, `--html-url`, `--app-id`, `--installation-id`, `--client-id`, `--client-secret`, `--private-key-uuid` required) |
| `coolify github update <app_uuid>` | Update the given fields |
| `coolify github delete <app_uuid>` | Delete — the app must be unused (`-f` skips the prompt) |

## GitLab Apps

| Command | Description |
|---------|-------------|
| `coolify gitlab list` | GitLab App integrations (team + system-wide) |
| `coolify gitlab get <app_id_or_uuid>` | One GitLab App |
| `coolify gitlab create` | Create (`--name`, `--html-url` required; `--api-url`, `--client-id`, `--client-secret`, `--group-name`, `--redirect-uri`, `--webhook-token`, …) |
| `coolify gitlab update <app_id_or_uuid>` | Update the given fields |
| `coolify gitlab delete <app_id_or_uuid>` | Delete — the app must be unused (`--force` skips the prompt) |

## Secret managers

| Command | Description |
|---------|-------------|
| `coolify integration-token create` | Create and validate a Doppler / Infisical / Vault token (`--provider`, `--name` required; `--metadata <json>`; `--provider-token-stdin`) |
| `coolify app secret-manager set <app_uuid>` | Make an application read its secrets from a manager (`--integration-token <uuid>` required; `--settings <json>`) |

The provider token goes on stdin, never as an argument:
`echo "$DOPPLER_TOKEN" | coolify integration-token create --provider doppler --name prod --provider-token-stdin`

---
