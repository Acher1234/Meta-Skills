# coolify-context — Commands

Contexts are saved instances (URL + token) in the per-user CLI config. This skill's context is
created by the connect block of `SKILL.md`; pass it to every command: `coolify --context "$COOLIFY_CONTEXT" …`.
All commands support `--help` and `--format json`.

| Command | Description |
|---------|-------------|
| `coolify context list` | List contexts (name, `fqdn`, default) — tokens are never printed |
| `coolify context get <name>` | One context |
| `coolify context verify` | Check connection and authentication of the context |
| `coolify context version` | Coolify version of the instance (check before version-gated flags) |
| `coolify context add <name> <url> <token>` | Add a context; no-op when the name exists (`-f` replaces the token only, `-d` makes it default — do not use `-d`) |
| `coolify context update <name>` | Change a context (`--url`, `--token`, `--name`) |
| `coolify context set-token <name> <token>` | Replace the token |
| `coolify context delete <name>` | Delete a context — confirm first |
| `coolify context use <name>` | **Do not use** — changes the user's default context |
| `coolify context set-default <name>` | **Do not use** — same as `use` |
| `coolify config` | Path of the CLI config file |
| `coolify version` | CLI version |
| `coolify completion <shell>` | Completion script (`bash`, `zsh`, `fish`, `powershell`) |
| `coolify update` | Self-update the CLI — only when the user asks |

---
