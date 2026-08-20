# zscaler-zia-users — Commands

ZIA user management via `LegacyZIAClient`. Implemented in `scripts/zia/users.py`.
Credentials from SkillCred `.env`.

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/security/zscaler`.

| Slash | CLI | Description |
|-------|-----|-------------|
| `/zscaler_zia_users_list` | `python scripts/cli.py zia users list [--page {PAGE}] [--page-size {PAGE_SIZE}]` | List ZIA users |
| `/zscaler_zia_users_groups` | `python scripts/cli.py zia users groups [--page {PAGE}] [--page-size {PAGE_SIZE}]` | List ZIA user groups |
| `/zscaler_zia_users_departments` | `python scripts/cli.py zia users departments [--page {PAGE}] [--page-size {PAGE_SIZE}] [--search {SEARCH}]` | List ZIA departments |

### Examples

```bash
python scripts/cli.py zia users list --page 1 --page-size 20
python scripts/cli.py zia users groups --page-size 100
python scripts/cli.py zia users departments --search {SEARCH}
```
