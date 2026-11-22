# gh-cli-actions — Commands

`gh` 2.103.0. Flags not listed: `gh <command> --help`. Rules: `gh-cli` SKILL.md.
All accept `-R OWNER/REPO`.

## Workflows

`<workflow>` = id, name or file name (`ci.yml`).

| Command | Description |
|---------|-------------|
| `gh workflow list [-a] [--json id,name,path,state]` | Workflows (`-a` includes disabled ones) |
| `gh workflow view [<workflow>] [-r <ref>] [-y]` | Summary and recent runs (`-y` = print the YAML) |
| `gh workflow run <workflow> [-r <branch\|tag>] [-f <key>=<value>]…` | Trigger a `workflow_dispatch` — confirm first |
| `echo '{"k":"v"}' \| gh workflow run <workflow> --json` | Same, inputs as JSON on stdin |
| `gh workflow enable <workflow>` / `gh workflow disable <workflow>` | Enable / disable — confirm first |

`HTTP 422: Workflow does not have 'workflow_dispatch' trigger` → it cannot be
started by hand; read the workflow file, do not retry. `workflow run` prints the
new run URL when available; otherwise find the run with
`gh run list -w <workflow> -L 1 --json databaseId,status`.

## Runs

| Command | Description |
|---------|-------------|
| `gh run list [-w <workflow>] [-b <branch>] [-c <sha>] [-e <event>] [-s <status>] [-u <user>] [--created <date>] [-L <n>] [--json <fields>]` | Recent runs (default 20) |
| `gh run view <run-id> [-v] [--json <fields>]` | Summary (`-v` shows job steps) |
| `gh run view <run-id> --log-failed` | Logs of the failed steps only — start here to debug CI |
| `gh run view <run-id> --log [-j <job-id>]` | Full logs of the run or of one job (can be very long) |
| `gh run view <run-id> -a <attempt>` / `--exit-status` | A specific attempt / non-zero exit if the run failed |
| `gh run watch <run-id> [--exit-status] [--compact] [-i <sec>]` | Block until the run ends — set a command timeout |
| `gh run download [<run-id>] [-n <artifact-name>]… [-p <glob>]… [-D <dir>]` | Download artifacts |
| `gh run rerun <run-id> [--failed] [-j <job-id>] [-d]` | Rerun all / failed jobs / one job (`-d` = debug logging) — confirm first |
| `gh run cancel <run-id> [--force]` | Cancel — confirm first |
| `gh run delete <run-id>` | Delete the run — confirm first |

Always pass `<run-id>`: without it `gh` opens a picker. `-s` values: `queued`,
`in_progress`, `completed`, `success`, `failure`, `cancelled`, `skipped`,
`timed_out`, `action_required`, `waiting`, … Run fields: `databaseId`, `status`,
`conclusion`, `workflowName`, `displayTitle`, `headBranch`, `headSha`, `event`,
`attempt`, `createdAt`, `url`, `jobs` (`run view` only).

CI of a PR: `gh pr checks <pr>` gives the links; the run id is in the link.

## Caches

| Command | Description |
|---------|-------------|
| `gh cache list [-k <key-prefix>] [-r <ref>] [-S created_at\|last_accessed_at\|size_in_bytes] [-O asc\|desc] [-L <n>] [--json <fields>]` | Actions caches |
| `gh cache delete <cache-id\|cache-key> [-r <ref>]` | Delete one — confirm first |
| `gh cache delete --all [-r <ref>] [--succeed-on-no-caches]` | Delete all (of a ref) — confirm first |

`<ref>` = `refs/heads/<branch>` or `refs/pull/<n>/merge`.

## Secrets

Scope flags: none = repository · `-e <env>` = environment · `-o <org>` =
organization · `-u` = user (Codespaces). `-a actions|agents|codespaces|dependabot`
selects the application (default `actions`).

| Command | Description |
|---------|-------------|
| `gh secret list [scope] [-a <app>] [--json <fields>]` | Names and dates only — values are never readable |
| `gh secret set <name> [scope] [-a <app>] < <file>` | Set from stdin (keeps the value out of the command line) |
| `gh secret set <name> -b "$ENV_VAR" [scope]` | Set from an environment variable — never a literal value |
| `gh secret set -f <dotenv-file> [scope]` | Set every `KEY=value` of a dotenv file |
| `gh secret set <name> -o <org> -v all\|private\|selected [-r <repos>] [--no-repos-selected]` | Organization secret and its visibility |
| `gh secret delete <name> [scope] [-a <app>]` | Delete — confirm first |

## Variables

Scope flags: none = repository · `-e <env>` · `-o <org>`.

| Command | Description |
|---------|-------------|
| `gh variable list [scope] [--json <fields>]` | Variables and values |
| `gh variable get <name> [scope]` | One value |
| `gh variable set <name> -b "<value>" [scope]` / `-f <dotenv-file>` | Create or update — confirm first |
| `gh variable set <name> -o <org> -v all\|private\|selected [-r <repos>]` | Organization variable and its visibility |
| `gh variable delete <name> [scope]` | Delete — confirm first |

## Debug a failing CI

```bash
gh run list -b <branch> -L 5 --json databaseId,workflowName,status,conclusion
gh run view <run-id> --json jobs --jq '.jobs[] | select(.conclusion=="failure") | {name, databaseId}'
gh run view <run-id> --log-failed
```
