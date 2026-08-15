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
```
