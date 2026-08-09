## Example Workflows

Requires an unlocked session first (`bitwarden-session`).

### Find an item and copy its password

```bash
# 1. Search
$BW list items --search github

# 2. Get password (secret — prefer clipboard, not chat)
$BW get password github | pbcopy
# or only if the user asked to see it:
$BW get password github
```

**When user says "what's my GitHub password"**, this skill should:
1. Ensure session is unlocked
2. Prefer `$BW get password github | pbcopy` (or equivalent) over printing in chat
3. Only print the secret if the user explicitly asked to see it

### List then resolve ambiguity

```bash
$BW list items --search aws
# several matches → pick an id from the list
$BW get item <exact-id>
```

`bw get` returns **one** result; if several match it errors — use `list --search` first.

### Generate a strong password

```bash
$BW generate -ulns --length 20
$BW generate --passphrase --words 4 --separator -
```

### Download an attachment

```bash
$BW get attachment secret.pdf --itemid <item-id> --output ~/Downloads/
```

`--output` must end with `/` (directory) or a full filename.
