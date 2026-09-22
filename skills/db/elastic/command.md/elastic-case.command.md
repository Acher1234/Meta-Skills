# elastic-case — Commands

Kibana Cases API. Implemented in `scripts/case.py` (`KibanaCase`). Confirm with the user before `create-from-alert`, `add-alert`, or `delete`.

`create-from-alert` opens a Security case (`owner`: `securitySolution`) and attaches the alert. `delete` removes the case **and** every attached alert.

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/db/elastic`.

| Slash | CLI | Description |
|-------|-----|-------------|
| `/elastic_kibana_case_get` | `python scripts/cli.py kibana case get {CASE_ID}` | Get a case |
| `/elastic_kibana_case_create_from_alert` | `python scripts/cli.py kibana case create-from-alert {ALERT_ID} [--json '{"title":"{TITLE}","description":"{DESCRIPTION}","tags":["{TAG}"],"severity":"{SEVERITY}"}']` | Create a case from an alert |
| `/elastic_kibana_case_add_alert` | `python scripts/cli.py kibana case add-alert {CASE_ID} {ALERT_ID}` | Put an alert on a case |
| `/elastic_kibana_case_delete` | `python scripts/cli.py kibana case delete {CASE_ID}` | Delete a case and its alerts |

Placeholders: `{CASE_ID}`, `{ALERT_ID}`, `{TITLE}`, `{DESCRIPTION}`, `{TAG}`, `{SEVERITY}`. `{ALERT_ID}` is the alert `_id` or `kibana.alert.uuid`. `--json` is a JSON object (not a file). Same Kibana URL/auth as dashboards (`URL` / `USERNAME` / `PASSWORD`).
