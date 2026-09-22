# youtrack-time — Commands

Requires `skill_env.py` + `yt auth login`. Confirm before logging time.
All commands support `--help` for full options.

| Command | Description |
|---------|-------------|
| `yt time log ISSUE-ID "2h 30m" [--description …] [--work-type Development]` | Log work |
| `yt time report --start-date YYYY-MM-DD --end-date YYYY-MM-DD` | Time report |
| `yt time summary [--group-by user]` | Time summary |

Duration formats: `2h`, `2h 30m`, `1d`.

---
