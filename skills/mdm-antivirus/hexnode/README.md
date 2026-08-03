# hexnode

Hexnode MDM API skill for Meta-Skills.

```bash
export CURRENT_SKILL_DIRECTORY="$PWD/.cursor/skills/hexnode"
cd ~/.meta-skills/skills/mdm-antivirus/hexnode
~/.meta-skills/install.sh pip init .
cp .env.example "$CURRENT_SKILL_DIRECTORY/.env"
# edit HEXNODE_API_KEY + HEXNODE_PORTAL
~/.meta-skills/.venv/bin/python scripts/cli.py env
~/.meta-skills/.venv/bin/python scripts/cli.py devices list --per-page 20
~/.meta-skills/.venv/bin/python scripts/cli.py devices get 5
~/.meta-skills/.venv/bin/python scripts/cli.py device-groups list
```
