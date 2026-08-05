# hexnode-users — Commands

API docs: [Users](https://www.hexnode.com/mobile-device-management/developers/users/)

Implemented in `scripts/users.py` (`UsersClient` extends `HexnodeClient`).

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/mdm-antivirus/hexnode`.

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/hexnode_users_list` | `python scripts/cli.py users list [--order-by asc\|desc] [--user-type local\|"active directory"] [--enrollment-status enrolled\|unenrolled] [--page N] [--per-page N]` | [`GET /users/`](https://www.hexnode.com/mobile-device-management/developers/users/list-all-users/) |
| `/hexnode_users_create` | `python scripts/cli.py users create --name NAME --email EMAIL [--phoneno N] [--password P]` | [`POST /users/`](https://www.hexnode.com/mobile-device-management/developers/users/create-user/) |
| `/hexnode_users_get` | `python scripts/cli.py users get USER_ID` | [`GET /users/{id}/`](https://www.hexnode.com/mobile-device-management/developers/users/retrieve-user-details/) |
| `/hexnode_users_edit` | `python scripts/cli.py users edit USER_ID --name NAME --email EMAIL [--phoneno N] [--password P]` | [`PUT /users/{id}/`](https://www.hexnode.com/mobile-device-management/developers/users/edit-user/) |
| `/hexnode_users_delete` | `python scripts/cli.py users delete USER_ID` | [`DELETE /users/{id}/`](https://www.hexnode.com/mobile-device-management/developers/users/delete-user/) |
| `/hexnode_users_send-enrollment` | `python scripts/cli.py users send-enrollment USER_ID --ownership personal\|corporate\|user_choice` | [`POST /users/{id}/send_request/`](https://www.hexnode.com/mobile-device-management/developers/users/send-enrollment-request/) |

**Destructive:** `users delete` also **disenrolls all devices** for that user — confirm with the user first. Prefer confirming `create` / `edit` / `send-enrollment` before running.

### Examples

```bash
python scripts/cli.py users list --per-page 50
python scripts/cli.py users get 1
python scripts/cli.py users create --name "Neil" --email neil@example.com
python scripts/cli.py users edit 13 --name "Neil" --email neil@example.com
python scripts/cli.py users send-enrollment 13 --ownership personal
# confirm before: python scripts/cli.py users delete 13
```
