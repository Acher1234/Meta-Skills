# eset-application-management — Commands

API docs: [Application Management](https://help.eset.com/eset_connect/en-US/application_management.html)

| Slash | CLI | Endpoint |
|-------|-----|----------|
| `/eset_executables_list` | `python cli.py executables list [--page-size N] [--page-token T]` | `GET /v1/executables` |
| `/eset_executables_get` | `python cli.py executables get EXECUTABLE_UUID` | `GET /v1/executables/{executableUuid}` |
| `/eset_executables_block` | `python cli.py executables block EXECUTABLE_UUID` | `POST /v1/executables/{executableUuid}:block` |
| `/eset_executables_unblock` | `python cli.py executables unblock EXECUTABLE_UUID` | `POST /v1/executables/{executableUuid}:unblock` |
