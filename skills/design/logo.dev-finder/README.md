# logo-dev-finder

Search logo.dev and download logos. Secret key in SkillCred `.env` (`API_KEY`).

```bash
export CURRENT_SKILL_DIRECTORY="$PWD/.cursor/skills/logo-dev-finder"
cd ~/.meta-skills/skills/design/logo.dev-finder
cp .env.example "$CURRENT_SKILL_DIRECTORY/.env"   # set API_KEY
python scripts/cli.py env
python scripts/cli.py search sweetgreen --folder {FOLDER}
python scripts/cli.py search sweetgreen.com --folder {FOLDER}
```
