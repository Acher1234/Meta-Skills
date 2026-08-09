# bitwarden

Self-hosted Bitwarden / Vaultwarden via the official [`bw`](https://bitwarden.com/help/cli/) CLI.
Command index: [`SKILL.md`](SKILL.md). Domains under `command.md/` + `exemple.md/`.
Helper: `scripts/session.py`.

## Install

```bash
cd ~/.meta-skills/skills/security/bitwarden
~/.meta-skills/install.sh npm init .
cp .env.example .env   # or next to the registered skill
# fill BW_SERVER, BW_CLIENTID, BW_CLIENTSECRET, BW_PASSWORD
```

## Connect

```bash
export CURRENT_SKILL_DIRECTORY="$PWD"   # dir that holds .env
eval "$(~/.meta-skills/.venv/bin/python ./scripts/session.py)"
$BW list items --search github
```
