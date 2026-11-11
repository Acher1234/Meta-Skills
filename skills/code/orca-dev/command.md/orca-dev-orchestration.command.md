# orca-dev-orchestration — Commands

`ORCA` = resolved CLI (see `orca-dev` SKILL.md). Add `--json` everywhere; full
flags: `ORCA <command> --help`.

Supervised multi-agent work only (coordinator + workers, task DAG, gates). For a
plain handoff use `orca-dev-agent.command.md`. Detailed rules:
`ORCA skills get orchestration` — load it before coordinating.

## Runs & messages

| Command | Description |
|---------|-------------|
| `ORCA orchestration run-create` / `run-use` / `run-current` / `run-list` / `run-show` | Create, resume (coordinator only), inspect Runs |
| `ORCA orchestration send` | Inter-agent message |
| `ORCA orchestration check [--peek] [--format]` | Read the bound Run mailbox |
| `ORCA orchestration ask` / `reply` | Blocking question to the coordinator / answer |
| `ORCA orchestration inbox` | All messages across recipients |

## Tasks & dispatch

| Command | Description |
|---------|-------------|
| `ORCA orchestration task-create` / `task-list` / `task-update` | Task DAG |
| `ORCA orchestration dispatch` / `dispatch-show` | Dispatch a task to a terminal |
| `ORCA orchestration gate-create` / `gate-resolve` / `gate-list` | Decision gates |
| `ORCA orchestration reset` | Reset orchestration state — confirm first |

## Supervised workers

| Command | Description |
|---------|-------------|
| `ORCA orchestration worker-start` | Start a worker (local or paired server) |
| `ORCA orchestration worker-show` / `worker-read` / `worker-list` | Inspect |
| `ORCA orchestration worker-stop` / `worker-abandon` | Fence a dispatch / uncertain worker |
| `ORCA orchestration worker-release` / `worker-retain` | Free or keep the worker terminal |

A worker in a **new** worktree: create it with the worktree flow (submodules + `.env`
sync) before `worker-start`.
