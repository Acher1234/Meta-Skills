# coolify-servers — Commands

Existing servers, their proxy, destinations (Docker networks) and SSH private keys.
Requires a connected context (`--context "$COOLIFY_CONTEXT"`). All commands support `--help`
and `--format json`. Buying servers from a cloud provider is out of scope for this skill.

## Servers

| Command | Description |
|---------|-------------|
| `coolify server list` | List servers |
| `coolify server get <uuid>` | Server details (`--resources` lists what is deployed on it) |
| `coolify server domains <uuid>` | Domains served by the server |
| `coolify server add <name> <ip> <private_key_uuid>` | Add a server (`-p` port, `-u` user, `--validate`, `--server-role deployment\|build\|both`) |
| `coolify server update <uuid>` | Update only the given flags (`--name`, `--ip`, `--port`, `--user`, `--private-key-uuid`, `--server-role`, `--concurrent-builds`, …) |
| `coolify server validate <uuid>` | Validate the SSH connection (`--install` installs missing prerequisites) |
| `coolify server remove <uuid>` | Remove a server (`-f` skips the prompt; never add `--delete-from-provider` unasked) |

## Proxy, cleanup, monitoring

| Command | Description |
|---------|-------------|
| `coolify server proxy get <server_uuid>` | Proxy settings |
| `coolify server proxy update <server_uuid>` | Update them (`--proxy-type`, `--redirect-enabled`, `--redirect-url`, `--generate-exact-labels`) |
| `coolify server proxy set-config <server_uuid>` | Save raw proxy configuration (`--configuration-file` or `--configuration`) |
| `coolify server proxy restart <server_uuid>` | Restart the proxy — interrupts traffic |
| `coolify server docker-cleanup get <server_uuid>` | Docker cleanup settings |
| `coolify server docker-cleanup update <server_uuid>` | Update them (`--frequency`, `--threshold`, `--delete-unused-volumes`, `--delete-unused-networks`, …) |
| `coolify server docker-cleanup run <server_uuid>` | Run a cleanup now |
| `coolify server docker-cleanup executions <server_uuid>` | Past cleanup executions |
| `coolify server sentinel get <server_uuid>` | Sentinel (metrics) settings |
| `coolify server sentinel update <server_uuid>` | Update them (`--json`) |
| `coolify server log-drains get <server_uuid>` | Log drain settings |
| `coolify server log-drains update <server_uuid>` | Update them (`--json`) |
| `coolify server cloudflare-tunnel get <server_uuid>` | Cloudflare tunnel state |
| `coolify server cloudflare-tunnel enable <server_uuid>` | Enable the tunnel flag |
| `coolify server cloudflare-tunnel disable <server_uuid>` | Disable the tunnel flag |
| `coolify server cloudflare-tunnel update <server_uuid>` | Set the state (`--enabled`, required) |

## Docker registries

| Command | Description |
|---------|-------------|
| `coolify server registry list <server_uuid>` | Registry logins of a server (token needs `read:sensitive`) |
| `coolify server registry login <server_uuid>…` | `docker login` on one or more servers (`--registry`, `-u`, `--password-stdin`) |
| `coolify server registry check <server_uuid> <registry>` | Check that the saved login still works |
| `coolify server registry logout <server_uuid> <registry>` | `docker logout` (`-f` skips the prompt) |

Pass the registry password on stdin, never as an argument:
`echo "$GHCR_TOKEN" | coolify server registry login <uuid> --registry ghcr.io -u <user> --password-stdin`

## Destinations

| Command | Description |
|---------|-------------|
| `coolify destination list` | Docker network destinations (`--server <uuid>` filters) |
| `coolify destination get <uuid>` | One destination |
| `coolify destination create` | Create one (`--server`, `--network` required; `--name`, `--type standalone\|swarm`) |
| `coolify destination update <uuid>` | Rename (`--name`) |
| `coolify destination delete <uuid>` | Delete an unused destination |
| `coolify server destinations list <server_uuid>` | Destinations of one server |
| `coolify server destinations create <server_uuid>` | Create one on that server (`--network` required; `--name`, `--type`) |

## Private keys

| Command | Description |
|---------|-------------|
| `coolify private-key list` | List SSH private keys |
| `coolify private-key get <uuid>` | One key |
| `coolify private-key add <name> <key_or_file>` | Add a key from content or a file path (`--description`) |
| `coolify private-key update <uuid>` | Update (`--private-key` required; `--name`, `--description`) |
| `coolify private-key remove <uuid>` | Remove a key |

---
