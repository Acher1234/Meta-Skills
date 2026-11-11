---
name: git-worktree-sync
description: >-
  Create a git worktree with scripts/worktree_sync.py (Python, Linux / macOS / Windows), which ALWAYS copies every
  .env file of the project (`.env`, `.env.*`, at any depth — including the
  credentials of registered skills like .claude/skills/<name>/.env) into the new
  worktree. Nothing else is copied. Use when the user wants a worktree that keeps
  its .env / skill credentials, says "worktree avec les .env", or invokes
  /git-worktree-sync_*. Plain-git variant: `git-worktree`.
disable-model-invocation: true
---

### TO COPY

# git-worktree-sync

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

# git-worktree-sync

## When to use

Same as [`git-worktree`](../git-worktree/SKILL.md), but the `.env` files follow.
`.env` files are git-ignored, so a plain `git worktree add` produces a worktree
without them — and meta-skills registered at project scope
(`./.claude/skills/<name>/.env`, `./.cursor/skills/<name>/.env`, …) lose their
credentials. This skill creates the worktree, puts every submodule on the worktree's branch
(pulled from its base branch first) **and** copies the `.env` files.

Script (Python 3.9+, stdlib only — Linux / macOS / Windows), written `worktree_sync.py` below:

```bash
~/.meta-skills/.venv/bin/python ~/.meta-skills/skills/code/git-worktree-sync/scripts/worktree_sync.py <command> [options]
```

```powershell
& "$HOME/.meta-skills/.venv/Scripts/python.exe" "$HOME/.meta-skills/skills/code/git-worktree-sync/scripts/worktree_sync.py" <command> [options]
```

## MANDATORY rule

- **Never** create the worktree with raw `git worktree add` in this skill — always
  `worktree_sync.py create`. The `.env` copy is part of the script and cannot be skipped.
- Worktree already created some other way (Orca, Claude Code `EnterWorktree`,
  plain git, …)? Run `worktree_sync.py copy` inside it **before** any other work.
- The [`git-worktree`](../git-worktree/SKILL.md) and
  [`orca-worktree`](../orca-worktree/SKILL.md) skills call this skill
  (`submodules`, then `copy` as their mandatory final step).

## Slash commands

| Slash | CLI | Description |
|-------|-----|-------------|
| `/git-worktree-sync_create` | `worktree_sync.py create -b <branch> [-f <base>] [-p <path>]` | Create worktree + copy `.env` files |
| `/git-worktree-sync_submodules` | `worktree_sync.py submodules [--to <wt>] [--sub-base <b>] [--branch <b>]` | Pull each submodule from its base, then put all on the worktree branch |
| `/git-worktree-sync_copy` | `worktree_sync.py copy [--from <dir>] [--to <wt>]` | Copy `.env` files into an existing worktree |
| `/git-worktree-sync_paths` | `worktree_sync.py list-paths` | List the `.env` files that would be copied |

Options of `create`:

| Option | Meaning |
|--------|---------|
| `-b, --branch` | Branch for the worktree. Existing local → checked out; remote-only → tracking branch; else new branch |
| `-f, --base` | Base for a **new** branch (default: `origin/HEAD`, else `origin/main`/`main`/`master`) |
| `-p, --path` | Folder (default `<repo>/../<repo-name>.worktrees/<branch-slug>`) |
| `--detach <ref>` | Detached worktree instead of a branch |
| `--from <dir>` | Source of the `.env` files (default: **main** worktree) |
| `--sub-base <branch>` | Base branch the submodules are pulled from (default: each submodule's `origin/HEAD`; missing → falls back to it) |
| `--no-submodules` | Skip the submodule step (by default: init, pull base, same branch as the worktree in every submodule) |
| `--dry-run` | Print the git command and the `.env` list, change nothing |

## How to run — `/git-worktree-sync_create`

1. Gather context exactly like `git-worktree` step 1 (`git branch`, `git branch -r`,
   `git worktree list`).
2. **Ask** the user: base branch, branch name (new / existing / detached),
   folder (propose the default), submodules base branch if `.gitmodules`. One question at a time with defaults.
3. Preview: `worktree_sync.py create -b <branch> -f <base> -p <path> --dry-run`.
4. Run the same command without `--dry-run` from inside the repo:

   `worktree_sync.py create -b feat/xyz -f origin/main` (full path: see top).

5. Report the `WORKTREE=` path printed at the end and the list of copied files
   (names only — never print the content of `.env` files).

## What gets copied

**Only `.env` files**: every file named `.env` or `.env.*` (`.env.local`,
`.env.production`, …) at any depth of the source checkout (main worktree by
default), keeping the same relative path. Nothing else.

- Only files **missing** in the new worktree are copied — a `.env.example`
  tracked on the new branch keeps its branch version.
- Never searched: `.git`, `worktrees/` (e.g. `.claude/worktrees`), `node_modules`,
  `.venv`, `__pycache__`.

Project-scope skills registered with
`SKILL_PATH = $(git rev-parse --show-toplevel)/.claude/skills/<name>` resolve to the
new worktree automatically, so the copied credentials work right away.

## Notes

- No dependency: runs with the shared venv or any `python3` ≥ 3.9.
- Remove a worktree with `git worktree remove <path>` — confirm first; the copied
  `.env` files are deleted with the folder.
- Copied secrets stay local (they are git-ignored); never `git add -f` them.
