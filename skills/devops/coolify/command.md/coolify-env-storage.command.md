# coolify-env-storage — Commands

Environment variables and storages have the same commands on applications, databases and services.
Below, `<res>` is `app`, `database` or `service`, and `<uuid>` is that resource's UUID.
Requires a connected context (`--context "$COOLIFY_CONTEXT"`). All commands support `--help`
and `--format json`. A changed variable or storage applies on the next deploy / restart.

## Environment variables

| Command | Description |
|---------|-------------|
| `coolify <res> env list <uuid>` | List variables — values are masked unless `-s` (apps: `--preview`, `--all`) |
| `coolify <res> env get <uuid> <env_uuid_or_key>` | One variable |
| `coolify <res> env create <uuid>` | Create (`--key`, `--value` required) |
| `coolify <res> env update <uuid> <env_uuid_or_key>` | Update (`--value` required; `--key` renames) |
| `coolify <res> env delete <uuid> <env_uuid>` | Delete (`--force` skips the prompt) |
| `coolify <res> env sync <uuid>` | Create / update from a file (`-f <path>` required) — never deletes variables missing from the file |

Flags of `create` / `update` / `sync`:

| Resource | Flags |
|----------|-------|
| `app` | `--build-time`, `--runtime` (both default true), `--preview`, `--comment`, `--is-literal`, `--is-multiline` |
| `service` | Same as `app` without `--preview` |
| `database` | `--comment`, `--is-literal`, `--is-multiline`, `--is-shown-once` |

Prefer `env sync -f <file>` for secrets: a `--value` argument is visible in the process list.

## Storages

| Command | Description |
|---------|-------------|
| `coolify <res> storage list <uuid>` | Persistent volumes and file storages |
| `coolify <res> storage create <uuid>` | Create (`--type persistent\|file`, `--mount-path` required; persistent: `--name`, `--host-path`; file: `--content`, `--is-directory`, `--fs-path`; services also need `--resource-uuid`) |
| `coolify <res> storage update <uuid>` | Update (`--uuid <storage_uuid>` and `--type` required; `--mount-path`, `--name`, `--host-path`, `--content`, `--is-preview-suffix-enabled`) |
| `coolify <res> storage delete <uuid> <storage_uuid>` | Delete a storage — the data goes with it |
| `coolify <res> storage set-backup <uuid> <storage_uuid>` | Create or replace the volume backup schedule (`--frequency <cron>` required; `--enabled`, `--save-s3`, `--s3-storage-uuid`, `--retention-*-locally`, `--retention-*-s3`, `--stop-during-backup`, `--timeout`, `--disable-local-backup`) |
| `coolify <res> storage run-backup <uuid> <storage_uuid>` | Run the volume backup now |
| `coolify <res> storage delete-backup <uuid> <storage_uuid>` | Delete the backup schedule |
| `coolify <res> run-storage-backup <uuid> <storage_uuid>` | Same as `storage run-backup` |

## S3 storages

Backup targets referenced by `--s3-storage-uuid`.

| Command | Description |
|---------|-------------|
| `coolify s3 list` | List S3 storages |
| `coolify s3 get <uuid>` | One S3 storage |
| `coolify s3 create` | Create (`--name`, `--endpoint`, `--bucket`, `--region`, `--key`, `--secret`, `--description`, `--usable`) |
| `coolify s3 update <uuid>` | Update the given flags |
| `coolify s3 validate <uuid>` | Test the connection |
| `coolify s3 delete <uuid>` | Delete an S3 storage |

---
