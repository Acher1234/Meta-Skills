## Example Workflows

Requires an unlocked session. **Confirm with the user** before create / edit / delete.

### Create a login with a generated password

```bash
PASS="$($BW generate -ulns --length 20)"
$BW get template item \
  | jq --arg p "$PASS" \
    '.name="Staging DB" | .login.username="app" | .login.password=$p' \
  | $BW encode \
  | $BW create item
```

**When user says "store this credential in Bitwarden"**, this skill should:
1. Confirm name / username / whether to generate the password
2. Prefer `$BW generate` over putting a password on the command line
3. Pipe template → `jq` → `encode` → `create item`
4. Return the new item id/name (not the password unless asked)

### Create a secure note

```bash
$BW get template item \
  | jq '.type=2 | .secureNote.type=0 | .name="VPN seed" | .notes="…"' \
  | $BW encode \
  | $BW create item
```

### Edit an existing password

```bash
$BW get item <exact-id> \
  | jq --arg p "$($BW generate -ulns --length 24)" '.login.password=$p' \
  | $BW encode \
  | $BW edit item <exact-id>
```

### Soft-delete then restore

```bash
$BW delete item <exact-id>       # trash (30 days)
$BW restore item <exact-id>
```

`--permanent` destroys the item for good — confirm twice before using it.
