# orca-dev-agent — Commands

`ORCA` = resolved CLI (see `orca-dev` SKILL.md). Add `--json` everywhere; full
flags: `ORCA <command> --help`.

## Start an agent

| Command | Description |
|---------|-------------|
| `ORCA agent launch --agent <id> [--worktree <sel>] [--prompt "<brief>"] [--model <id>] [--effort <lvl>] [--surface chat\|terminal] [--focus]` | Agent in an **existing** worktree (current one if `--worktree` omitted) |
| `ORCA worktree create --name <n> --agent <id> --prompt "<brief>"` | New checkout + agent — prefer the worktree flow (`orca-dev-worktree.command.md`), then `agent launch` |

Agent ids: `claude`, `codex`, `omp`, `pi`, `grok`, … Read `result.launch`:
`outcome.kind` (chat / terminal), `outcome.handle` (the **only** handle to use),
`prompt.outcome` (`journaled` / `handed-to-terminal` = brief delivered).
Lost reply → same command + `--retry-launch <operationId>`, never a fresh launch.

## Full handoff (give the task to another agent)

1. New worktree via the worktree flow (`--no-parent`, no `--base-branch` unless stacked work).
2. `ORCA agent launch --agent <id> --worktree id:<repoId>::<path> --prompt "<brief>"`.
3. Report worktree id + handle, then stop — do not wait for it to finish, do not use
   `orchestration task-create` (that is supervised work: `orca-dev-orchestration.command.md`).

## Review / issue references

| Command | Description |
|---------|-------------|
| `ORCA reference list --worktree <sel>` | Linked PRs / issues |
| `ORCA reference add <url-or-jira-key>… --worktree <sel> [--reference-site <id>]` | Attach |
| `ORCA reference remove <url> --worktree <sel>` / `--key <key>` | Detach |
| `ORCA reference find <url-or-key> [--repo] [--worktree] [--limit]` | Workspaces + agents linked to it |

## Agent session search

| Command | Description |
|---------|-------------|
| `ORCA search "<query>" [--scope conversation\|all] [--agent <id>] [--path <p>] [--since <iso>] [--sort relevance\|newest] [--limit <n>]` | Full-text search of agent sessions |
| `ORCA search --index-status` | Index state |
