# zscaler-zia-dedicated-ip-gateways — Commands

ZIA dedicated IP gateways via `LegacyZIAClient`. Implemented in `scripts/zia/dedicated_ip_gateways.py`.

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/security/zscaler`.

| Slash | CLI | Description |
|-------|-----|-------------|
| `/zscaler_zia_dedicated_ip_gateways_list` | `python scripts/cli.py zia dedicated-ip-gateways list` | List dedicated IP gateways |
| `/zscaler_zia_dedicated_ip_gateways_get` | `python scripts/cli.py zia dedicated-ip-gateways get [--id {GATEWAY_ID}] [--name {GATEWAY_NAME}]` | Get by id or name |

### Examples

```bash
python scripts/cli.py zia dedicated-ip-gateways list
python scripts/cli.py zia dedicated-ip-gateways get --id {GATEWAY_ID}
python scripts/cli.py zia dedicated-ip-gateways get --name {GATEWAY_NAME}
```
