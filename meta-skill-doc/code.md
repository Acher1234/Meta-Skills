# Code skills

Paths are relative to `~/.meta-skills/`. Built-in skills under `skills/code/`. Use **Folder** as `SRC` for `/meta-skills`;
register under `$DEST/<folder basename>/`. Open the linked `SKILL.md` only for the skill you need.

| Name | Folder | What it does |
|------|--------|--------------|
| `git-worktree` | [`skills/code/git-worktree/`](../skills/code/git-worktree/SKILL.md) | Plain-git worktrees (asks base branch, branch, folder), then mandatory `.env` copy via `git-worktree-sync` |
| `git-worktree-sync` | [`skills/code/git-worktree-sync/`](../skills/code/git-worktree-sync/SKILL.md) | `worktree-sync.sh`: create a worktree and always copy every `.env` / `.env.*` file from the main worktree |
| `orca-worktree` | [`skills/code/orca-worktree/`](../skills/code/orca-worktree/SKILL.md) | Orca-managed worktree via `orca worktree create`, then mandatory `.env` copy via `git-worktree-sync` |
