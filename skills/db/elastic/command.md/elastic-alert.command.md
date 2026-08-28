# elastic-alert — Commands

Elastic Security detection **alerts** (signals) and **rules**.
Alerts: `scripts/alert.py` (`Alert`). Rules: `scripts/security_rule.py`. Confirm before alert `delete` and rule `create` / `update` / `delete`. Rule `update` is a full replace (`PUT`).

`--id` / `{ALERT_ID}` is the alert `_id` or `kibana.alert.uuid`. For rules, `--id` is the saved-object UUID and `--rule-id` is the stable `rule_id`. Rule get / update / delete need one of them.

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/db/elastic`.

| Slash | CLI | Description |
|-------|-----|-------------|
| `/elastic_alert_get` | `python scripts/cli.py alert get {ALERT_ID}` | Get a detection alert |
| `/elastic_alert_delete` | `python scripts/cli.py alert delete {ALERT_ID}` | Delete a detection alert |
| `/elastic_alert_security_rule_get` | `python scripts/cli.py alert security-rule get [--id {ID}] [--rule-id {RULE_ID}]` | Get a rule |
| `/elastic_alert_security_rule_create` | `python scripts/cli.py alert security-rule create --json '{"name":"{NAME}","description":"{DESCRIPTION}","type":"query","query":"{QUERY}","language":"kuery","data_view_id":"{DATA_VIEW_ID}","index":["{INDEX}*"],"enabled":false,"interval":"{INTERVAL}","from":"{FROM}","severity":"{SEVERITY}","risk_score":{RISK_SCORE}}'` | Create a rule |
| `/elastic_alert_security_rule_update` | `python scripts/cli.py alert security-rule update [--id {ID}] [--rule-id {RULE_ID}] --json '{"name":"{NAME}","description":"{DESCRIPTION}","type":"query","query":"{QUERY}","language":"kuery","data_view_id":"{DATA_VIEW_ID}","index":["{INDEX}*"],"enabled":false,"interval":"{INTERVAL}","from":"{FROM}","severity":"{SEVERITY}","risk_score":{RISK_SCORE}}'` | Replace a rule |
| `/elastic_alert_security_rule_delete` | `python scripts/cli.py alert security-rule delete [--id {ID}] [--rule-id {RULE_ID}]` | Delete a rule |

Placeholders: `{ALERT_ID}`, `{ID}`, `{RULE_ID}`, `{NAME}`, `{DESCRIPTION}`, `{QUERY}`, `{DATA_VIEW_ID}`, `{INDEX}`, `{INTERVAL}`, `{FROM}`, `{SEVERITY}`, `{RISK_SCORE}`. Use `data_view_id` **or** `index` (wildcard pattern `{INDEX}*`), not both — drop the unused key. `--json` is a JSON object (not a file). Same Kibana URL/auth as dashboards (`URL` / `USERNAME` / `PASSWORD`).
