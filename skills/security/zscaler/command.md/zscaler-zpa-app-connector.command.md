# zscaler-zpa-app-connector — Commands

ZPA App Connectors via `LegacyZPAClient`. Implemented in `scripts/zpa/app_connectors.py`.
Get plus a health check. Healthy means `controlChannelStatus` is `ZPN_STATUS_AUTHENTICATED`. `--enabled-only` skips disabled connectors.

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/security/zscaler`.

| Slash | CLI | Description |
|-------|-----|-------------|
| `/zscaler_zpa_app_connector_list` | `python scripts/cli.py zpa app-connector list [--search {SEARCH}]` | List App Connectors |
| `/zscaler_zpa_app_connector_get` | `python scripts/cli.py zpa app-connector get [--id {CONNECTOR_ID}] [--name {CONNECTOR_NAME}]` | Get by id or name |
| `/zscaler_zpa_app_connector_health` | `python scripts/cli.py zpa app-connector health [--search {SEARCH}] [--enabled-only]` | Check all App Connectors are healthy |

### Examples

```bash
python scripts/cli.py zpa app-connector list
python scripts/cli.py zpa app-connector list --search {SEARCH}
python scripts/cli.py zpa app-connector get --id {CONNECTOR_ID}
python scripts/cli.py zpa app-connector get --name {CONNECTOR_NAME}
python scripts/cli.py zpa app-connector health
python scripts/cli.py zpa app-connector health --enabled-only
```
