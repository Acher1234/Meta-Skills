# eset

ESET Connect CLI — OAuth (`POST /oauth/token`) + Device / App / Asset / Policy /
Automation / Incident APIs.

Credentials via SkillCred `.env` (`CURRENT_SKILL_DIRECTORY`). Tokens are saved
and reloaded automatically (`ESET_ACCESS_TOKEN` / `ESET_REFRESH_TOKEN`).

```bash
export CURRENT_SKILL_DIRECTORY="$PWD/.cursor/skills/eset"
cd ~/.meta-skills/skills/mdm-antivirus/eset/script
~/.meta-skills/install.sh pip init ..
cp ../.env.example "$CURRENT_SKILL_DIRECTORY/.env"   # set URL / user / password
python cli.py token
python cli.py devices list
```
