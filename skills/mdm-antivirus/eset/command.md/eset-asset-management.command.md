# eset-asset-management — Commands

API docs: [Asset Management](https://help.eset.com/eset_connect/en-US/asset_management.html)

### API gateway

`ESET_ASSET_URL` — `https://<region>.automation.eset.systems` (from `ESET_URL` unless overridden).

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/eset_assets_create` | `python cli.py assets create --name NAME [--parent PARENT_UUID]` | `POST /v1/groups` |
| `/eset_assets_delete` | `python cli.py assets delete GROUP_UUID` | `DELETE /v1/groups/{groupUuid}` |
| `/eset_assets_move` | `python cli.py assets move GROUP_UUID --parent PARENT_UUID` | `POST /v1/groups/{groupUuid}:move` |
| `/eset_assets_rename` | `python cli.py assets rename GROUP_UUID --name NAME` | `POST /v1/groups/{groupUuid}:rename` |

### CLI flag → JSON body

JSON fields follow the ESET Connect schema. CLI flags are aliases only.

| CLI | JSON | Example |
|-----|------|---------|
| `--name` (rename) | `displayName` | `python cli.py assets rename UUID --name VO2-Laptops` → `{"displayName": "VO2-Laptops"}` |
| `--name` (create) | `group.displayName` | `python cli.py assets create --name VO2-Laptops` → `{"group": {"displayName": "VO2-Laptops"}}` |
| `--parent` (create) | `group.parentGroupUuid` | nested under `group` |
| `--parent` (move) | `newParentUuid` | `python cli.py assets move UUID --parent PARENT_UUID` → `{"newParentUuid": "PARENT_UUID"}` |
