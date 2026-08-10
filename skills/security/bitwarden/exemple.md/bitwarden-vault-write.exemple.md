## Example Workflows

Requires an unlocked session. **Confirm with the user** before create / edit / delete.
Prefer the one-liners in `command.md/bitwarden-vault-write.command.md`.

### Create a login with a generated password

```bash
PASS="$(bw generate -ulns --length 20)"
echo "{\"type\":1,\"name\":\"Staging DB\",\"favorite\":false,\"reprompt\":0,\"notes\":null,\"folderId\":null,\"fields\":[],\"passwordHistory\":[],\"login\":{\"uris\":[],\"username\":\"app\",\"password\":\"$PASS\",\"totp\":null,\"fido2Credentials\":[]}}" | bw encode | bw create item
```

**When user says "store this credential in Bitwarden"**, this skill should:
1. Confirm name / username / whether to generate the password
2. Prefer `bw generate` over putting a password on the command line
3. `echo '<JSON>' | bw encode | bw create item`
4. Return the new item id/name (not the password unless asked)

### Create a secure note

```bash
echo '{"type":2,"name":"VPN seed","favorite":false,"reprompt":0,"notes":"…","folderId":null,"fields":[],"passwordHistory":[],"secureNote":{"type":0}}' | bw encode | bw create item
```

### Edit an existing password

```bash
PASS="$(bw generate -ulns --length 24)"
bw get item <exact-id> | jq --arg p "$PASS" '.login.password=$p' | bw encode | bw edit item <exact-id>
```

### Soft-delete then restore

```bash
bw delete item <exact-id>
bw restore item <exact-id>
```

`--permanent` destroys the item for good — confirm twice before using it.
