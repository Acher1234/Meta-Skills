# bitwarden-session — Commands

All commands support `--help` for full options. Prefer `scripts/session.py` for connect.

Official docs: https://bitwarden.com/help/cli/

| Command | Description |
|---------|-------------|
| `session.py` | Load `.env` → `login --apikey` if needed → `unlock` → print `export BW_SESSION=…` |
| `bw status` | Vault status: `unlocked` / `locked` / `unauthenticated` |
| `bw login --apikey` | Authenticate with `BW_CLIENTID` / `BW_CLIENTSECRET` (does not unlock) |
| `bw unlock --passwordenv BW_PASSWORD --raw` | Decrypt vault; prints session key |
| `bw lock` | Lock vault; invalidate session |
| `bw logout` | Log out; clear local auth state |
| `bw sync` | Pull encrypted vault from server |
| `bw sync --last` | Last sync timestamp only |
| `bw config server <url>` | Point CLI at self-hosted / Vaultwarden URL |

---
