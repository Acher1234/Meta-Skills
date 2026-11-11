# orca-dev-computer — Commands

`ORCA` = resolved CLI (see `orca-dev` SKILL.md). Add `--json` everywhere; full
flags: `ORCA <command> --help`. Last resort: only when a visible window needs GUI
control that shell / files / APIs / the embedded browser cannot do.
Guides: `ORCA skills get computer-use`, `orca-emulator`, `orca-emulator-android`.

## Computer use (native apps, external browsers)

| Command | Description |
|---------|-------------|
| `ORCA computer capabilities` / `permissions` | Provider support / permission setup |
| `ORCA computer list-apps` / `list-windows` | Targets |
| `ORCA computer get-app-state` | Accessibility snapshot |
| `ORCA computer click` / `scroll` / `drag` / `perform-secondary-action` | Pointer actions |
| `ORCA computer type-text` / `paste-text` / `press-key` / `hotkey` / `set-value` | Keyboard / values |

## iOS simulator — `ORCA emulator <cmd>`

| Command | Description |
|---------|-------------|
| `list` · `attach <device>` · `kill` | Devices / helper |
| `tap <x> <y>` (0..1) · `gesture <json>` · `type <text>` | Input |
| `button <name>` · `rotate <orientation>` · `exec --command "<serve-sim cmd>"` | Hardware / raw |
