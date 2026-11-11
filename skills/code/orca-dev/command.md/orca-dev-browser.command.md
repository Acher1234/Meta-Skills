# orca-dev-browser — Commands

`ORCA` = resolved CLI (see `orca-dev` SKILL.md). Add `--json` everywhere; full
flags: `ORCA <command> --help`. Orca's **embedded** browser only (external browsers /
native apps: `orca-dev-computer.command.md`). Scope with `--worktree <sel>`; for
parallel work reuse `--page <browserPageId>` from `tab list`.

Loop: `tab create --url` / `goto --url` → `snapshot` (refs `@e1`…) → act → **re-snapshot**
(refs change after navigation).

| Group | Commands |
|-------|----------|
| Tabs | `tab create --url <u> [--profile <id>]` · `tab list` · `tab show --page <id>` · `tab current` · `tab switch --index\|--page` · `tab close` |
| Profiles | `tab profile list\|create\|delete\|set\|show\|use-default\|clone` |
| Navigate | `goto --url` · `back` · `forward` · `reload` · `wait [--timeout <ms>]` |
| Inspect | `snapshot` · `screenshot [--format png\|jpeg]` · `get --what text\|html\|value\|url\|title` · `is --what visible\|enabled\|checked` · `find --locator role\|text\|label --value <v>` · `eval --expression "<js>"` |
| Act | `click` · `dblclick` · `hover` · `focus` · `fill --value` · `clear` · `select --value` · `check` · `uncheck` · `drag --from --to` · `upload --files` · `scrollintoview` (all `--element <ref>`) |
| Keyboard / mouse | `type --input` · `inserttext` · `keypress --key` · `scroll --direction --amount` · `mouse move\|down\|up\|wheel` |
| Page settings | `set device --name` · `set offline --state` · `set headers` · `set credentials` · `set media` |
| Data | `clipboard read\|write` · `dialog accept\|dismiss` · `storage local\|session get\|set\|clear` · `download --selector --path` · `highlight` |
| Raw | `exec --command "<agent-browser command>"` |

Never type real credentials into pages unless the user gave them for that site.
