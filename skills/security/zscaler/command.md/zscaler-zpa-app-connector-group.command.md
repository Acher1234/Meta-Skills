# zscaler-zpa-app-connector-group — Commands

ZPA App Connector groups via `LegacyZPAClient`. Implemented in `scripts/zpa/app_connector_groups.py`.
Get only.

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/security/zscaler`.

| Slash | CLI | Description |
|-------|-----|-------------|
| `/zscaler_zpa_app_connector_group_list` | `python scripts/cli.py zpa app-connector-group list [--search {SEARCH}]` | List App Connector groups |
| `/zscaler_zpa_app_connector_group_get` | `python scripts/cli.py zpa app-connector-group get [--id {GROUP_ID}] [--name {GROUP_NAME}]` | Get by id or name |

### Examples

```bash
python scripts/cli.py zpa app-connector-group list
python scripts/cli.py zpa app-connector-group list --search {SEARCH}
python scripts/cli.py zpa app-connector-group get --id {GROUP_ID}
python scripts/cli.py zpa app-connector-group get --name {GROUP_NAME}
```
