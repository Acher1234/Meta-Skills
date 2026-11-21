# coolify-apps — Commands

Applications: create, configure, lifecycle, logs, previews, scheduled tasks.
Requires a connected context (`--context "$COOLIFY_CONTEXT"`). All commands support `--help`
and `--format json`. Environment variables and storages: `coolify-env-storage.command.md`.
Deployments and rollback: `coolify-deploy.command.md`.

## Read

| Command | Description |
|---------|-------------|
| `coolify app list` | List applications |
| `coolify app get <uuid>` | Application details |
| `coolify app logs <uuid>` | Runtime logs (`-n` lines, default 100; `--show-timestamps`; `--service <name>` for compose apps; `-f` follows) |

## Create

Common required flags: `--server-uuid`, `--project-uuid`, `--environment-name` (or `--environment-uuid`).
Common optional flags: `--name`, `--description`, `--domains`, `--destination-uuid`, `--instant-deploy`,
`--limits-memory`, `--limits-cpus`, `--health-check-enabled`, `--health-check-path`, `--tag` / `--tags`.

| Command | Description |
|---------|-------------|
| `coolify app create public` | From a public git repository (`--git-repository`, `--git-branch`, `--build-pack nixpacks\|static\|dockerfile\|dockercompose`, `--ports-exposes` required) |
| `coolify app create github` | From a private repository through a GitHub App — same flags plus `--github-app-uuid`; `--git-repository owner/repo` |
| `coolify app create deploy-key` | From a private repository through an SSH deploy key — same flags plus `--private-key-uuid`; `--git-repository git@host:owner/repo.git` |
| `coolify app create dockerfile` | From Dockerfile content (`--dockerfile` required) |
| `coolify app create dockerimage` | From a registry image (`--docker-registry-image-name`, `--ports-exposes` required; `--docker-registry-image-tag`) |

Git variants also take `--base-directory`, `--publish-directory`, `--build-command`, `--install-command`,
`--start-command`, `--git-commit-sha`, and repeatable `--compose-domain <service>=<url>[,<url>]`.

## Change

| Command | Description |
|---------|-------------|
| `coolify app update <uuid>` | Update only the given flags (`--name`, `--domains`, `--git-branch`, `--git-repository`, `--build-command`, `--start-command`, `--docker-image`, `--docker-tag`, `--ports-exposes`, `--compose-domain` — replaces the mapping, …) |
| `coolify app start <uuid>` | Start = queue a deployment (`--force`, `--instant-deploy`) |
| `coolify app stop <uuid>` | Stop the application |
| `coolify app restart <uuid>` | Restart the application |
| `coolify app move <uuid>` | Move to another environment (`--environment-uuid` required) |
| `coolify app clone <uuid>` | Clone to a destination (`--destination`, `--name`, `--clone-volumes`) |
| `coolify app delete <uuid>` | Delete — cannot be undone (`-f` skips the prompt) |

## Destinations and tags

| Command | Description |
|---------|-------------|
| `coolify app destinations list <uuid>` | Destinations the application is attached to |
| `coolify app destinations add <uuid>` | Attach a destination (`--destination`) |
| `coolify app destinations remove <uuid> <destination_uuid>` | Detach a destination |
| `coolify app tag list <app_uuid>` | Tags of the application |
| `coolify app tag add <app_uuid> <name>` | Add a tag |
| `coolify app tag remove <app_uuid> <tag_uuid>` | Remove a tag |

## Preview deployments

| Command | Description |
|---------|-------------|
| `coolify app previews list <app_uuid>` | Previews, newest pull request first |
| `coolify app previews get <app_uuid> <pr_id>` | One preview |
| `coolify app previews create <app_uuid> <pr_id>` | Open or redeploy a preview (`--git-type github\|gitlab\|gitea\|bitbucket`, `--commit`, `--docker-tag`, `--url`, `--force`, `--no-deploy`) |
| `coolify app previews update <app_uuid> <pr_id>` | Replace its domains (`--domains`, `--compose-domain`, `--force-domain-override`) |
| `coolify app previews logs <app_uuid> <pr_id>` | Runtime logs of a preview (`-n`, `--show-timestamps`, `--service`, `-f`) |
| `coolify app previews delete <app_uuid> <pr_id>` | Delete a preview (`--force` skips the prompt) |

## Scheduled tasks

| Command | Description |
|---------|-------------|
| `coolify app task list <app_uuid>` | Scheduled tasks |
| `coolify app task create <app_uuid>` | Create (`--name`, `--command`, `--frequency <cron>` required; `--container`, `--enabled`, `--timeout`) |
| `coolify app task update <app_uuid> <task_uuid>` | Update the given flags |
| `coolify app task delete <app_uuid> <task_uuid>` | Delete a task |
| `coolify app task execute <app_uuid> <task_uuid>` | Run a task now |
| `coolify app task executions <app_uuid> <task_uuid>` | Past executions |
| `coolify app execute-task <app_uuid> <task_uuid>` | Same as `task execute` |

---
