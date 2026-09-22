# youtrack-auth — Commands

Requires `eval` of `skill_env.py` so `$URL` and `$API_TOKEN` are in the current shell.
All commands support `--help` for full options.

| Command | Description |
|---------|-------------|
| `yt auth login --base-url "$URL" --token "$API_TOKEN"` | Login (first command every session) |
| `yt auth login --base-url "$URL" --token "$API_TOKEN" --no-verify-ssl` | Login with self-signed TLS |
| `yt auth status` | Check authentication |
| `yt auth token --show` | Show stored token |
| `yt auth refresh` | Refresh the current token |
| `yt auth logout` | Clear stored credentials |

---
