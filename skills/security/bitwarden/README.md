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

Either way the vault needs the master password to produce a session key. The password is
used once and never stored; only the session key is cached, in the skill dir for
`BW_SESSION_TTL` minutes (default 15). Because that prompt needs a terminal, an agent
cannot run it — the user does, once per session window.

On macOS you can widen that window:

```bash
python scripts/cli.py keychain set    # prompts once, then caches the session key
```

The session key then lives in the encrypted login keychain rather than a plaintext file,
and stays valid until `lock` or `logout` revokes it — so an agent keeps working without
asking again. The master password is still never written anywhere. `keychain status`
reports the state and `keychain clear` removes the entry.

Storing the session rather than the password is deliberate: a leaked session key
decrypts the vault until you revoke it, whereas a leaked master password is a permanent
account takeover that also works on the Web Vault.

## Dependencies

Node 22 and the pinned `bw` binary — see [`dependencies.md`](dependencies.md).
Agent-facing reference: [`SKILL.md`](SKILL.md).
