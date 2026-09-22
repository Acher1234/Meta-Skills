# folder-crypt

Encrypt or decrypt a folder with a password (prompt, `--password`, or `.env`).

```bash
export CURRENT_SKILL_DIRECTORY="$PWD/.cursor/skills/folder-crypt"
cd ~/.meta-skills/skills/security/folder-crypt
~/.meta-skills/install.sh pip init .
cp .env.example "$CURRENT_SKILL_DIRECTORY/.env"   # optional: FOLDER + PASSWORD
python scripts/cli.py encrypt ~/Documents/secret
python scripts/cli.py decrypt ~/Documents/secret.fcr
```
