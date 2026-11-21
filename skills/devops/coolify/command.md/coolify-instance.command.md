# coolify-instance — Commands

Teams, audit log, instance email and notification channels. Requires a connected context
(`--context "$COOLIFY_CONTEXT"`). All commands support `--help` and `--format json`.
Teams use **numeric IDs**, not UUIDs.

| Command | Description |
|---------|-------------|
| `coolify teams list` | Teams the token can access |
| `coolify teams current` | Team bound to the token |
| `coolify teams get <team_id>` | One team |
| `coolify teams members list [team_id]` | Members of a team (current team if omitted) |
| `coolify teams update` | Team settings (`--build-server-fallback=<true\|false>`, required) |
| `coolify audit list` | Audit events, newest first (`--search`, `--action`, `--source`, `--page`, `--per-page`) — admins / owners only |
| `coolify settings email get` | Instance SMTP / Resend settings |
| `coolify settings email update` | Update them (`--json '<settings>'`) — root-team token with `write:sensitive` |
| `coolify notification get <channel>` | Channel settings: `email`, `discord`, `slack`, `telegram`, `pushover`, `webhook` |
| `coolify notification update <channel>` | Update a channel (`--json '{"webhook_enabled":true}'`) |

---
