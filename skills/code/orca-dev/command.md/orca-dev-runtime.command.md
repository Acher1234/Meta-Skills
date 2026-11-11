# orca-dev-runtime — Commands

`ORCA` = resolved CLI (see `orca-dev` SKILL.md). Add `--json` everywhere; full
flags: `ORCA <command> --help`.

| Command | Description |
|---------|-------------|
| `ORCA open` | Launch Orca and wait for the runtime |
| `ORCA serve [--port <p>] [--pairing-address <host>] [--no-pairing] …` | Headless runtime server |
| `ORCA status` | App / runtime readiness |
| `ORCA diagnostics memory` | Memory snapshot |
| `ORCA agent-context` | Machine-readable command schema |
| `ORCA host list` | Targetable machines (`--host` values) |
| `ORCA environment add --name <n> --pairing-code <code>` · `list` · `show` · `rm` | Saved remote runtimes |
| `ORCA account add [--agent claude\|codex]` · `list` · `select` · `rm` | Managed agent accounts |
| `ORCA skills list` · `get <name>` · `installed` · `install` · `update` · `share` | Version-matched guides |
| `ORCA vm recipe doctor` | Validate a per-workspace environment recipe |

Remote runtime on any command: `--environment <name>` or `--pairing-code <code>`
(env: `ORCA_ENVIRONMENT`, `ORCA_PAIRING_CODE`). Handles from a remote server only
work against that server.
