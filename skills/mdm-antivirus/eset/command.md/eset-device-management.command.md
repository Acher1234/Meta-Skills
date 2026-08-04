# eset-device-management — Commands

API docs: [Device Management](https://help.eset.com/eset_connect/en-US/device_management.html)

### Device groups (`groups`)

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/eset_groups_list` | `python cli.py groups list [--page-size N] [--page-token T]` | `GET /v1/device_groups` |
| `/eset_groups_devices` | `python cli.py groups devices GROUP_UUID [--page-size N]` | `GET /v1/device_groups/{groupUuid}/devices` |

### Devices (`devices`)

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/eset_devices_list` | `python cli.py devices list [--page-size N] [--page-token T]` | `GET /v1/devices` |
| `/eset_devices_get` | `python cli.py devices get DEVICE_UUID` | `GET /v1/devices/{deviceUuid}` |
| `/eset_devices_move` | `python cli.py devices move DEVICE_UUID --group GROUP_UUID` | `POST /v1/devices/{deviceUuid}:move` |
| `/eset_devices_rename` | `python cli.py devices rename DEVICE_UUID --name NAME` | `POST /v1/devices/{deviceUuid}:rename` |
| `/eset_devices_batch-get` | `python cli.py devices batch-get UUID [UUID …]` | `GET /v1/devices:batchGet` |
| `/eset_devices_batch-import` | `python cli.py devices batch-import --file devices.json` | `POST /v1/devices:batchImport` |
