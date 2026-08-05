# bitwarden

Bitwarden vault CLI (read, write, Send) wrapping [`bw`](https://bitwarden.com/help/cli/),
with JSON output and secrets masked by default.

## Install

```bash
export CURRENT_SKILL_DIRECTORY="$PWD/.cursor/skills/bitwarden"
cd ~/.meta-skills/skills/security/bitwarden
~/.meta-skills/install.sh pip init . && ~/.meta-skills/install.sh npm init .
python scripts/cli.py setup
```

`setup` asks for the server and the auth method, writes the `.env` at `chmod 600`,
offers the macOS keychain, and verifies everything by unlocking. Then:

```bash
python scripts/cli.py list items --search github
python scripts/cli.py get password github --clipboard
python scripts/cli.py create item --name "Staging DB" --username app --generate
```

## Authentication

Either an **email + master password** (nothing to copy) or a **personal API key**
(Web Vault → Account settings → Security → Keys). The API key is the one that survives
two-step login; with email auth and 2FA on, unlock takes a code:

```bash
python scripts/cli.py unlock --code 123456
```

Either way the vault needs the master password to produce a session key, cached in the
skill dir for `BW_SESSION_TTL` minutes (default 15). Because that prompt needs a
terminal, an agent cannot run it — the user does, once per session window.

On macOS you can remove that friction entirely:

```bash
python scripts/cli.py keychain set    # `security` prompts, the password never enters Python
```

The master password then lives in the keychain instead of a prompt, and unlocking
becomes silent — including from an agent. `keychain status` reports the state and
`keychain clear` removes the entry.

## Dependencies

Node 22 and the pinned `bw` binary — see [`dependencies.md`](dependencies.md).
Agent-facing reference: [`SKILL.md`](SKILL.md).
