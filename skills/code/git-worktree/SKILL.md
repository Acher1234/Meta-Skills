---
name: git-worktree
description: >-
  Create, list and remove git worktrees with plain git commands. Asks which
  branch to base the worktree on, the new branch name and the target folder.
  Use when the user asks to "create a worktree", "nouveau worktree", "work tree
  sur la branche X", or invokes /git-worktree_*. Then puts every submodule on
  the same branch and, as a mandatory final step, copies the .env files with
  the `git-worktree-sync` skill.
disable-model-invocation: true
---

### TO COPY

# git-worktree

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

# git-worktree

## When to use

Create an isolated checkout of the repo (a **worktree**) to work on another
branch in parallel, without stashing or cloning again. Pure `git` — no script.

Trigger phrases: "create a worktree", "crée un worktree", "work tree basé sur
main", `/git-worktree_*`.

> **Final step is MANDATORY:** every worktree created with this skill must then
> receive the project's `.env` files through the **`git-worktree-sync`** skill
> (step 6). Plain `git worktree add` never copies ignored files, so without it the
> skills registered in the project (`.claude/skills/*/.env`, …) have no credentials.

## Slash commands

| Slash | Command | Description |
|-------|---------|-------------|
| `/git-worktree_create` | `git worktree add …` | Ask base / branch / folder, then create |
| `/git-worktree_list` | `git worktree list` | List worktrees |
| `/git-worktree_remove` | `git worktree remove <path>` | Remove a worktree (confirm first) |
| `/git-worktree_prune` | `git worktree prune` | Clean stale worktree metadata |

## How to run — `/git-worktree_create`

### 1. Gather context (run, don't ask)

```bash
git rev-parse --show-toplevel            # repo root
git branch --show-current                # current branch
git fetch --prune origin                 # refresh remote branches
git branch --format='%(refname:short)'   # local branches
git branch -r --format='%(refname:short)' | grep -v HEAD   # remote branches
git worktree list                        # existing worktrees
```

### 2. Ask the user (one question each, propose defaults)

1. **Base branch** — which branch/commit the worktree starts from.
   Default: the repo's main branch (`origin/main`, else `main`/`master`); offer
   the current branch and the list from step 1.
2. **Branch name** for the worktree:
   - a **new** branch (e.g. `feat/xyz`), created from the base; or
   - an **existing** branch (local or `origin/…`) to check out as-is; or
   - **detached** (no branch — read-only exploration).
3. **Folder** — where the worktree lives. Default:
   `<repo-root>/../<repo-name>.worktrees/<branch-with-/-replaced-by-->`.
   The folder must not exist (or be empty).
4. **Submodules base branch** (only if the repo has `.gitmodules`) — branch each
   submodule is updated from before branching. Default: each submodule's own
   default branch (`origin/HEAD`).

### 3. Create

Pick the command that matches the answers:

```bash
REPO=$(git rev-parse --show-toplevel)
WT_PATH="$REPO/../$(basename "$REPO").worktrees/feat-xyz"   # step 2.3

# a) NEW branch from a base
git worktree add -b feat/xyz "$WT_PATH" origin/main

# b) EXISTING local branch
git worktree add "$WT_PATH" feat/xyz

# c) EXISTING remote-only branch -> local tracking branch
git worktree add --track -b feat/xyz "$WT_PATH" origin/feat/xyz

# d) DETACHED at a ref / commit
git worktree add --detach "$WT_PATH" v1.2.0
```

Notes:

- A branch can be checked out in **only one** worktree. If git answers
  `'feat/xyz' is already used by worktree at …`, offer to reuse that worktree or
  pick another branch name. Never use `--force` without asking.
- Repo with submodules (`.gitmodules`): step 5 is mandatory.
- Git LFS: `git -C "$WT_PATH" lfs pull` if the repo uses LFS.

### 4. Verify

```bash
git worktree list
git -C "$WT_PATH" status -sb
```

### 5. Submodules — same branch everywhere (if `.gitmodules`)

Every submodule must end on the **same branch as the worktree**. For each one
(recursive): init → check out its base branch and `pull --ff-only` (answer of
step 2, else its default branch) → check out the worktree branch (existing local
or `origin/<branch>`) or create it from that base.

```bash
SYNC=~/.meta-skills/skills/code/git-worktree-sync/scripts/worktree-sync.sh
bash "$SYNC" submodules --to "$WT_PATH" [--sub-base <branch>]
```

The script ends with `all submodules on <branch>`; on `NOT on <branch>: …` fix
those submodules (dirty tree, pull conflict) and re-run it. Run this **before**
the `.env` copy (submodule folders must be checked out first).

### 6. MANDATORY — copy the `.env` files (`git-worktree-sync`)

Never skip this step, never report the worktree as ready before it ran. Follow the
[`git-worktree-sync`](../git-worktree-sync/SKILL.md) skill in **copy** mode:

```bash
SYNC=~/.meta-skills/skills/code/git-worktree-sync/scripts/worktree-sync.sh
bash "$SYNC" copy --to "$WT_PATH"          # source = main worktree by default
```

Then give the user the absolute path of the new worktree, its branch, the branch
of each submodule and the list of copied `.env` files (names only, never their content).

## Other commands

```bash
git worktree list --porcelain           # machine-readable list
git worktree remove "$WT_PATH"          # refuses if dirty — CONFIRM before --force
git worktree prune                      # drop metadata of deleted folders
git worktree move "$WT_PATH" "$NEW"     # relocate
git worktree lock "$WT_PATH" --reason "on USB drive"
git branch -d feat/xyz                  # delete the branch after removal (optional, confirm)
```

## Notes

- Confirm before `remove`, `--force`, or deleting a branch.
- The worktree shares `.git` objects, refs and the **stash** with the main
  checkout — use named stashes or WIP commits.
- Ignored files such as `.env` are **not** present in the new worktree → step 5
  (`git-worktree-sync`) is mandatory.
