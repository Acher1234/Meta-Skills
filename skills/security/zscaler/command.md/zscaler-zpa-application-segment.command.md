# zscaler-zpa-application-segment — Commands

ZPA application segments via `LegacyZPAClient`. Implemented in `scripts/zpa/application_segment.py`.
Confirm before `update` and `delete`. Update only changes domains / IPs and TCP/UDP ports; other fields are kept. `--domain`, `--tcp-port`, and `--udp-port` replace unless `--append`.

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/security/zscaler`.

| Slash | CLI | Description |
|-------|-----|-------------|
| `/zscaler_zpa_application_segment_list` | `python scripts/cli.py zpa application-segment list [--search {SEARCH}]` | List segments |
| `/zscaler_zpa_application_segment_get` | `python scripts/cli.py zpa application-segment get [--id {SEGMENT_ID}] [--name {SEGMENT_NAME}]` | Get by id or name |
| `/zscaler_zpa_application_segment_update` | `python scripts/cli.py zpa application-segment update [--id {SEGMENT_ID}] [--name {SEGMENT_NAME}] [--domain {DOMAIN}] [--tcp-port {PORT}] [--udp-port {PORT}]` | Update domains / ports |
| `/zscaler_zpa_application_segment_delete` | `python scripts/cli.py zpa application-segment delete [--id {SEGMENT_ID}] [--name {SEGMENT_NAME}] [--force]` | Delete a segment |

`--domain` is an IP, FQDN, or URL (repeatable). Ports accept a single value (`443`) or a range (`8080-8081`). Repeatable: `--domain`, `--tcp-port`, `--udp-port`. `--force` unmaps the segment from its segment group before delete.

### Examples

```bash
python scripts/cli.py zpa application-segment list
python scripts/cli.py zpa application-segment list --search {SEARCH}
python scripts/cli.py zpa application-segment get --id {SEGMENT_ID}
python scripts/cli.py zpa application-segment get --name {SEGMENT_NAME}
python scripts/cli.py zpa application-segment update --name {SEGMENT_NAME} --domain {DOMAIN} --tcp-port 443
python scripts/cli.py zpa application-segment update --id {SEGMENT_ID} --append --domain {DOMAIN} --tcp-port 8080-8081
python scripts/cli.py zpa application-segment delete --name {SEGMENT_NAME}
python scripts/cli.py zpa application-segment delete --id {SEGMENT_ID} --force
```
