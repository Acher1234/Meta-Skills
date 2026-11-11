# orca-dev-terminal — Commands

`ORCA` = resolved CLI (see `orca-dev` SKILL.md). Add `--json` everywhere; full
flags: `ORCA <command> --help`.

## Terminals

| Command | Description |
|---------|-------------|
| `ORCA terminal list [--worktree <sel>] [--limit <n>] [--include-visual-layouts]` | Live terminals + handles |
| `ORCA terminal show [--terminal <h>]` | Metadata + preview |
| `ORCA terminal read [--terminal <h>] [--cursor <n>] [--limit <n>] [--screen]` | Output (`--screen` = rendered frame) |
| `ORCA terminal send [--terminal <h>] --text "<t>" [--enter] [--interrupt] [--wait-submit <s>]` | Send input |
| `ORCA terminal wait [--terminal <h>] --for exit\|tui-idle --timeout-ms <ms>` | Wait (always a timeout) |
| `ORCA terminal create [--worktree <sel>] [--title <t>] [--command "<cmd>"] [--focus]` | New terminal |
| `ORCA terminal split [--terminal <h>] --direction vertical\|horizontal [--command "<cmd>"]` | Split (vertical = left/right) |
| `ORCA terminal rename --terminal <h> --title <t>` / `set-pane-title` | Tab / pane title |
| `ORCA terminal switch --terminal <h>` | Bring to front (`focus` = alias) |
| `ORCA terminal close --terminal <h> [--tab]` / `--worktree <sel> --all` | Close — confirm `--all` |

Rules:

- `--terminal` omitted = active terminal of the current worktree. Handles are
  runtime-scoped: after `terminal_handle_stale`, re-list and use the new one only.
- `read` before `send`. `accepted: true` = input accepted, not a started turn —
  never resend on silence; use `--wait-submit` for proof, `--retry-request <id>` after a transport error.
- Agent permission menu (`agent_prompt_blocked`): send `--text` and `--enter` separately.
- Long output: page with `--cursor` (`nextCursor` while `limited`).
- Find an agent's terminal: join `worktree ps` `agents[].paneKey` to `tabId:leafId` of `terminal list`.

## Files (open as Orca tabs)

| Command | Description |
|---------|-------------|
| `ORCA file open <path> [--line <n> [--column <n>]] [--worktree <sel>] [--focus]` | Open a file |
| `ORCA file diff <path> [--staged] [--worktree <sel>] [--focus]` | Open its diff |
| `ORCA file open-changed [--mode edit\|diff\|both] [--worktree <sel>] [--focus]` | Open all changed files |
