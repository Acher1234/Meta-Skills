# bitwarden-vault-write — Commands

Requires unlocked session. **Confirm with the user** before create / edit / delete.
Payloads: JSON → `bw encode` → create/edit (`jq` helps). All commands support `--help`.

| Command | Description |
|---------|-------------|
| `bw create item` | Create vault item from encoded JSON |
| `bw create folder` | Create folder from encoded JSON |
| `bw create attachment --file <path> --itemid <id>` | Attach file to existing item |
| `bw create org-collection --organizationid <id>` | Create org collection from encoded JSON |
| `bw edit item <exact-id>` | Replace item from encoded JSON |
| `bw edit folder <exact-id>` | Replace folder from encoded JSON |
| `bw edit org-collection <exact-id> --organizationid <id>` | Replace org collection |
| `bw delete item <exact-id>` | Move item to trash (30 days) |
| `bw delete item <exact-id> --permanent` | Irreversible delete |
| `bw delete attachment\|folder\|org-collection <exact-id>` | Delete other object types |
| `bw restore item <exact-id>` | Restore item from trash |
| `bw encode` | Base64-encode stdin JSON for create/edit |
| `bw move <itemid> <orgid>` | Move item into an organization |

Item types: login=`1`, secure note=`2`, card=`3`, identity=`4`, ssh key=`5`.

---
