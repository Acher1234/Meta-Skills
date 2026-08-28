# zscaler-zia-ip-fqdn-groups — Commands

ZIA IP/FQDN destination groups via `LegacyZIAClient`. Implemented in `scripts/zia/ip_fqdn_groups.py`.
Confirm before `create` and `update`. Unspecified fields are kept on update. `--address` replaces members unless `--append`.

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/security/zscaler`.

| Slash | CLI | Description |
|-------|-----|-------------|
| `/zscaler_zia_ip_fqdn_groups_list` | `python scripts/cli.py zia ip-fqdn-groups list [--search {SEARCH}] [--exclude-type {TYPE}]` | List groups |
| `/zscaler_zia_ip_fqdn_groups_get` | `python scripts/cli.py zia ip-fqdn-groups get [--id {GROUP_ID}] [--name {GROUP_NAME}]` | Get by id or name |
| `/zscaler_zia_ip_fqdn_groups_create` | `python scripts/cli.py zia ip-fqdn-groups create --name {NAME} --type DSTN_FQDN --address {FQDN}` | Create a group |
| `/zscaler_zia_ip_fqdn_groups_update` | `python scripts/cli.py zia ip-fqdn-groups update [--id {GROUP_ID}] [--name {GROUP_NAME}] [--address {ADDRESS}]` | Update a group |

`--exclude-type` / `--type`: `DSTN_IP`, `DSTN_FQDN` (create default), `DSTN_DOMAIN`, `DSTN_OTHER`. Create requires `--name` and at least one `--address`. Repeatable: `--address`, `--ip-category`, `--country`. Rename: `--new-name`.

### Examples

```bash
python scripts/cli.py zia ip-fqdn-groups list
python scripts/cli.py zia ip-fqdn-groups list --exclude-type DSTN_OTHER --search {SEARCH}
python scripts/cli.py zia ip-fqdn-groups get --id {GROUP_ID}
python scripts/cli.py zia ip-fqdn-groups get --name {GROUP_NAME}
python scripts/cli.py zia ip-fqdn-groups create --name {NAME} --type DSTN_FQDN --address {FQDN}
python scripts/cli.py zia ip-fqdn-groups update --name {GROUP_NAME} --address {ADDRESS}
python scripts/cli.py zia ip-fqdn-groups update --id {GROUP_ID} --append --address {ADDRESS}
python scripts/cli.py zia ip-fqdn-groups update --name {GROUP_NAME} --new-name {NEW_NAME} --description {DESCRIPTION}
```
