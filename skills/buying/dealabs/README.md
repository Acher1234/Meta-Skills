# dealabs

Dealabs REST v2 — search deals, get a deal, list comments. No credentials.

```bash
cd ~/.meta-skills/skills/buying/dealabs
~/.meta-skills/install.sh pip init .
python scripts/cli.py deals search --query "ssd"
python scripts/cli.py deals hot --days 1
python scripts/cli.py deals new
python scripts/cli.py merchants search --query "amazon"
python scripts/cli.py deals hot --merchant-id 36 --days 1
python scripts/cli.py deals get {DEAL_ID}
python scripts/cli.py thread-comments list {DEAL_ID}
```
