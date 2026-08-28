# elastic-cluster — Commands

Cluster info and `.env` validation. Implemented in `scripts/skill_env.py` and `scripts/utils.py`.

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/db/elastic`.

| Slash | CLI | Description |
|-------|-----|-------------|
| `/elastic_env` | `python scripts/cli.py env` | Validate `.env` (no network) |
| `/elastic_ping` | `python scripts/cli.py ping` | `GET /` cluster info |
| `/elastic_health` | `python scripts/cli.py health` | Cluster health |

### Examples

```bash
python scripts/cli.py env
python scripts/cli.py ping
python scripts/cli.py health
```
