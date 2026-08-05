# hexnode-policies — Commands

API docs: [Policies](https://www.hexnode.com/mobile-device-management/developers/policies/)

Implemented in `scripts/policy.py` (`PolicyClient` extends `HexnodeClient`). Portal policies (distinct from `devices policies`, which lists policies *on a device*). Platform payload schemas: [`references/policy-platforms.md`](../references/policy-platforms.md).

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/mdm-antivirus/hexnode`.

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/hexnode_policies_list` | `python scripts/cli.py policies list [--page N] [--per-page N]` | [`GET /policy/`](https://www.hexnode.com/mobile-device-management/developers/policies/list-policies/) |
| `/hexnode_policies_create` | `python scripts/cli.py policies create --file policy.json` / `policies create --name NAME [--description D]` | [`POST /policy/`](https://www.hexnode.com/mobile-device-management/developers/policies/create-policy/) |
| `/hexnode_policies_get` | `python scripts/cli.py policies get POLICY_ID` | [`GET /policy/{id}/`](https://www.hexnode.com/mobile-device-management/developers/policies/policy-details/) |
| `/hexnode_policies_edit` | `python scripts/cli.py policies edit POLICY_ID --file policy.json` | [`PUT /policy/{id}/`](https://www.hexnode.com/mobile-device-management/developers/policies/edit-policy/) |
| `/hexnode_policies_archive` | `python scripts/cli.py policies archive POLICY_ID` | [`DELETE /policy/{id}/`](https://www.hexnode.com/mobile-device-management/developers/policies/archive-policy/) |

Platform dictionaries for create/edit (not separate CLI commands): [iOS](https://www.hexnode.com/mobile-device-management/developers/policies/ios-policies/), [Android](https://www.hexnode.com/mobile-device-management/developers/policies/android-policies/), [macOS](https://www.hexnode.com/mobile-device-management/developers/policies/macos-policies/), [Windows](https://www.hexnode.com/mobile-device-management/developers/policies/windows-policies/). Prefer `--file` for full payloads. **Archive** dissociates the policy from all devices — confirm first.

### Examples

```bash
python scripts/cli.py policies list
python scripts/cli.py policies get 129
python scripts/cli.py policies create --file policy.json
python scripts/cli.py policies edit 129 --file policy.json
# confirm before: python scripts/cli.py policies archive 129
```
