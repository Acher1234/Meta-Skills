# orca-dev-worktree — Commands

`ORCA` = resolved CLI (see `orca-dev` SKILL.md). All commands take `--json`; full
flags: `ORCA worktree <cmd> --help`.

> **Creating a worktree always follows the flow below** — never a bare
> `ORCA worktree create` and stop: submodules go on the same branch, then the
> `.env` files are copied with **`git-worktree-sync`** (mandatory final step).
> Orca creates a clean checkout: ignored files (`.env`, `.claude/skills/*/.env`, …)
> are not there.

## Commands

| Command | Description |
|---------|-------------|
| `ORCA worktree create --name <n> [--repo <sel>] [--branch <b>] [--base-branch <ref>] [--no-parent \| --parent-worktree active]` | Create — **use the flow below** |
| `ORCA worktree list [--repo <sel>] [--limit <n>]` | List Orca worktrees |
| `ORCA worktree show --worktree <sel>` | One worktree (id, path, branch, links) |
| `ORCA worktree current` | Worktree of the current directory |
| `ORCA worktree set --worktree <sel> [--display-name] [--comment] [--workspace-status] [--unread\|--read] [--parent-worktree <sel>\|--no-parent]` | Update Orca metadata |
| `ORCA worktree rm --worktree <sel> [--force]` | Remove from Orca **and git** — confirm first |
| `ORCA worktree ps [--limit <n>] [--agent-wait]` | Orchestration summary across worktrees |
| `ORCA ports [--worktree <sel>] [--all]` | Listening ports tied to a workspace (dev servers) |

Selectors: `id:<repoId>::<path>` (copy the whole `id` from JSON), `name:<display>`,
`path:<abs>`, `branch:<b>`, `issue:<n>`, `active` / `current`.

Card comment at checkpoints: `ORCA worktree set --worktree active --comment "<status>" --json`.

## Create — `/orca-dev_worktree create` (MANDATORY flow)

### 1. Gather context (run, don't ask)

```text
ORCA worktree current --json                        # repo id + current branch, if inside Orca
ORCA repo list --json                               # repos known by Orca (id, path, displayName)
ORCA repo search-refs --repo id:<repoId> --query <text> --limit 20 --json
ORCA worktree list --repo id:<repoId> --json        # existing worktrees
```

### 2. Ask the user (one question each, propose defaults)

1. **Repo** — default: the repo of the current worktree (then `--repo` can be omitted).
2. **Base branch** (`--base-branch`) — default: omit it → repo default base
   (usually `origin/main`). Never base on the current feature branch unless the user
   asks for stacked work / "branch from current".
3. **Name** (`--name`, required) and **branch** (`--branch`, optional — without it
   Orca uses its prefixed default; a taken name gets a numeric suffix).
4. **Lineage** — child of the current worktree (`--parent-worktree active`) or
   independent (`--no-parent`).
5. **Submodules base branch** (only if the repo has `.gitmodules`) — branch each
   submodule is updated from before branching. Default: each submodule's own
   default branch (`origin/HEAD`).
6. **Agent** (optional) — e.g. `claude`, `codex` + a prompt. See step 3: the agent
   is launched **after** the submodules and the `.env` copy.

### 3. Create the worktree (without agent)

```text
ORCA worktree create --repo id:<repoId> --name <name> [--branch <branch>] \
  [--base-branch origin/main] [--no-parent | --parent-worktree active] \
  [--comment "<short status>"] [--reference <issue/PR url>] --json
```

Read from the JSON result the worktree **`id`** (`<repoId>::<path>`) and **`path`**
(`result.worktree.id` / `result.worktree.path`; if missing:
`ORCA worktree show --worktree name:<name> --json`).

Do **not** pass `--agent` here: the agent would start before the `.env` files exist.

### 4. Submodules — same branch everywhere (if `.gitmodules`)

Every submodule must end on the **same branch as the worktree**. For each one
(recursive): init → check out its base branch and `pull --ff-only` (answer of
step 2, else its default branch) → check out the worktree branch (existing local
or `origin/<branch>`) or create it from that base.

```bash
~/.meta-skills/.venv/bin/python ~/.meta-skills/skills/code/git-worktree/scripts/submodules.py --to "<path>" [--sub-base <branch>]
```

```powershell
& "$HOME/.meta-skills/.venv/Scripts/python.exe" "$HOME/.meta-skills/skills/code/git-worktree/scripts/submodules.py" --to "<path>" [--sub-base <branch>]
```

Script from the `git-worktree` skill. It ends with `all submodules on <branch>`; on `NOT on <branch>: …` fix
those submodules (dirty tree, pull conflict) and re-run it. Run this **before**
the `.env` copy (submodule folders must be checked out first).

### 5. MANDATORY — copy the `.env` files (`git-worktree-sync`)

Never skip this step, never report the worktree as ready before it ran. It copies
the `.env` files and the user's extra items (`SYNC_EXTRA`) — set
`CURRENT_SKILL_DIRECTORY` with that skill's Working directory block first. Follow the
[`git-worktree-sync`](../../git-worktree-sync/SKILL.md) skill in **copy** mode:

```bash
~/.meta-skills/.venv/bin/python ~/.meta-skills/skills/code/git-worktree-sync/scripts/worktree_sync.py copy --to "<path>"
```

```powershell
& "$HOME/.meta-skills/.venv/Scripts/python.exe" "$HOME/.meta-skills/skills/code/git-worktree-sync/scripts/worktree_sync.py" copy --to "<path>"
```

Source = main worktree by default.

### 6. Start the agent (if asked in step 2.6)

```text
ORCA agent launch --agent claude --worktree id:<repoId>::<path> --prompt "<task brief>" --json
```

Report `launch.outcome.handle` and `prompt.outcome`. If the reply is lost, retry
with `--retry-launch <operationId>` — never relaunch from scratch.

### 7. Report

Worktree id, path, branch, branch of each submodule, copied `.env` files (names only, never their content),
and the agent handle if any. Optionally set the card comment:
`ORCA worktree set --worktree id:<repoId>::<path> --comment "<status>" --json`.

## Notes

- Confirm before `worktree rm` (and before `--force`).
- `--activate` reveals the new worktree in the Orca app — only if the user wants it.
- Full handoff to another agent: still create → copy `.env` → `agent launch`; do
  not use `orchestration task-create` (see `orca-cli`).
