---
name: namecheap
description: >-
  Manage Namecheap domains, DNS, email forwarding, and WhoisGuard privacy via
  namecheap-cli. Installs with pip, loads per-workspace .env through SkillCred.
  Use when the user mentions Namecheap, DNS records, domain list/check, or
  invokes /namecheap_*.
disable-model-invocation: true
---

# namecheap

## When to use

Trigger phrases: "list my Namecheap domains", "add a DNS record", "check domain
availability", "Namecheap email forwarding", "WhoisGuard", `/namecheap_*`.

## Working directory

Placeholders changed by `/meta-skills` at copy time (NAME => {PLACEHOLDER}):

IS_GLOBAL => {IS_GLOBAL}
TYPE_OF_AI_TOOLS => {TYPE_OF_AI_TOOLS}
SKILL_PATH => {SKILL_PATH}

Before `cd`, export the local skill directory and source `.env` files:

```bash
export CURRENT_SKILL_DIRECTORY="{SKILL_PATH}"
export IS_GLOBAL="{IS_GLOBAL}"
export TYPE_OF_AI_TOOLS="{TYPE_OF_AI_TOOLS}"
[ -f "$HOME/.meta-skills/.env" ] && set -a && . "$HOME/.meta-skills/.env" && set +a
[ -f "{SKILL_PATH}/.env" ] && set -a && . "{SKILL_PATH}/.env" && set +a
cd "{SKILL_PATH}"
```

Always `cd` into `{SKILL_PATH}` before running scripts. Prefer
`~/.meta-skills/.venv/bin/python` for `scripts/init.py`.

## Credentials — load env via SkillCred

**Always load env from `SkillCred`** — never rely on `namecheap-cli config init`
or `~/.config/namecheap/config.yaml` for this skill.

| Variable | Notes |
|----------|--------|
| `NAMECHEAP_API_KEY` | Required |
| `NAMECHEAP_USERNAME` | Required |
| `NAMECHEAP_API_USER` | Defaults to username if empty |
| `NAMECHEAP_CLIENT_IP` | Auto-detected if empty (must be whitelisted in Namecheap API Access) |
| `NAMECHEAP_SANDBOX` | `true` / `false` (production = `false`) |

`.env` path = `SkillCred("namecheap", [".env"]).file_path()` under
`$CURRENT_SKILL_DIRECTORY`.

### Init (required first)

```bash
python scripts/init.py
```

`init` will:

1. Resolve / create `.env` in the skill dir via `SkillCred` (from `.env.example`)
2. Install the CLI via pip into the shared Meta-Skills venv (fallback: current Python):
   `python -m pip install 'namecheap-python[cli]'`
3. Load the env and print JSON status (which keys are set — not secret values)

Fill `NAMECHEAP_API_KEY` + `NAMECHEAP_USERNAME` in the printed `env_path`, then
re-run `init` until `"ok": true`.

### Run (direct `namecheap-cli`)

Source the SkillCred `.env` (Working directory block above), then call the CLI
**directly** — no Python wrapper:

```bash
# prefer the shared-venv binary if namecheap-cli is not on PATH
~/.meta-skills/.venv/bin/namecheap-cli -o json domain list
# or, if on PATH:
namecheap-cli -o json domain list
```

Global options go **before** the resource:
`namecheap-cli -o json dns list example.com` (not after). Prefer `-o json` for agents
(table output truncates long values).

If `NAMECHEAP_API_USER` is empty in `.env`, set it to `NAMECHEAP_USERNAME` before
calling the CLI (or leave blank only if the CLI defaults it for you).

## Important — Safety rules

These matter equally for humans scripting the CLI and for agents driving it:

- **Every DNS write replaces the whole zone.** `dns add` and `dns delete` are
  read-modify-write over all records (Namecheap has no per-record API). Snapshot
  before bulk or risky changes:
  `namecheap-cli dns export example.com --format json > example.com.dns.json`.
  Never run two DNS writes against the same domain concurrently.
- **Confirmation prompts and `--yes`.** `dns delete`, `dns set-nameservers`,
  `dns reset-nameservers`, `dns set-email-forwarding`, `privacy disable`, and
  `privacy renew` prompt interactively. In non-interactive shells (scripts,
  agents) the prompt cannot be answered and the command dies: pass `--yes`/`-y`,
  but only once the operation is actually intended. **Agents: never pass `--yes`
  without explicit user approval of that specific operation.**
- `dns set-email-forwarding` **replaces all existing rules**. Read current rules
  first (`dns email-forwarding example.com`) and re-include the keepers.
- `privacy renew` charges real money from the account balance.
- `dns delete --all` wipes the zone. Prefer targeted deletes by
  `--type` / `--name` / `--value`.

## Slash commands

### Setup

| Slash | CLI | Description |
|-------|-----|-------------|
| `/namecheap_init` | `python scripts/init.py` | Create SkillCred `.env` + `pip install 'namecheap-python[cli]'` (shared venv) |

### Domain

| Slash | CLI | Description |
|-------|-----|-------------|
| `/namecheap_domain_list` | `namecheap-cli -o json domain list [--status …] [--sort …] [--expiring-in N]` | List domains |
| `/namecheap_domain_check` | `namecheap-cli -o json domain check [DOMAINS…] [--file FILE]` | Availability check |
| `/namecheap_domain_info` | `namecheap-cli -o json domain info DOMAIN` | Domain details |
| `/namecheap_domain_contacts` | `namecheap-cli -o json domain contacts DOMAIN` | Contact info |
| `/namecheap_domain_tlds` | `namecheap-cli -o json domain tlds [--registerable] [--type gtld\|cctld]` | Supported TLDs |

### DNS

| Slash | CLI | Description |
|-------|-----|-------------|
| `/namecheap_dns_list` | `namecheap-cli -o json dns list DOMAIN [-t TYPE] [-n NAME]` | List DNS records |
| `/namecheap_dns_add` | `namecheap-cli dns add DOMAIN TYPE NAME VALUE [--ttl N] [--priority N]` | Add record (rewrites zone) |
| `/namecheap_dns_delete` | `namecheap-cli dns delete DOMAIN [-t …] [-n …] [-v …] [--all] [-y]` | Delete records (needs user OK for `-y`) |
| `/namecheap_dns_export` | `namecheap-cli dns export DOMAIN [-f bind\|yaml\|json] [-o FILE]` | Snapshot zone |
| `/namecheap_dns_nameservers` | `namecheap-cli -o json dns nameservers DOMAIN` | Show nameservers |
| `/namecheap_dns_set-nameservers` | `namecheap-cli dns set-nameservers DOMAIN NS… [-y]` | Custom NS (needs user OK for `-y`) |
| `/namecheap_dns_reset-nameservers` | `namecheap-cli dns reset-nameservers DOMAIN [-y]` | Back to Namecheap BasicDNS |
| `/namecheap_dns_email-forwarding` | `namecheap-cli -o json dns email-forwarding DOMAIN` | List forwarding rules |
| `/namecheap_dns_set-email-forwarding` | `namecheap-cli dns set-email-forwarding DOMAIN RULES… [-y]` | Replace all rules |

`dns add` types: `a` \| `aaaa` \| `cname` \| `mx` \| `txt` \| `ns` \| `url` \| `url301` \| `frame`. MX requires `--priority`.

### Privacy (WhoisGuard)

| Slash | CLI | Description |
|-------|-----|-------------|
| `/namecheap_privacy_list` | `namecheap-cli -o json privacy list [-t all\|alloted\|free\|discard]` | List subscriptions |
| `/namecheap_privacy_enable` | `namecheap-cli privacy enable DOMAIN EMAIL` | Enable privacy |
| `/namecheap_privacy_disable` | `namecheap-cli privacy disable DOMAIN [-y]` | Disable (needs user OK for `-y`) |
| `/namecheap_privacy_renew` | `namecheap-cli privacy renew DOMAIN [--years N] [--yes]` | **Charges money** — needs user OK |
| `/namecheap_privacy_change-email` | `namecheap-cli privacy change-email DOMAIN` | Rotate masked email |

### Account

| Slash | CLI | Description |
|-------|-----|-------------|
| `/namecheap_account_balance` | `namecheap-cli -o json account balance` | Account balance |
| `/namecheap_account_pricing` | `namecheap-cli -o json account pricing [TLD] [-a register\|renew\|transfer\|reactivate]` | Pricing |

### Other

| Slash | CLI | Description |
|-------|-----|-------------|
| `/namecheap_completion` | `namecheap-cli completion {bash\|zsh\|fish}` | Shell completion script |
| `/namecheap_skill_commands` | `namecheap-cli skill commands` | Upstream-generated command markdown |
| `/namecheap_skill_install` | `namecheap-cli skill install [--dir PATH]` | Upstream Claude skill install (optional; Meta-Skills uses this skill instead) |

Global CLI options (before resource): `--config`, `--profile`, `--sandbox`,
`-o table|json|yaml|csv`, `--no-color`, `-q`, `-v`, `--debug`, `--version`.

## How to run

1. Export `CURRENT_SKILL_DIRECTORY` to the registered skill dir (holds `.env`).
2. Source that `.env` (`set -a && . "{SKILL_PATH}/.env" && set +a`).
3. `cd` to `{SKILL_PATH}` / `~/.meta-skills/skills/namecheap`.
4. `/namecheap_init` → fill `.env` → re-run until OK.
5. Call `namecheap-cli -o json …` directly; parse JSON.
6. Confirm with the user before any DNS write, `--yes`, privacy disable/renew, or `dns delete --all`.

## Notes

- Namecheap API requires a **whitelisted client IP**. IP rejection ≠ bad API key.
  If the IP rotates: `ALL_PROXY=socks5://127.0.0.1:1080 namecheap-cli …`
  (needs `namecheap-python[cli,socks]`).
- DNS edits only apply while the domain uses **Namecheap BasicDNS**.
- Never commit `.env` / API keys.
- Exit codes: `0` success, `1` error, `130` interrupted.
