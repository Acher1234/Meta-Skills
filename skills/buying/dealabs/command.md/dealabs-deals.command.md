# dealabs-deals — Commands

Search, list, and get Dealabs deals. Implemented in `scripts/deals.py` (`Deals`) via `scripts/dealabs.py`.

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/buying/dealabs`.

| Slash | CLI | API |
|-------|-----|-----|
| `/dealabs_deals_search` | `python scripts/cli.py deals search [--query {QUERY}] [--order-by hot] [--page 0] [--limit 50]` | `GET thread/search` |
| `/dealabs_deals_hot` | `python scripts/cli.py deals hot [--days 1] [--page 0] [--limit 50]` | `GET thread?order_by=hot` |
| `/dealabs_deals_new` | `python scripts/cli.py deals new [--page 0] [--limit 50]` | `GET thread?order_by=new` |
| `/dealabs_deals_list` | `python scripts/cli.py deals list [--deal-ids {IDS}] [--page 0] [--limit 25]` | `GET thread` |
| `/dealabs_deals_get` | `python scripts/cli.py deals get {DEAL_ID}` | `GET thread/{deal_id}` |

Placeholders: `{QUERY}`, `{IDS}` (comma-separated), `{DEAL_ID}`. Optional search filters: `--type-id`, `--group-id`, `--merchant-id`, `--expired`, `--local`, `--clearance`. `--order-by` is `new`, `hot`, `discussed`, or `featured`.
