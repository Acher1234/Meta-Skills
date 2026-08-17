# zscaler-zia-forwarding-rule — Commands

ZIA forwarding control via `LegacyZIAClient`. Implemented in `scripts/zia/forwarding_rule.py`.
Confirm before `create` and `delete`. `ENATDEDIP` requires `--gateway-id` or `--gateway-name`. Rule names are max 31 characters.

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/security/zscaler`.

| Slash | CLI | Description |
|-------|-----|-------------|
| `/zscaler_zia_forwarding_rule_list` | `python scripts/cli.py zia forwarding-rule list [--search {SEARCH}]` | List rules |
| `/zscaler_zia_forwarding_rule_get` | `python scripts/cli.py zia forwarding-rule get [--id {RULE_ID}] [--name {RULE_NAME}]` | Get by id or name |
| `/zscaler_zia_forwarding_rule_create` | `python scripts/cli.py zia forwarding-rule create {NAME} --forward-method {FORWARD_METHOD}` | Create a rule |
| `/zscaler_zia_forwarding_rule_delete` | `python scripts/cli.py zia forwarding-rule delete [--id {RULE_ID}] [--name {RULE_NAME}]` | Delete a rule |

Forward methods: `DIRECT`, `PROXYCHAIN`, `ZIA`, `ZPA`, `ECZPA`, `ECSELF`, `DROP`, `ENATDEDIP` (default), `GEOIP`. Repeatable: `--group-id`, `--group-name`, `--category-id`, `--category-name`, `--dest-address`, `--dest-ip-group-id`, `--dest-ip-group-name`. URL categories map to `destIpCategories`. Optional client overrides: `--username` `--password` `--api-key` `--cloud`.

### Examples

```bash
python scripts/cli.py zia forwarding-rule list --search {SEARCH}
python scripts/cli.py zia forwarding-rule get --id {RULE_ID}
python scripts/cli.py zia forwarding-rule create {NAME} --forward-method ENATDEDIP --gateway-name {GATEWAY_NAME} --group-name {GROUP_NAME} --category-name {CATEGORY_NAME}
python scripts/cli.py zia forwarding-rule delete --name {RULE_NAME}
```
