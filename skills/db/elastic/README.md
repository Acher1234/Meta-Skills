# elastic

Elasticsearch CLI (basic auth). Shared code under Meta-Skills; per-workspace `.env`.

```bash
export CURRENT_SKILL_DIRECTORY="$PWD/.cursor/skills/elastic"
cd ~/.meta-skills/skills/db/elastic
~/.meta-skills/install.sh pip init .
cp .env.example "$CURRENT_SKILL_DIRECTORY/.env"   # set URL / USERNAME / PASSWORD
python scripts/cli.py env
python scripts/cli.py ping
python scripts/cli.py health
python scripts/cli.py indices list
python scripts/cli.py indices fields my-index
python scripts/cli.py indices query my-index --esquery '{"match_all":{}}' --page 1 --number-of-document 10
python scripts/cli.py kibana dashboard list
python scripts/cli.py kibana dashboard get DASH_ID
python scripts/cli.py kibana dashboard create --json '{"title":"Web logs","panels":[]}'
python scripts/cli.py kibana dashboard update DASH_ID --json '{"title":"Web logs","panels":[]}'
python scripts/cli.py kibana visualization list
python scripts/cli.py kibana visualization get VIS_ID
python scripts/cli.py kibana visualization create --json '{"type":"xy","title":"Logs"}'
python scripts/cli.py kibana visualization update VIS_ID --json '{"type":"xy","title":"Logs"}'
python scripts/cli.py kibana visualization delete VIS_ID
```
