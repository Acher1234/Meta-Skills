## Example Workflows

Every command runs after the connect block of `SKILL.md`.

### Deploy an application and read its logs

```bash
coolify --context "$COOLIFY_CONTEXT" --format json resource list          # find the name / UUID
coolify --context "$COOLIFY_CONTEXT" --format json deploy name my-api     # returns the deployment UUID
coolify --context "$COOLIFY_CONTEXT" --format json deploy get <deployment_uuid>
coolify --context "$COOLIFY_CONTEXT" app deployments logs <app_uuid> -n 200
```

**When user says "deploy my-api on Coolify"**, this skill should:
1. Find the resource with `resource list` and confirm the exact name and instance
2. Run `deploy name` after the user confirms
3. Poll `deploy get` until it is finished, then show the end of `app deployments logs` (no `-f`)

### Sync a `.env` file to an application

```bash
coolify --context "$COOLIFY_CONTEXT" --format json app env list <app_uuid>
coolify --context "$COOLIFY_CONTEXT" app env sync <app_uuid> -f .env.production
coolify --context "$COOLIFY_CONTEXT" app restart <app_uuid>
```

`sync` creates and updates, never deletes. Tell the user which keys exist only on Coolify, and
ask before the restart.

### Back up a database, then restore it

```bash
coolify --context "$COOLIFY_CONTEXT" --format json database backup list <database_uuid>
coolify --context "$COOLIFY_CONTEXT" database backup trigger <database_uuid> <backup_uuid>
coolify --context "$COOLIFY_CONTEXT" --format json database backup executions <database_uuid> <backup_uuid>
coolify --context "$COOLIFY_CONTEXT" database import start <database_uuid> --file ./dump.sql.gz --wait
```

A restore overwrites data: name the target database and instance, and wait for an explicit yes.

### Create an application from a public repository

```bash
coolify --context "$COOLIFY_CONTEXT" --format json server list
coolify --context "$COOLIFY_CONTEXT" --format json project list
coolify --context "$COOLIFY_CONTEXT" app create public \
  --server-uuid <server_uuid> --project-uuid <project_uuid> --environment-name production \
  --git-repository https://github.com/owner/repo --git-branch main \
  --build-pack nixpacks --ports-exposes 3000 --domains https://app.example.com
```

Add `--instant-deploy` only when the user wants the first deployment right away.
