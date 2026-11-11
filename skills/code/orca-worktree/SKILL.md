---
name: orca-worktree
description: >-
  Create an Orca-managed worktree with the `orca worktree create` CLI (repo,
  base branch, branch name, parent lineage, optional agent + prompt), puts every
  submodule on the same branch, then — as a mandatory final step — copy the project's .env files into it with the
  `git-worktree-sync` skill. Use when the user asks for an "Orca worktree",
  "nouveau workspace Orca", "worktree Orca avec un agent", or invokes
  /orca-worktree_*. Plain-git variant: `git-worktree`.
disable-model-invocation: true
---

### TO COPY

# orca-worktree

Per-workspace registration slice. No credentials.

## Working directory

Placeholders changed by `/meta-skills` at copy time (NAME => {PLACEHOLDER}):

IS_GLOBAL => {IS_GLOBAL}
TYPE_OF_AI_TOOLS => {TYPE_OF_AI_TOOLS}
SKILL_PATH => {SKILL_PATH}

Bash / zsh:

```bash
export CURRENT_SKILL_DIRECTORY="{SKILL_PATH}"
```

PowerShell (Windows):

```powershell
$env:CURRENT_SKILL_DIRECTORY = "{SKILL_PATH}"
```

##### END TO COPY

# orca-worktree

## When to use

Create a worktree that Orca tracks (workspace card, terminals, lineage, agents)
instead of a raw `git worktree add`. Trigger phrases: "Orca worktree", "crée un
workspace Orca", "worktree Orca avec claude/codex", `/orca-worktree_*`.

> **Final step is MANDATORY:** every worktree created with this skill must then
> receive the project's `.env` files through the **`git-worktree-sync`** skill
> (step 5). Orca creates a clean checkout: ignored files (`.env`,
> `.claude/skills/*/.env`, …) are not there.

## Resolve the Orca CLI (once per session)

Same rule as the `orca-cli` skill — written `ORCA` below, substitute it:

- `$ORCA_CLI_COMMAND` if set;
- else `orca-dev` in an Orca dev checkout (`$ORCA_DEV_REPO_ROOT` set);
- else on Linux **outside** an Orca terminal: `orca-ide` — never bare `orca`
  there (`/usr/bin/orca` is the GNOME screen reader);
- else `orca`.

If the executable fails, report the exact error and stop. If Orca is not running:
`ORCA open --json`, then retry. For flags not covered here: `ORCA worktree create --help`
or `ORCA skills get orca-cli`.

## Slash commands

| Slash | CLI | Description |
|-------|-----|-------------|
| `/orca-worktree_create` | `ORCA worktree create … --json` + `worktree-sync.sh copy` | Ask, create, then copy `.env` |
| `/orca-worktree_list` | `ORCA worktree list --repo id:<repoId> --json` | List Orca worktrees of a repo |
| `/orca-worktree_current` | `ORCA worktree current --json` | Show the enclosing worktree |
| `/orca-worktree_remove` | `ORCA worktree rm --worktree id:<repoId>::<path> --json` | Remove (confirm first) |

## How to run — `/orca-worktree_create`

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
SYNC=~/.meta-skills/skills/code/git-worktree-sync/scripts/worktree-sync.sh
bash "$SYNC" submodules --to "<path>" [--sub-base <branch>]
```

The script ends with `all submodules on <branch>`; on `NOT on <branch>: …` fix
those submodules (dirty tree, pull conflict) and re-run it. Run this **before**
the `.env` copy (submodule folders must be checked out first).

### 5. MANDATORY — copy the `.env` files (`git-worktree-sync`)

Never skip this step, never report the worktree as ready before it ran. Follow the
[`git-worktree-sync`](../git-worktree-sync/SKILL.md) skill in **copy** mode:

```bash
SYNC=~/.meta-skills/skills/code/git-worktree-sync/scripts/worktree-sync.sh
bash "$SYNC" copy --to "<path>"          # source = main worktree by default
```

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
