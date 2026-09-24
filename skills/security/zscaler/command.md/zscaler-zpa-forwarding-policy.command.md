# zscaler-zpa-forwarding-policy — Commands

ZPA client forwarding policy via `LegacyZPAClient`. Implemented in `scripts/zpa/forwarding_policy.py`.
Get only.

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/security/zscaler`.

| Slash | CLI | Description |
|-------|-----|-------------|
| `/zscaler_zpa_forwarding_policy_list` | `python scripts/cli.py zpa forwarding-policy list [--search {SEARCH}]` | List forwarding policy rules |
| `/zscaler_zpa_forwarding_policy_get` | `python scripts/cli.py zpa forwarding-policy get [--id {RULE_ID}] [--name {RULE_NAME}]` | Get by id or name |

### Examples

```bash
python scripts/cli.py zpa forwarding-policy list
python scripts/cli.py zpa forwarding-policy list --search {SEARCH}
python scripts/cli.py zpa forwarding-policy get --id {RULE_ID}
python scripts/cli.py zpa forwarding-policy get --name {RULE_NAME}
```
