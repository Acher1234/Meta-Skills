# coolify-deploy — Commands

Trigger, follow, cancel and roll back deployments. Requires a connected context
(`--context "$COOLIFY_CONTEXT"`). All commands support `--help` and `--format json`.
Confirm with the user before every deploy, cancel or rollback.

| Command | Description |
|---------|-------------|
| `coolify deploy name <resource_name>` | Deploy a resource by name |
| `coolify deploy uuid <uuid>` | Deploy a resource by UUID |
| `coolify deploy batch <name1,name2,…>` | Deploy several resources by name |
| `coolify deploy list` | Deployments currently running |
| `coolify deploy get <uuid>` | One deployment (status, commit) |
| `coolify deploy cancel <uuid>` | Cancel a running deployment (`-f` skips the prompt) |
| `coolify app deployments list <app_uuid>` | Deployment history of an application |
| `coolify app deployments logs <app_uuid> [deployment_uuid]` | Build / deploy logs — latest deployment if no UUID (`-n` lines, 0 = all; `--debuglogs`; `-f` follows) |
| `coolify app rollback images <uuid>` | Images available for rollback |
| `coolify app rollback run <uuid>` | Roll an application back (`--commit <sha>`) |

`deploy name|uuid|batch` flags: `--force` (rebuild without cache), `--pull-request-id <id>`
(preview deployment), `--docker-tag <tag>` (needs Coolify `4.0.0-beta.471+`).

After a deploy, poll `coolify deploy get <uuid>` or read `app deployments logs` with `-n`;
avoid `-f`, which never returns.

---
