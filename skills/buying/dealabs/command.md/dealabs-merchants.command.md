# dealabs-merchants — Commands

Search, list, and get Dealabs merchants. Implemented in `scripts/merchants.py` (`Merchants`). Use `merchant_id` to filter deals (`deals hot|new|search --merchant-id`).

`GET merchant` is an A–Z listing — it ignores a name query. Use `merchant/search` to find an id (Amazon = `36`).

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/buying/dealabs`.

| Slash | CLI | API |
|-------|-----|-----|
| `/dealabs_merchants_search` | `python scripts/cli.py merchants search --query {QUERY} [--page 0] [--limit 25]` | `GET merchant/search` |
| `/dealabs_merchants_list` | `python scripts/cli.py merchants list [--page 0] [--limit 25]` | `GET merchant` |
| `/dealabs_merchants_get` | `python scripts/cli.py merchants get {MERCHANT_ID}` | `GET merchant/{merchant_id}` |

Placeholders: `{QUERY}`, `{MERCHANT_ID}`.
