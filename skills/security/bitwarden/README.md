# bitwarden

Self-hosted Bitwarden / Vaultwarden via the official [`bw`](https://bitwarden.com/help/cli/) CLI.
Command index: [`SKILL.md`](SKILL.md). Domains under `command.md/` + `exemple.md/`.
Credentials helper: `scripts/skill_env.py` (then `bw login` / `bw unlock` in SKILL.md).

## Install

```bash
cd ~/.meta-skills/skills/security/bitwarden
~/.meta-skills/install.sh npm init .
cp .env.example .env   # or next to the registered skill
# fill BW_SERVER, BW_CLIENTID, BW_CLIENTSECRET, BW_PASSWORD
```

## Connect

See [SKILL.md](SKILL.md) — `eval skill_env.py`, then `bw login --apikey` (if needed) and
`bw unlock --passwordenv BW_PASSWORD`.
