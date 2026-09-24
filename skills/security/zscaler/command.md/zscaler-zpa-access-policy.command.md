# zscaler-zpa-access-policy — Commands

ZPA access policy via `LegacyZPAClient`. Implemented in `scripts/zpa/access_policy.py`.
Get only.

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/security/zscaler`.

| Slash | CLI | Description |
|-------|-----|-------------|
| `/zscaler_zpa_access_policy_list` | `python scripts/cli.py zpa access-policy list [--search {SEARCH}]` | List access policy rules |
| `/zscaler_zpa_access_policy_get` | `python scripts/cli.py zpa access-policy get [--id {RULE_ID}] [--name {RULE_NAME}]` | Get by id or name |

### Examples

```bash
python scripts/cli.py zpa access-policy list
python scripts/cli.py zpa access-policy list --search {SEARCH}
python scripts/cli.py zpa access-policy get --id {RULE_ID}
python scripts/cli.py zpa access-policy get --name {RULE_NAME}
```
