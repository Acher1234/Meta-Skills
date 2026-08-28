# dealabs-thread-comments — Commands

List comments on a Dealabs thread. Implemented in `scripts/thread_comments.py` (`ThreadComments`).

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/buying/dealabs`.

| Slash | CLI | API |
|-------|-----|-----|
| `/dealabs_thread_comments_list` | `python scripts/cli.py thread-comments list {THREAD_ID} [--page 0] [--limit 50] [--order new]` | `GET thread/{thread_id}/comments` |

Placeholders: `{THREAD_ID}`.
