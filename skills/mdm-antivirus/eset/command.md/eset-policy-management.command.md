# eset-policy-management — Commands

API docs: [Policy Management](https://help.eset.com/eset_connect/en-US/policy_management.html)

### API gateway

`ESET_POLICY_URL` — `https://<region>.automation.eset.systems` (from `ESET_URL` unless overridden).

### Policies (`policies`)

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/eset_policies_list` | `python cli.py policies list [--page-size N] [--page-token T]` | `GET /v2/policies` |
| `/eset_policies_get` | `python cli.py policies get POLICY_UUID` | `GET /v2/policies/{policyUuid}` |
| `/eset_policies_create` | `python cli.py policies create --file policy.json` | `POST /v2/policies` |
| `/eset_policies_delete` | `python cli.py policies delete POLICY_UUID` | `DELETE /v2/policies/{policyUuid}` |

### Policy assignments (`policy-assignments`)

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/eset_policy-assignments_list` | `python cli.py policy-assignments list [--page-size N]` | `GET /v2/policy-assignments` |
| `/eset_policy-assignments_get` | `python cli.py policy-assignments get ASSIGNMENT_UUID` | `GET /v2/policy-assignments/{assignmentUuid}` |
| `/eset_policy-assignments_assign` | `python cli.py policy-assignments assign --file assignment.json` | `POST /v2/policy-assignments` |
| `/eset_policy-assignments_unassign` | `python cli.py policy-assignments unassign ASSIGNMENT_UUID` | `DELETE /v2/policy-assignments/{assignmentUuid}` |
| `/eset_policy-assignments_update-ranking` | `python cli.py policy-assignments update-ranking ASSIGNMENT_UUID --ranking N` | `POST /v2/policy-assignments/{assignmentUuid}:updateRanking` |
