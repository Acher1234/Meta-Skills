# folder-crypt

Encrypt or decrypt a file or folder with a password (prompt, `--password`, or `.env`).

```bash
export CURRENT_SKILL_DIRECTORY="$PWD/.cursor/skills/folder-crypt"
export PROJECT_PATH="$PWD"   # main project folder; relative FOLDER paths start here
cd ~/.meta-skills/skills/security/folder-crypt
~/.meta-skills/install.sh pip init .
cp .env.example "$CURRENT_SKILL_DIRECTORY/.env"   # optional: FOLDER (comma-separated) + PASSWORD
python scripts/cli.py encrypt ~/Documents/secret
python scripts/cli.py decrypt ~/Documents/secret.fcr
```
