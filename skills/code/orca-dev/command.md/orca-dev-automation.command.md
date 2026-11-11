# orca-dev-automation — Commands

`ORCA` = resolved CLI (see `orca-dev` SKILL.md). Add `--json` everywhere; full
flags: `ORCA <command> --help`.

| Command | Description |
|---------|-------------|
| `ORCA automations list` | Scheduled automations |
| `ORCA automations show <selector>` | One automation |
| `ORCA automations create --name <n> --trigger <preset\|cron\|rrule> --prompt "<p>" --provider <agent> [--repo <sel>\|--workspace <sel>] [--workspace-mode existing\|new-per-run] [--base-branch <ref>] [--precheck "<cmd>"]` | Create |
| `ORCA automations edit …` | Edit (same flags) |
| `ORCA automations run <selector>` | Run now |
| `ORCA automations runs <selector>` | Run history |
| `ORCA automations remove <selector>` | Delete + history — confirm first |

`--workspace-mode new-per-run` creates a fresh worktree per run: it will **not**
contain the `.env` files — prefer `existing` on a worktree prepared with the
worktree flow, or start the prompt with the `git-worktree-sync` `copy` command.
