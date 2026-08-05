# eset-incidents — Commands

API docs: [Incident Management](https://help.eset.com/eset_connect/en-US/incident_management.html)

### Incidents (`incidents`)

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/eset_incidents_list` | `python cli.py incidents list [--page-size N]` | `GET /v2/incidents` |
| `/eset_incidents_get` | `python cli.py incidents get INCIDENT_UUID` | `GET /v2/incidents/{incidentUuid}` |
| `/eset_incidents_update-attributes` | `python cli.py incidents update-attributes INCIDENT_UUID [--assignee UUID] [--description D] [--name N] [--severity S]` | `POST /v2/incidents/{incidentUuid}/basic-attributes:update` |
| `/eset_incidents_close` | `python cli.py incidents close INCIDENT_UUID [--reason R] [--comment TEXT]` | `POST /v2/incidents/{incidentUuid}:close` |
| `/eset_incidents_reopen` | `python cli.py incidents reopen INCIDENT_UUID` | `POST /v2/incidents/{incidentUuid}:reopen` |

### Incident comments (`incident-comments`)

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/eset_incident-comments_list` | `python cli.py incident-comments list INCIDENT_UUID [--page-size N]` | `GET /v2/incidents/{incidentUuid}/comments` |
| `/eset_incident-comments_create` | `python cli.py incident-comments create INCIDENT_UUID --text TEXT` | `POST /v2/incidents/{incidentUuid}/comments` |
| `/eset_incident-comments_get` | `python cli.py incident-comments get INCIDENT_UUID COMMENT_UUID` | `GET /v2/incidents/{incidentUuid}/comments/{commentUuid}` |
| `/eset_incident-comments_delete` | `python cli.py incident-comments delete INCIDENT_UUID COMMENT_UUID` | `DELETE /v2/incidents/{incidentUuid}/comments/{commentUuid}` |
| `/eset_incident-comments_update-text` | `python cli.py incident-comments update-text INCIDENT_UUID COMMENT_UUID --text TEXT` | `POST /v2/incidents/{incidentUuid}/comments/{commentUuid}/text:update` |
