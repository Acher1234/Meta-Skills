# elastic-dashboard — Commands

Kibana dashboards API. Implemented in `scripts/kibana.py` (`Kibana`) and `scripts/model/dashboard.py`.

`update` is a full replace (`PUT`). Confirm with the user before update.

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/db/elastic`.

| Slash | CLI | Description |
|-------|-----|-------------|
| `/elastic_kibana_dashboard_list` | `python scripts/cli.py kibana dashboard list` | List dashboards from `.kibana` |
| `/elastic_kibana_dashboard_get` | `python scripts/cli.py kibana dashboard get {DASH_ID}` | Get a dashboard |
| `/elastic_kibana_dashboard_create` | `python scripts/cli.py kibana dashboard create --json '{"title":"{TITLE}","panels":[{"type":"vis","grid":{"x":0,"y":0,"w":24,"h":15},"config":{"ref_id":"{VIS_ID}"}}]}'` | Create a dashboard |
| `/elastic_kibana_dashboard_update` | `python scripts/cli.py kibana dashboard update {DASH_ID} --json '{"title":"{TITLE}","panels":[{"type":"vis","grid":{"x":0,"y":0,"w":24,"h":15},"config":{"ref_id":"{VIS_ID}"}}]}'` | Replace a dashboard |

Placeholders: `{DASH_ID}`, `{TITLE}`, `{VIS_ID}`.
