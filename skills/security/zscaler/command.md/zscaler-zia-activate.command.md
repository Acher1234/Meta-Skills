# zscaler-zia-activate — Commands

ZIA configuration activation via `LegacyZIAClient`. Implemented on `ZiaClient` in `scripts/zia/client.py`.
Create / update / delete commands activate pending changes automatically. Confirm before `run`.

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/security/zscaler`.

| Slash | CLI | Description |
|-------|-----|-------------|
| `/zscaler_zia_activate_status` | `python scripts/cli.py zia activate status` | Get activation status (`ACTIVE` / `PENDING`) |
| `/zscaler_zia_activate_run` | `python scripts/cli.py zia activate run` | Activate pending changes |

Optional client overrides: `--username` `--password` `--api-key` `--cloud`.

### Examples

```bash
python scripts/cli.py zia activate status
python scripts/cli.py zia activate run
```
