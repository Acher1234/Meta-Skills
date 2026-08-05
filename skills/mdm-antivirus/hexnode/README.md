# hexnode

Hexnode MDM API skill for Meta-Skills.

```bash
export CURRENT_SKILL_DIRECTORY="$PWD/.cursor/skills/hexnode"
eval "$(~/.meta-skills/.venv/bin/python ~/.meta-skills/skills/mdm-antivirus/hexnode/scripts/skill_env.py)"
cd ~/.meta-skills/skills/mdm-antivirus/hexnode
~/.meta-skills/install.sh pip init .
cp .env.example "$CURRENT_SKILL_DIRECTORY/.env"
# edit HEXNODE_API_KEY + HEXNODE_BASE_URL (or HEXNODE_PORTAL)
~/.meta-skills/.venv/bin/python scripts/cli.py env
~/.meta-skills/.venv/bin/python scripts/cli.py devices list --per-page 20
~/.meta-skills/.venv/bin/python scripts/cli.py devices get 5
~/.meta-skills/.venv/bin/python scripts/cli.py device-groups list
```

`skill_env.py` resolves the SkillCred `.env` via `$CURRENT_SKILL_DIRECTORY` — do not `source` the file manually.
