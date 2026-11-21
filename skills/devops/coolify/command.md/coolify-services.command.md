# coolify-services — Commands

One-click services (WordPress, n8n, Ghost, …) and the applications / databases inside them.
Requires a connected context (`--context "$COOLIFY_CONTEXT"`). All commands support `--help`
and `--format json`. Environment variables and storages: `coolify-env-storage.command.md`.

## Service

| Command | Description |
|---------|-------------|
| `coolify service list` | List services |
| `coolify service get <uuid>` | Service details |
| `coolify service logs <uuid>` | Logs of one sub-resource (`--sub-service-name` required; `-n` lines, `--show-timestamps`) |
| `coolify service create <type>` | Create a one-click service (`--server-uuid`, `--project-uuid` required; `--environment-name` or `--environment-uuid`; `--name`, `--docker-compose <content>`, `--destination-uuid`, `--instant-deploy`, `--tag`). `--list-types` lists the available types |
| `coolify service start <uuid>` | Deploy all containers |
| `coolify service stop <uuid>` | Stop all containers |
| `coolify service restart <uuid>` | Restart all containers |
| `coolify service move <uuid>` | Move to another environment (`--environment-uuid` required) |
| `coolify service clone <uuid>` | Clone to a destination (`--destination`, `--name`, `--clone-volumes`) |
| `coolify service delete <uuid>` | Delete — volumes, configurations and networks included by default (`--delete-volumes=false` … to keep them; `--force` skips the prompt) |
| `coolify service tag list <service_uuid>` | Tags of the service |
| `coolify service tag add <service_uuid> <name>` | Add a tag |
| `coolify service tag remove <service_uuid> <tag_uuid>` | Remove a tag |

## Applications inside a service

| Command | Description |
|---------|-------------|
| `coolify service application list <service_uuid>` | Applications of the service |
| `coolify service application get <service_uuid> <application_uuid>` | One application |
| `coolify service application logs <service_uuid> <application_uuid>` | Logs (`-n` lines, default 100) |
| `coolify service application update <service_uuid> <application_uuid>` | Update (`--url`, `--image`, `--human-name`, `--description`, `--gzip-enabled`, `--stripprefix-enabled`, `--log-drain-enabled`, `--exclude-from-status`, `--force-domain-override`) |
| `coolify service application start <service_uuid> <application_uuid>` | Start or redeploy (`--force`, `--latest`) |
| `coolify service application restart <service_uuid> <application_uuid>` | Restart |
| `coolify service application stop <service_uuid> <application_uuid>` | Stop |

## Databases inside a service

| Command | Description |
|---------|-------------|
| `coolify service database list <service_uuid>` | Databases of the service |
| `coolify service database get <service_uuid> <database_uuid>` | One database |
| `coolify service database logs <service_uuid> <database_uuid>` | Logs (`-n` lines) |
| `coolify service database update <service_uuid> <database_uuid>` | Update (`--image`, `--human-name`, `--description`, `--public`, `--public-port`, `--public-port-timeout`, `--log-drain-enabled`, `--exclude-from-status`) |
| `coolify service database start <service_uuid> <database_uuid>` | Start or redeploy (`--force`, `--latest`) |
| `coolify service database restart <service_uuid> <database_uuid>` | Restart |
| `coolify service database stop <service_uuid> <database_uuid>` | Stop |
| `coolify service database import start <service_uuid> <database_uuid>` | Import a backup — same sources and options as `coolify database import start` |
| `coolify service database import upload <service_uuid> <database_uuid> <file>` | Upload a backup file and print its upload ID |
| `coolify service database import status <service_uuid> <database_uuid> <activity_id>` | Import status (`--wait`) |

## Scheduled tasks

| Command | Description |
|---------|-------------|
| `coolify service task list <service_uuid>` | Scheduled tasks |
| `coolify service task create <service_uuid>` | Create (`--name`, `--command`, `--frequency <cron>` required; `--container`, `--enabled`, `--timeout`) |
| `coolify service task update <service_uuid> <task_uuid>` | Update the given flags |
| `coolify service task delete <service_uuid> <task_uuid>` | Delete a task |
| `coolify service task execute <service_uuid> <task_uuid>` | Run a task now |
| `coolify service task executions <service_uuid> <task_uuid>` | Past executions |
| `coolify service execute-task <service_uuid> <task_uuid>` | Same as `task execute` |

---
