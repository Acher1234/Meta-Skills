## Example Workflows

### Connect once from `.env`

Most common start — unlock the vault before any vault command:

```bash
export CURRENT_SKILL_DIRECTORY="{SKILL_PATH}"   # directory that holds .env
eval "$(~/.meta-skills/.venv/bin/python ~/.meta-skills/skills/security/bitwarden/scripts/session.py)"

# Sets: BW_SESSION, BITWARDENCLI_APPDATA_DIR, BW
$BW status
# {"status":"unlocked", "serverUrl":"…", "userEmail":"…"}
```

`session.py` calls `bw login --apikey` **only** if status is `unauthenticated`.
If already `locked`, it unlocks without logging in again.

**When user says "connect to Bitwarden" / "unlock my vault"**, this skill should:
1. Ensure `CURRENT_SKILL_DIRECTORY` points at the registered skill dir (with `.env`)
2. Run `eval "$(…/scripts/session.py)"`
3. Confirm with `$BW status` → `unlocked`

### Manual login then unlock (no session.py)

```bash
export BITWARDENCLI_APPDATA_DIR="$CURRENT_SKILL_DIRECTORY/.bw-appdata"
export BW_CLIENTID BW_CLIENTSECRET BW_PASSWORD   # from .env
bw config server "$BW_SERVER"
bw login --apikey          # only if unauthenticated
export BW_SESSION="$(bw unlock --passwordenv BW_PASSWORD --raw)"
```

### Lock / logout when finished

```bash
bw lock
unset BW_SESSION
# or fully sign out:
bw logout
unset BW_SESSION
```
