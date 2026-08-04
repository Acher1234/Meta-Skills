# eset-auth — Commands

Validate credentials and obtain OAuth Bearer tokens. No API gateway required.

All commands: `~/.meta-skills/.venv/bin/python cli.py …` from `~/.meta-skills/skills/mdm-antivirus/eset/script`.

| Slash | CLI | Description |
|-------|-----|-------------|
| `/eset_env-check` | `python cli.py env-check` | Validate `.env` + show resolved paths (no network) |
| `/eset_env-path` | `python cli.py env-check` | Print the resolved SkillCred `.env` path |
| `/eset_token` | `python cli.py token` | Get a Bearer token (password grant) → saves to `.env` |
| `/eset_token_refresh` | `python cli.py token --refresh REFRESH_TOKEN` | Refresh with a refresh_token |
| `/eset_token_print-request` | `python cli.py token --print-request` | Dry run: print request (secrets masked) |

### `token` options

| Flag | Description |
|------|-------------|
| `--refresh REFRESH_TOKEN` | Use refresh_token grant instead of password |
| `--print-request` | Dry run without calling the API |
| `--token-only` | On success, print only the access_token |
