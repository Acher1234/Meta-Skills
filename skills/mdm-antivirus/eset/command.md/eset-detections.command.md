# eset-detections — Commands

API docs: [Incident Management](https://help.eset.com/eset_connect/en-US/incident_management.html)

### Detections (`detections`)

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/eset_detections_list` | `python cli.py detections list [--version v1\|v2] [--device UUID] [--start-time T] [--end-time T] [--page-size N]` | `GET /{version}/detections` |
| `/eset_detections_get` | `python cli.py detections get DETECTION_UUID [--version v1\|v2]` | `GET /{version}/detections/{detectionUuid}` |
| `/eset_detections_resolve` | `python cli.py detections resolve DETECTION_UUID [--note TEXT]` | `POST /v2/detections/{detectionUuid}:resolve` |
| `/eset_detections_batch-get` | `python cli.py detections batch-get UUID [UUID …]` | `POST /v2/detections:batchGet` |

### Detection groups (`detection-groups`)

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/eset_detection-groups_list` | `python cli.py detection-groups list [--page-size N]` | `GET /v2/detection-groups` |
| `/eset_detection-groups_get` | `python cli.py detection-groups get GROUP_UUID` | `GET /v2/detection-groups/{detectionGroupUuid}` |
| `/eset_detection-groups_resolve` | `python cli.py detection-groups resolve GROUP_UUID [--note TEXT]` | `POST /v2/detection-groups/{detectionGroupUuid}:resolve` |
| `/eset_detection-groups_search` | `python cli.py detection-groups search [--filter "resolved eq 0"] [--total-size]` | `POST /v2/detection-groups:search` |
