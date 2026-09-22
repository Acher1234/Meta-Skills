# elastic-visualization — Commands

Kibana visualizations API. Implemented in `scripts/visualization.py` (`KibanaVisualization`) and `scripts/model/visualization.py`.

`update` is a full replace (`PUT`). Confirm with the user before update or delete.

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/db/elastic`.

| Slash | CLI | Description |
|-------|-----|-------------|
| `/elastic_kibana_visualization_list` | `python scripts/cli.py kibana visualization list` | List visualizations |
| `/elastic_kibana_visualization_get` | `python scripts/cli.py kibana visualization get {VIS_ID}` | Get a visualization |
| `/elastic_kibana_visualization_create` | `python scripts/cli.py kibana visualization create --json '{"type":"xy","title":"{TITLE}","layers":[{"type":"line","data_source":{"type":"data_view_spec","index_pattern":"{INDEX_PATTERN}","time_field":"{TIME_FIELD}"},"x":{"operation":"date_histogram","field":"{TIME_FIELD}"},"y":[{"operation":"count"}]}]}'` | Create a visualization |
| `/elastic_kibana_visualization_update` | `python scripts/cli.py kibana visualization update {VIS_ID} --json '{"type":"xy","title":"{TITLE}","layers":[{"type":"line","data_source":{"type":"data_view_spec","index_pattern":"{INDEX_PATTERN}","time_field":"{TIME_FIELD}"},"x":{"operation":"date_histogram","field":"{TIME_FIELD}"},"y":[{"operation":"count"}]}]}'` | Replace a visualization |
| `/elastic_kibana_visualization_delete` | `python scripts/cli.py kibana visualization delete {VIS_ID}` | Delete a visualization |

Placeholders: `{VIS_ID}`, `{TITLE}`, `{INDEX_PATTERN}`, `{TIME_FIELD}`.
