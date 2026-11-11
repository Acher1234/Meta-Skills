# Code skills

Paths are relative to `~/.meta-skills/`. Built-in skills under `skills/code/`. Use **Folder** as `SRC` for `/meta-skills`;
register under `$DEST/<folder basename>/`. Open the linked `SKILL.md` only for the skill you need.

| Name | Folder | What it does |
|------|--------|--------------|
| `git-worktree` | [`skills/code/git-worktree/`](../skills/code/git-worktree/SKILL.md) | Plain-git worktrees (asks base branch, branch, folder), `submodules.py` puts every submodule on the same branch, then mandatory `.env` copy via `git-worktree-sync` |
| `git-worktree-sync` | [`skills/code/git-worktree-sync/`](../skills/code/git-worktree-sync/SKILL.md) | `worktree_sync.py` (Linux / macOS / Windows): copy every `.env` / `.env.*` file + `SYNC_EXTRA` items from one checkout to another — no worktree creation |
| `orca-dev` | [`skills/code/orca-dev/`](../skills/code/orca-dev/SKILL.md) | `orca` CLI router — worktree (submodules + mandatory `.env` sync), repo, agent, terminal, orchestration, automation, tickets, browser, computer, runtime |
