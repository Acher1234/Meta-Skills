# namecheap

Manage Namecheap domains, DNS, email forwarding, and domain privacy via
[`namecheap-cli`](https://github.com/adriangalilea/namecheap-python/blob/main/CLI.md).

Credentials live in a per-workspace `.env` resolved by `SkillCred` — not
`namecheap-cli config init`.

```bash
export CURRENT_SKILL_DIRECTORY="$PWD/.cursor/skills/namecheap"  # or your install path
cd ~/.meta-skills/skills/namecheap
python scripts/init.py
set -a && . "$CURRENT_SKILL_DIRECTORY/.env" && set +a
namecheap-cli -o json domain list
```
