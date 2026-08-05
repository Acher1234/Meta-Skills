# hexnode-devices — Commands

API docs: [Devices](https://www.hexnode.com/mobile-device-management/developers/devices/)

Implemented in `scripts/devices.py` (`DevicesClient` extends `HexnodeClient`).

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/mdm-antivirus/hexnode`.

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/hexnode_env` | `python scripts/cli.py env` | Validate `.env` (no network) |
| `/hexnode_devices_list` | `python scripts/cli.py devices list [--platform ios\|android\|windows] [--active\|--inactive] [--order-by asc\|desc] [--page N] [--per-page N]` | [`GET /devices/`](https://www.hexnode.com/mobile-device-management/developers/devices/list-all-devices/) |
| `/hexnode_devices_get` | `python scripts/cli.py devices get DEVICE_ID` | [`GET /devices/{id}/`](https://www.hexnode.com/mobile-device-management/developers/devices/retrieve-device-details/) |
| `/hexnode_devices_policies` | `python scripts/cli.py devices policies DEVICE_ID [--page N] [--per-page N]` | [`GET /devices/{id}/policies/`](https://www.hexnode.com/mobile-device-management/developers/devices/list-device-policies/) |
| `/hexnode_devices_applications` | `python scripts/cli.py devices applications DEVICE_ID [--page N] [--per-page N]` | [`GET /devices/{id}/applications/`](https://www.hexnode.com/mobile-device-management/developers/devices/list-all-applications/) |
| `/hexnode_devices_locations` | `python scripts/cli.py devices locations DEVICE_ID [--page N] [--per-page N]` | [`GET /devices/{id}/locations/`](https://www.hexnode.com/mobile-device-management/developers/devices/list-device-locations/) |

`--per-page` max is **250** on list / applications.

### Examples

```bash
python scripts/cli.py env
python scripts/cli.py devices list --per-page 50
python scripts/cli.py devices get 5
python scripts/cli.py devices policies 5
python scripts/cli.py devices applications 5 --per-page 100
python scripts/cli.py devices locations 5
```
