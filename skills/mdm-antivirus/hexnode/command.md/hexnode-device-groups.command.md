# hexnode-device-groups — Commands

API docs: [Device groups](https://www.hexnode.com/mobile-device-management/developers/device-groups/)

Implemented in `scripts/device_groups.py` (`DeviceGroupsClient` extends `HexnodeClient`).

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/mdm-antivirus/hexnode`.

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/hexnode_device-groups_list` | `python scripts/cli.py device-groups list [--page N] [--per-page N]` | [`GET /devicegroups/`](https://www.hexnode.com/mobile-device-management/developers/device-groups/list-device-groups/) |
| `/hexnode_device-groups_create` | `python scripts/cli.py device-groups create --name NAME --description D [--device ID …]` | [`POST /devicegroups/`](https://www.hexnode.com/mobile-device-management/developers/device-groups/create-device-group/) |
| `/hexnode_device-groups_get` | `python scripts/cli.py device-groups get GROUP_ID` | [`GET /devicegroups/{id}/`](https://www.hexnode.com/mobile-device-management/developers/device-groups/retrieve-device-group-details/) |
| `/hexnode_device-groups_update` | `python scripts/cli.py device-groups update GROUP_ID --name NAME --description D [--device ID …]` | [`PUT /devicegroups/{id}/`](https://www.hexnode.com/mobile-device-management/developers/device-groups/update-device-group/) |
| `/hexnode_device-groups_add-remove` | `python scripts/cli.py device-groups add-remove GROUP_ID [--add ID …] [--remove ID …]` | [`POST /devicegroups/{id}/`](https://www.hexnode.com/mobile-device-management/developers/device-groups/add-remove-devices/) |
| `/hexnode_device-groups_delete` | `python scripts/cli.py device-groups delete GROUP_ID` | [`DELETE /devicegroups/{id}/`](https://www.hexnode.com/mobile-device-management/developers/device-groups/delete-device-group/) |

Confirm before `create` / `update` / `add-remove` / `delete`.

### Examples

```bash
python scripts/cli.py device-groups list
python scripts/cli.py device-groups get 1
python scripts/cli.py device-groups create --name "iOS devices" --description "Group of iOS devices" --device 1 --device 2
python scripts/cli.py device-groups add-remove 1 --add 3 --remove 2
# confirm before: python scripts/cli.py device-groups delete 1
```
