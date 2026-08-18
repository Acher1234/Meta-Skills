# zscaler-zia-url-cloud-apps — Commands

ZIA URL cloud applications (read-only) via `LegacyZIAClient`.
Implemented in `scripts/zia/url_cloud_apps.py`. Category list/get delegates to `url_categories.py`.

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/security/zscaler`.

| Slash | CLI | Description |
|-------|-----|-------------|
| `/zscaler_zia_url_cloud_apps_list` | `python scripts/cli.py zia url-cloud-apps list [--search {SEARCH}]` | List URL cloud applications |
| `/zscaler_zia_url_cloud_apps_get` | `python scripts/cli.py zia url-cloud-apps get [--id {APP_ID}] [--name {APP_NAME}]` | Get a cloud application |
| `/zscaler_zia_url_cloud_apps_categories` | `python scripts/cli.py zia url-cloud-apps categories [--search {SEARCH}]` | List URL categories |
| `/zscaler_zia_url_cloud_apps_category` | `python scripts/cli.py zia url-cloud-apps category [--id {CATEGORY_ID}] [--name {CATEGORY_NAME}]` | Get a URL category |

Optional client overrides: `--username` `--password` `--api-key` `--cloud`.

### Examples

```bash
python scripts/cli.py zia url-cloud-apps list --search {SEARCH}
python scripts/cli.py zia url-cloud-apps get --name {APP_NAME}
python scripts/cli.py zia url-cloud-apps categories
python scripts/cli.py zia url-cloud-apps category --id {CATEGORY_ID}
```
