# coolify-projects — Commands

Projects, their environments, the resource inventory, team tags and shared environment variables.
Requires a connected context (`--context "$COOLIFY_CONTEXT"`). All commands support `--help`
and `--format json`.

## Projects and environments

| Command | Description |
|---------|-------------|
| `coolify project list` | List projects |
| `coolify project get <uuid>` | One project and its environments |
| `coolify project create` | Create (`--name` required, `--description`) |
| `coolify project update <uuid>` | Update (`--name`, `--description`) |
| `coolify project delete <uuid>` | Delete a project (`--force` skips the prompt) |
| `coolify project environments list <project_uuid>` | Environments of a project |
| `coolify project environments get <project_uuid> <env>` | One environment with its applications, databases and services (name or UUID) |
| `coolify project environments create <project_uuid>` | Create (`--name` required) |
| `coolify project environments update <project_uuid> <env>` | Update (`--name`, `--description`) |
| `coolify project environments delete <project_uuid> <env>` | Delete (`--force` skips the prompt) |
| `coolify project update-environment <project_uuid> <env>` | Older alias of `environments update` — prefer that one |

## Inventory and tags

| Command | Description |
|---------|-------------|
| `coolify resource list` | Every application, database and service with its status — best first call to find a UUID |
| `coolify tag list` | Team tags |
| `coolify tag create` | Create a tag (`--name`) |
| `coolify tag update <uuid>` | Rename (`--name`) |
| `coolify tag delete <uuid>` | Delete a tag |

## Shared environment variables

Same four commands at four scopes; values are inherited by the resources below the scope.

| Command | Description |
|---------|-------------|
| `coolify shared-env team list` | Team-wide variables |
| `coolify shared-env team create` | Create one |
| `coolify shared-env team update <id>` | Update one |
| `coolify shared-env team delete <id>` | Delete one |
| `coolify shared-env project list <project_uuid>` | Project variables |
| `coolify shared-env project create <project_uuid>` | Create one |
| `coolify shared-env project update <project_uuid> <id>` | Update one |
| `coolify shared-env project delete <project_uuid> <id>` | Delete one |
| `coolify shared-env environment list <project_uuid> <env>` | Environment variables |
| `coolify shared-env environment create <project_uuid> <env>` | Create one |
| `coolify shared-env environment update <project_uuid> <env> <id>` | Update one |
| `coolify shared-env environment delete <project_uuid> <env> <id>` | Delete one |
| `coolify shared-env server list <server_uuid>` | Server variables |
| `coolify shared-env server create <server_uuid>` | Create one |
| `coolify shared-env server update <server_uuid> <id>` | Update one |
| `coolify shared-env server delete <server_uuid> <id>` | Delete one |

`create` / `update` flags: `--key`, `--value`, `--comment`, `--literal`, `--multiline`, `--shown-once`.

---
