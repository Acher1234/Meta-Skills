# bitwarden-send — Commands

Docs: https://bitwarden.com/help/send-cli/

Create/list/get/delete need an unlocked session. `receive` does not.
The `accessUrl` **is** the secret. All commands support `--help`.

| Command | Description |
|---------|-------------|
| `bw send` | Create text or file Send (`-n` name, `-d` days, `-f` file, `--hidden`, …) |
| `bw send list` | List Sends |
| `bw send get <id>` | Get one Send |
| `bw send delete <id>` | Delete a Send |
| `bw send receive <url>` | Access a Send (`--password` if protected) |

---
