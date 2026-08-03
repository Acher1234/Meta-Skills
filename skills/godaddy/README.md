# godaddy

GoDaddy Domains API v3 — discovery, owned domain get, and DNS CLI.

```bash
export CURRENT_SKILL_DIRECTORY="$PWD/.cursor/skills/godaddy"
cd ~/.meta-skills/skills/godaddy
~/.meta-skills/install.sh pip init .
cp .env.example "$CURRENT_SKILL_DIRECTORY/.env"   # set GODADDY_PAT
python scripts/cli.py check example.com
python scripts/cli.py domain get example.com
python scripts/cli.py dns list example.com
```
