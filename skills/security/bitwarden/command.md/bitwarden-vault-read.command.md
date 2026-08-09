# bitwarden-vault-read — Commands

Requires unlocked session (`eval "$(…/scripts/session.py)"` first).
All commands support `--help` for full options.

| Command | Description |
|---------|-------------|
| `bw list items` | List vault items (filters: `--search`, `--folderid`, `--collectionid`, `--organizationid`, `--url`, `--trash`) |
| `bw list folders` | List folders |
| `bw list collections` | List collections (all orgs) |
| `bw list organizations` | List organizations |
| `bw list org-collections --organizationid <id>` | Collections for one org |
| `bw list org-members --organizationid <id>` | Members for one org |
| `bw get item <id-or-search>` | One item (exact id or search; error if ambiguous) |
| `bw get username <id-or-search>` | Login username |
| `bw get password <id-or-search>` | Login password (secret) |
| `bw get uri <id-or-search>` | Login URI |
| `bw get totp <id-or-search>` | TOTP code (secret) |
| `bw get notes <id-or-search>` | Item notes (secret) |
| `bw get folder <id-or-name>` | One folder |
| `bw get collection <id>` | One collection |
| `bw get organization <id>` | One organization |
| `bw get attachment <file> --itemid <id>` | Download attachment (`--output` dir/ or file) |
| `bw get template <type>` | JSON template (`item`, `folder`, …) |
| `bw get fingerprint me` | Account fingerprint phrase |
| `bw generate` | Generate password (`-ulns --length N`) or passphrase (`--passphrase`) |

---
