---
name: git-worktree-sync
description: >-
  Copy the .env files (`.env`, `.env.*`, any depth — incl. skill credentials
  like .claude/skills/<name>/.env) from one checkout to another, plus extra
  items the user lists in SYNC_EXTRA (skill .env). Does not create worktrees —
  it is the mandatory final step of `git-worktree` and `orca-dev` (worktree).
  Use when the user says "copie les .env dans le worktree", "sync worktree",
  or invokes /git-worktree-sync_*.
disable-model-invocation: true
---

### TO COPY

# git-worktree-sync

Per-workspace registration slice. Optional settings in `{SKILL_PATH}/.env` (`SYNC_EXTRA`).

## Working directory

Placeholders changed by `/meta-skills` at copy time (NAME => {PLACEHOLDER}):

IS_GLOBAL => {IS_GLOBAL}
TYPE_OF_AI_TOOLS => {TYPE_OF_AI_TOOLS}
SKILL_PATH => {SKILL_PATH}

Bash / zsh:

```bash
export CURRENT_SKILL_DIRECTORY="{SKILL_PATH}"
~/.meta-skills/.venv/bin/python ~/.meta-skills/skills/code/git-worktree-sync/scripts/worktree_sync.py copy --to "<target>"
```

PowerShell (Windows):

```powershell
$env:CURRENT_SKILL_DIRECTORY = "{SKILL_PATH}"
& "$HOME/.meta-skills/.venv/Scripts/python.exe" "$HOME/.meta-skills/skills/code/git-worktree-sync/scripts/worktree_sync.py" copy --to "<target>"
```

##### END TO COPY

# git-worktree-sync

## When to use

`.env` files are git-ignored, so a new worktree (plain git, Orca, Claude Code
`EnterWorktree`, …) has none of them — and project-scope meta-skills
(`./.claude/skills/<name>/.env`, …) lose their credentials. This skill **only copies**
them from one checkout to another; it never creates a worktree.

Called as the **mandatory final step** by [`git-worktree`](../git-worktree/SKILL.md)
and [`orca-dev`](../orca-dev/SKILL.md) (worktree create). A worktree made any
other way: run `copy` in it **before** any other work.

## Slash commands

`worktree_sync.py` = the script in the Working directory block (Bash or PowerShell).

| Slash | CLI | Description |
|-------|-----|-------------|
| `/git-worktree-sync_copy` | `worktree_sync.py copy [--from <dir>] [--to <dir>] [--extra <path>]… [--dry-run]` | Copy `.env` files + extra items |
| `/git-worktree-sync_paths` | `worktree_sync.py list-paths [--from <dir>] [--extra <path>]…` | What would be copied |

- `--from`: source checkout (default: the **main** worktree of the current repo).
- `--to`: target checkout (default: root of the current repo).
- `--extra`: one more path / glob for this run (repeatable).

## What gets copied

1. **Always**: every `.env` / `.env.*` file at any depth, same relative path.
2. **Extra items** from `SYNC_EXTRA` in `{SKILL_PATH}/.env` (see `.env.example`) and
   `--extra`: comma-separated paths or globs relative to the repo root; a folder
   copies all its files. Example:
   `SYNC_EXTRA=CLAUDE.local.md,.claude/settings.local.json,.vscode/`

Rules: only files **missing** in the target are copied (tracked files of the target
branch are never overwritten); `.git`, `worktrees/`, `node_modules`, `.venv`,
`__pycache__` are never walked. An extra pattern matching nothing is reported, not fatal.

## How to run

1. Set `CURRENT_SKILL_DIRECTORY` (Working directory block) so `SYNC_EXTRA` is read.
2. First Python run: `cd ~/.meta-skills/skills/code/git-worktree-sync && ~/.meta-skills/install.sh pip init .`
   (shared venv + `common`; Windows: `install.ps1`).
3. Preview with `--dry-run`, then `copy`.
4. Report the copied file **names** only — never print the content of `.env` files.

## Notes

- Copied secrets stay local (git-ignored); never `git add -f` them.
- Registered with `SKILL_PATH = $(git rev-parse --show-toplevel)/.claude/skills/…`,
  the copied skill `.env` files work right away in the new worktree.
