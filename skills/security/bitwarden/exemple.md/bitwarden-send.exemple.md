## Example Workflows

Create/list/get/delete need an unlocked session. The `accessUrl` **is** the secret.

### Share text for 7 days

```bash
$BW send -n "OTP backup" -d 7 --hidden "one-time payload"
# Output includes accessUrl — treat like a password
```

**When user says "share this securely via Bitwarden Send"**, this skill should:
1. Confirm name, lifetime (`-d`), and whether text or file
2. Run `bw send …`
3. Hand back the `accessUrl` carefully (do not paste casually into chat logs)

### Share a file

```bash
$BW send -n "Contract PDF" -d 14 -f /path/to/file.pdf
```

### List / delete / receive

```bash
$BW send list
$BW get send <id>
$BW delete send <id>

# Receiver (no vault unlock required):
bw receive --password <access-password> 'https://…/#/send/…'
```
