# elastic-data-view — Commands

Kibana data views API. Implemented in `scripts/data_view.py` (`KibanaDataView`) and `scripts/model/data_view.py`.

`title` is the index pattern (wildcards allowed). `name` is the display name. `timeFieldName` is the time field.

`update` is a **partial** `POST` — only fields in `--json` change. Confirm with the user before create, update, or delete.

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/db/elastic`.

| Slash | CLI | Description |
|-------|-----|-------------|
| `/elastic_kibana_data_view_get` | `python scripts/cli.py kibana data-view get {DATA_VIEW_ID}` | Get a data view |
| `/elastic_kibana_data_view_create` | `python scripts/cli.py kibana data-view create --json '{"title":"{INDEX}*","name":"{NAME}","timeFieldName":"{TIME_FIELD}"}'` | Create a data view |
| `/elastic_kibana_data_view_update` | `python scripts/cli.py kibana data-view update {DATA_VIEW_ID} --json '{"title":"{INDEX}*","name":"{NAME}","timeFieldName":"{TIME_FIELD}"}'` | Patch a data view |
| `/elastic_kibana_data_view_delete` | `python scripts/cli.py kibana data-view delete {DATA_VIEW_ID}` | Delete a data view |

Placeholders: `{DATA_VIEW_ID}`, `{INDEX}`, `{NAME}`, `{TIME_FIELD}`. `--json` is a JSON object (not a file); the client wraps it as `{ "data_view": … }`.
