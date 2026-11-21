# coolify-databases — Commands

Standalone databases: create, lifecycle, scheduled backups, restore.
Requires a connected context (`--context "$COOLIFY_CONTEXT"`). All commands support `--help`
and `--format json`. Environment variables, storages and S3: `coolify-env-storage.command.md`.

## Read

| Command | Description |
|---------|-------------|
| `coolify database list` | List databases |
| `coolify database get <uuid>` | Database details (passwords need `--format json -s`) |
| `coolify database logs <uuid>` | Logs (`-n` lines, `--show-timestamps`) |

## Create and change

| Command | Description |
|---------|-------------|
| `coolify database create <type>` | Create — types `postgresql`, `mysql`, `mariadb`, `mongodb`, `redis`, `keydb`, `clickhouse`, `dragonfly`, `sqlite` (`--server-uuid`, `--project-uuid` required; `--environment-name` or `--environment-uuid`; `--name`, `--image`, `--instant-deploy`, `--is-public`, `--public-port`, `--limits-memory`, `--limits-cpus`, engine credentials such as `--postgres-user`) |
| `coolify database update <uuid>` | Update (`--name`, `--description`, `--image`, `--is-public`, `--public-port`, `--limits-memory`, `--limits-cpus`, `--sqlite-databases`) |
| `coolify database start <uuid>` | Start |
| `coolify database stop <uuid>` | Stop |
| `coolify database restart <uuid>` | Restart |
| `coolify database move <uuid>` | Move to another environment (`--environment-uuid` required) |
| `coolify database clone <uuid>` | Clone to a destination (`--destination`, `--name`, `--clone-volumes`) |
| `coolify database delete <uuid>` | Delete — **volumes, configurations and networks are deleted by default** (`--delete-volumes=false`, `--delete-configurations=false`, `--delete-connected-networks=false`, `--docker-cleanup=false` to keep them) |
| `coolify database tag list <database_uuid>` | Tags of the database |
| `coolify database tag add <database_uuid> <name>` | Add a tag |
| `coolify database tag remove <database_uuid> <tag_uuid>` | Remove a tag |

## Scheduled backups

| Command | Description |
|---------|-------------|
| `coolify database backup list <database_uuid>` | Backup configurations |
| `coolify database backup create <database_uuid>` | Create one (`--frequency <cron>`, `--enabled`, `--save-s3`, `--s3-storage-uuid`, `--databases-to-backup`, `--dump-all`, `--retention-*-locally`, `--retention-*-s3`, `--timeout`, `--disable-local-backup`) |
| `coolify database backup update <database_uuid> <backup_uuid>` | Update the given flags |
| `coolify database backup trigger <database_uuid> <backup_uuid>` | Run a backup now |
| `coolify database backup executions <database_uuid> <backup_uuid>` | Past executions |
| `coolify database backup delete-execution <database_uuid> <backup_uuid> <execution_uuid>` | Delete one execution (`--delete-s3` also removes the file from S3) |
| `coolify database backup delete <database_uuid> <backup_uuid>` | Delete a configuration (`--delete-s3` also removes its files from S3) |

## Restore (import)

| Command | Description |
|---------|-------------|
| `coolify database import start <database_uuid>` | Import a backup — exactly one source: `--file <path>`, `--upload-id <id>`, `--s3-storage-uuid <uuid> --s3-path <path>`, or `--server-path <path>` (token needs `deploy`) |
| `coolify database import upload <database_uuid> <file>` | Upload a local file (max 10 GiB) and print its upload ID |
| `coolify database import status <database_uuid> <activity_id>` | Status and output of an import (`--wait`) |

`import start` options: `--wait` (non-zero exit on failure, `--poll-interval 3s`), `--dump-all`,
`--replace-existing` and `--keep-owners` (PostgreSQL), `--restore-mysql-users` (MySQL / MariaDB),
`--sqlite-database <file>`. An import overwrites data — confirm the target database first.

---
