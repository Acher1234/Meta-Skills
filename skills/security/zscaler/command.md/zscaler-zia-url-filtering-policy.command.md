# zscaler-zia-url-filtering-policy — Commands

ZIA URL Filtering Policy via `LegacyZIAClient`. Implemented in `scripts/zia/url_filtering_policy.py`.
Confirm before `create`, `update`, and `delete`. `--user-name` is a directory user (not `ZIA__USERNAME`).

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/security/zscaler`.

| Slash | CLI | Description |
|-------|-----|-------------|
| `/zscaler_zia_url_filtering_policy_list` | `python scripts/cli.py zia url-filtering-policy list [--search {SEARCH}]` | List rules |
| `/zscaler_zia_url_filtering_policy_get` | `python scripts/cli.py zia url-filtering-policy get [--id {RULE_ID}] [--name {RULE_NAME}]` | Get by id or name |
| `/zscaler_zia_url_filtering_policy_create` | `python scripts/cli.py zia url-filtering-policy create {NAME} --action {ACTION} --category-id {CATEGORY_ID}` | Create a rule |
| `/zscaler_zia_url_filtering_policy_update` | `python scripts/cli.py zia url-filtering-policy update [--id {RULE_ID}] [--name {RULE_NAME}] [--action {ACTION}]` | Update a rule (unspecified fields kept) |
| `/zscaler_zia_url_filtering_policy_delete` | `python scripts/cli.py zia url-filtering-policy delete [--id {RULE_ID}] [--name {RULE_NAME}]` | Delete a rule |

Create requires `--action` and at least one `--category-id` / `--category-name`. Repeatable: `--category-id`, `--category-name`, `--request-method`, `--group-id`, `--group-name`, `--user-id`, `--user-name`, `--protocol`. Rename on update: `--new-name`.

### Examples

```bash
python scripts/cli.py zia url-filtering-policy list --search {SEARCH}
python scripts/cli.py zia url-filtering-policy get --id {RULE_ID}
python scripts/cli.py zia url-filtering-policy create {NAME} --action BLOCK --category-name {CATEGORY_NAME}
python scripts/cli.py zia url-filtering-policy update --name {RULE_NAME} --action ALLOW --order {ORDER}
python scripts/cli.py zia url-filtering-policy delete --id {RULE_ID}
```
