# eset-edr — Commands

API docs: [Incident Management](https://help.eset.com/eset_connect/en-US/incident_management.html)

### API gateway

`ESET_INCIDENT_URL` — `https://<region>.incident-management.eset.systems` (from `ESET_URL` unless overridden).

Requires ESET Inspect.

### EDR rules (`edr-rules`)

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/eset_edr-rules_list` | `python cli.py edr-rules list [--page-size N]` | `GET /v2/edr-rules` |
| `/eset_edr-rules_create` | `python cli.py edr-rules create --file rule.json` | `POST /v2/edr-rules` |
| `/eset_edr-rules_get` | `python cli.py edr-rules get RULE_UUID` | `GET /v2/edr-rules/{ruleUuid}` |
| `/eset_edr-rules_delete` | `python cli.py edr-rules delete RULE_UUID` | `DELETE /v2/edr-rules/{ruleUuid}` |
| `/eset_edr-rules_enable` | `python cli.py edr-rules enable RULE_UUID` | `POST /v2/edr-rules/{ruleUuid}:enable` |
| `/eset_edr-rules_disable` | `python cli.py edr-rules disable RULE_UUID` | `POST /v2/edr-rules/{ruleUuid}:disable` |
| `/eset_edr-rules_update-definition` | `python cli.py edr-rules update-definition RULE_UUID --xml-definition XML` | `POST /v2/edr-rules/{ruleUuid}:updateDefinition` |

### EDR exclusions (`edr-exclusions`)

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/eset_edr-exclusions_list` | `python cli.py edr-exclusions list [--page-size N]` | `GET /v2/edr-rule-exclusions` |
| `/eset_edr-exclusions_create` | `python cli.py edr-exclusions create --file exclusion.json` | `POST /v2/edr-rule-exclusions` |
| `/eset_edr-exclusions_get` | `python cli.py edr-exclusions get EXCLUSION_UUID` | `GET /v2/edr-rule-exclusions/{exclusionUuid}` |
| `/eset_edr-exclusions_delete` | `python cli.py edr-exclusions delete EXCLUSION_UUID` | `DELETE /v2/edr-rule-exclusions/{exclusionUuid}` |
| `/eset_edr-exclusions_update-definition` | `python cli.py edr-exclusions update-definition EXCLUSION_UUID --xml-definition XML` | `POST /v2/edr-rule-exclusions/{exclusionUuid}:updateDefinition` |
