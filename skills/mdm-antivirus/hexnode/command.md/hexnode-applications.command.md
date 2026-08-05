# hexnode-applications — Commands

API docs: [Applications](https://www.hexnode.com/mobile-device-management/developers/applications/)

Implemented in `scripts/application.py` (`ApplicationClient` extends `HexnodeClient`). Portal app catalog (distinct from `devices applications`, which lists apps *on a device*).

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/mdm-antivirus/hexnode`.

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/hexnode_apps_list` | `python scripts/cli.py apps list [--app-type store\|web\|enterprise] [--platform ios\|android] [--order-by asc\|desc] [--page N] [--per-page N]` | [`GET /applications/`](https://www.hexnode.com/mobile-device-management/developers/applications/list-all-apps/) |
| `/hexnode_apps_search` | `python scripts/cli.py apps search --keyword NAME --platform ios\|android [--country us]` | [`GET /applications/searchapp/`](https://www.hexnode.com/mobile-device-management/developers/applications/search-app/) |
| `/hexnode_apps_add` | `python scripts/cli.py apps add --file app.json` / `apps add --name N --app-type store\|web --platform ios\|android --category C --icon URL …` | [`POST /applications/`](https://www.hexnode.com/mobile-device-management/developers/applications/add-app-to-list/) |
| `/hexnode_apps_get` | `python scripts/cli.py apps get APP_ID` | [`GET /applications/{id}/`](https://www.hexnode.com/mobile-device-management/developers/applications/retrieve-app-details/) |

For `apps add`, prefer `--file` when iOS store fields (`appstore_id`, `bundle_size`, …) are required. Confirm before adding.

### Examples

```bash
python scripts/cli.py apps list --app-type store --platform ios
python scripts/cli.py apps search --keyword youtube --platform android --country us
python scripts/cli.py apps get 1
# python scripts/cli.py apps add --file app.json
```
