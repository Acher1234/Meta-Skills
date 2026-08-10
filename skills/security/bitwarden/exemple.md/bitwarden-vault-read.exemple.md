## Example Workflows

Requires an unlocked session first (see SKILL.md Connect / Working directory).

### Find an item and copy its password

```bash
bw list items --search github
bw get password github | pbcopy   # macOS; Linux: xclip -selection clipboard / wl-copy
# or only if the user asked to see it:
bw get password github
```

**When user says "what's my GitHub password"**, this skill should:
1. Ensure session is unlocked
2. Prefer clipboard over printing in chat
3. Only print the secret if the user explicitly asked to see it

### List then resolve ambiguity

```bash
bw list items --search aws
bw get item <exact-id>
```

`bw get` returns **one** result; if several match it errors — use `list --search` first.

### Generate a strong password

```bash
bw generate -ulns --length 20
bw generate --passphrase --words 4 --separator -
```

### Download an attachment

```bash
bw get attachment secret.pdf --itemid <item-id> --output ~/Downloads/
```

`--output` must end with `/` (directory) or a full filename.
