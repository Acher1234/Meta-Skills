# youtrack-issues — Commands

Requires `skill_env.py` + `yt auth login`. Confirm before create / update / delete / assign.
All commands support `--help` for full options.

| Command | Description |
|---------|-------------|
| `yt issues list [--project-id ID] [--state Open] [--assignee USER]` | List issues |
| `yt issues show ISSUE-ID` | Get one issue |
| `yt issues search "priority:Critical state:Open"` | Search (YouTrack query language) |
| `yt issues create PROJECT-ID "Summary" [-d DESC] [-t Bug] [-p High] [-a USER]` | Create issue |
| `yt issues update ISSUE-ID [--state "In Progress"] [--assignee USER] [-s SUMMARY]` | Update issue |
| `yt issues update ISSUE-ID --show-details` | Show current fields |
| `yt issues delete ISSUE-ID [--force]` | Delete issue |
| `yt issues assign ISSUE-ID USER` | Assign |
| `yt issues move ISSUE-ID -p TARGET-PROJECT` | Move to another project |
| `yt issues comments add ISSUE-ID "text"` | Add comment |
| `yt issues comments list ISSUE-ID` | List comments |
| `yt issues comments update ISSUE-ID COMMENT-ID "text"` | Update comment |
| `yt issues comments delete ISSUE-ID COMMENT-ID` | Delete comment |
| `yt issues attach upload ISSUE-ID /path/to/file` | Upload attachment |
| `yt issues attach list ISSUE-ID` | List attachments |
| `yt issues attach download ISSUE-ID ATTACHMENT-ID` | Download attachment |
| `yt issues attach delete ISSUE-ID ATTACHMENT-ID` | Delete attachment |
| `yt issues links create ISSUE-A ISSUE-B "depends on"` | Link issues |
| `yt issues links list ISSUE-ID` | List links |
| `yt issues links delete ISSUE-ID LINK-ID` | Delete link |
| `yt issues tag add ISSUE-ID TAG` | Add tag |
| `yt issues tag remove ISSUE-ID TAG` | Remove tag |

Custom fields on create/update: `-cf "FieldName=value"` (repeatable).

---
