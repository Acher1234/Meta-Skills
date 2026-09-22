# elastic-indices — Commands

List indices and field mappings. Implemented in `scripts/indices.py`.

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/db/elastic`.

| Slash | CLI | Description |
|-------|-----|-------------|
| `/elastic_indices_list` | `python scripts/cli.py indices list` | List indices |
| `/elastic_indices_fields` | `python scripts/cli.py indices fields {INDEX}` | List field paths + types |
| `/elastic_indices_query` | `python scripts/cli.py indices query {INDEX} --esquery '{QUERY}' [--page {PAGE}] [--skip {SKIP}] [--number-of-document {SIZE}] [--all]` | Search documents |

`--esquery` is Query DSL JSON (`{"match_all":{}}` or `{"query":{...}}`) or a query string. `--all` fetches remaining hits from the offset (`from`+`size` capped at 10000).

### Examples

```bash
python scripts/cli.py indices list
python scripts/cli.py indices fields {INDEX}
python scripts/cli.py indices query {INDEX} --esquery '{"match_all":{}}' --page 1 --number-of-document 10
python scripts/cli.py indices query {INDEX} --esquery '{"query":{"term":{"status":"{STATUS}"}}}' --skip {SKIP}
python scripts/cli.py indices query {INDEX} --esquery '{STATUS}:200' --all
```
