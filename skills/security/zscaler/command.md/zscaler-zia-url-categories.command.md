# zscaler-zia-url-categories — Commands

ZIA URL categories via `LegacyZIAClient`. Implemented in `scripts/zia/url_categories.py`.
Credentials from SkillCred `.env`; CLI flags override them. Confirm before `create`, `add-urls`, `remove-urls`, and `delete`.

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/security/zscaler`.

| Slash | CLI | Description |
|-------|-----|-------------|
| `/zscaler_zia_url_categories_list` | `python scripts/cli.py zia url-categories list` | List URL categories |
| `/zscaler_zia_url_categories_get` | `python scripts/cli.py zia url-categories get [--id {CATEGORY_ID}] [--name {CATEGORY_NAME}]` | Get by id or configured_name |
| `/zscaler_zia_url_categories_create` | `python scripts/cli.py zia url-categories create {NAME} --url {URL} [--ip-range {CIDR}] [--keyword {KEYWORD}] [--description {DESCRIPTION}]` | Create a custom category |
| `/zscaler_zia_url_categories_add_urls` | `python scripts/cli.py zia url-categories add-urls --url {URL} [--id {CATEGORY_ID}] [--name {CATEGORY_NAME}]` | Add URLs |
| `/zscaler_zia_url_categories_remove_urls` | `python scripts/cli.py zia url-categories remove-urls --url {URL} [--id {CATEGORY_ID}] [--name {CATEGORY_NAME}]` | Remove URLs |
| `/zscaler_zia_url_categories_delete` | `python scripts/cli.py zia url-categories delete [--id {CATEGORY_ID}] [--name {CATEGORY_NAME}]` | Delete a custom category |

Create requires at least one of `--url` / `--ip-range` / `--keyword`. Optional client overrides: `--username` `--password` `--api-key` `--cloud`.

### Examples

```bash
python scripts/cli.py zia url-categories list
python scripts/cli.py zia url-categories get --id {CATEGORY_ID}
python scripts/cli.py zia url-categories create {NAME} --url {URL}
python scripts/cli.py zia url-categories add-urls --name {CATEGORY_NAME} --url {URL}
python scripts/cli.py zia url-categories remove-urls --id {CATEGORY_ID} --url {URL}
python scripts/cli.py zia url-categories delete --id {CATEGORY_ID}
```
