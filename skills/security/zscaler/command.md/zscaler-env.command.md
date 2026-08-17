# zscaler-env — Commands

Validate SkillCred `.env` (no network). Implemented in `scripts/skill_env.py`.

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/security/zscaler`.

| Slash | CLI | Description |
|-------|-----|-------------|
| `/zscaler_env` | `python scripts/cli.py env` | Validate `.env` (secrets masked) |

Nested JSON → env (`__` separator):

| JSON path | Variable |
|-----------|----------|
| `zpa.client_id` | `ZPA__CLIENT_ID` |
| `zpa.client_secret` | `ZPA__CLIENT_SECRET` |
| `zpa.customer_id` | `ZPA__CUSTOMER_ID` |
| `zpa.cloud` | `ZPA__CLOUD` |
| `zpa.microtenant_id` | `ZPA__MICROTENANT_ID` |
| `zia.username` | `ZIA__USERNAME` |
| `zia.password` | `ZIA__PASSWORD` |
| `zia.api_key` | `ZIA__API_KEY` |
| `zia.cloud` | `ZIA__CLOUD` |
| `zidentity.client_id` | `ZIDENTITY__CLIENT_ID` |
| `zidentity.client_secret` | `ZIDENTITY__CLIENT_SECRET` |
| `zidentity.vanity_domain` | `ZIDENTITY__VANITY_DOMAIN` |
| `zidentity.cloud` | `ZIDENTITY__CLOUD` |
| `zidentity.customer_id` | `ZIDENTITY__CUSTOMER_ID` |

### Examples

```bash
python scripts/cli.py env
```
