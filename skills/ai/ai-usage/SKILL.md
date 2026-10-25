---
name: ai-usage
description: >-
  Show how much of your AI coding plan is left — Claude Code, Codex and OpenCode:
  5h session / weekly limits used and remaining (with reset time) plus local token
  usage per period (5h, today, week, month, 30d). Reads each tool's own login token
  (project .claude/.codex/.opencode first, then the computer's). Use when the user
  asks about AI usage, quota, limits, "how much is left", or invokes /ai-usage_*.
disable-model-invocation: true
---

### TO COPY

# ai-usage

Per-workspace registration slice. Optional settings live in `{SKILL_PATH}/.env`.

## Working directory

Placeholders changed by `/meta-skills` at copy time (NAME => {PLACEHOLDER}):

IS_GLOBAL => {IS_GLOBAL}
TYPE_OF_AI_TOOLS => {TYPE_OF_AI_TOOLS}
SKILL_PATH => {SKILL_PATH}
PROJECT_PATH => {PROJECT_PATH}

Bash / zsh:

```bash
export CURRENT_SKILL_DIRECTORY="{SKILL_PATH}"
export IS_GLOBAL="{IS_GLOBAL}"
export PROJECT_PATH="{PROJECT_PATH}"
~/.meta-skills/.venv/bin/python ~/.meta-skills/skills/ai/ai-usage/scripts/cli.py all --text
```

PowerShell (Windows):

```powershell
$env:CURRENT_SKILL_DIRECTORY = "{SKILL_PATH}"
$env:IS_GLOBAL = "{IS_GLOBAL}"
$env:PROJECT_PATH = "{PROJECT_PATH}"
& "$HOME/.meta-skills/.venv/Scripts/python.exe" "$HOME/.meta-skills/skills/ai/ai-usage/scripts/cli.py" all --text
```

`IS_GLOBAL=FALSE` → tokens are searched in `PROJECT_PATH/.<tool>/` first, then in `~`.
`IS_GLOBAL=TRUE` → only the computer's (`~`) tool dirs.

##### END TO COPY

# ai-usage

One CLI, four subcommands: `claude`, `codex`, `opencode`, `all`. Each prints
(1) the **plan limits** — used % / remaining % / time to reset for the 5h session and weekly
windows, read live from the provider with the tool's own OAuth token, and (2) **local usage**
from the tool's session logs: messages, input / output / cache tokens and cost for
`last_5h`, `today`, `last_7d`, `this_week`, `this_month`, `last_30d` (+ per-model split this month).

Read-only: tokens are never refreshed or written; an expired token is reported — open the tool once.

## Prerequisites

```bash
cd ~/.meta-skills/skills/ai/ai-usage && ~/.meta-skills/install.sh pip init .
```

## Where tokens / logs are read

| Tool | Credentials (project first if `IS_GLOBAL=FALSE`) | Limits API | Local logs |
|------|------|------|------|
| claude | `<project>/.claude/.credentials.json` → `${CLAUDE_CONFIG_DIR:-~/.claude}/.credentials.json` → macOS keychain → `$CLAUDE_CODE_OAUTH_TOKEN` | `api.anthropic.com/api/oauth/usage` | `~/.claude/projects/**/*.jsonl` |
| codex | `<project>/.codex/auth.json` → `${CODEX_HOME:-~/.codex}/auth.json` | `chatgpt.com/backend-api/wham/usage` (+ last limits logged in sessions, offline) | `~/.codex/sessions/**/*.jsonl` |
| opencode | `<project>/.opencode/auth.json` → `~/.local/share/opencode/auth.json` → `~/.opencode/` → `~/.config/opencode/` | per provider: `anthropic` OAuth → Claude API, `openai` OAuth → Codex API; API keys have no window | `opencode.db` / `storage/message/` |

Project scope also filters local logs to sessions whose cwd is inside the project.
`.env` keys (all optional): `CLAUDE_CREDENTIALS_FILE`, `CODEX_AUTH_FILE`, `OPENCODE_AUTH_FILE`
force a file; `HTTP_*` / `PROXY_URL` as in `meta-skill-common/http`.

## Slash commands

| Slash | CLI | Description |
|-------|-----|-------------|
| `/ai-usage_claude` | `python scripts/cli.py claude` | Claude Code limits left + token usage |
| `/ai-usage_codex` | `python scripts/cli.py codex` | Codex limits left + token usage |
| `/ai-usage_opencode` | `python scripts/cli.py opencode` | OpenCode providers' limits + token/cost usage |
| `/ai-usage_all` | `python scripts/cli.py all` | All three |

Flags (every subcommand): `--text` (human table, default JSON), `--scope auto|project|global`
(override `IS_GLOBAL`), `--no-remote` (logs only), `--no-local` (limits only).

## Notes

- Answer with the remaining % and reset time first, then the period table.
- The limits APIs are undocumented endpoints used by the tools themselves; fields may change.
- Never print tokens; never commit `.env` or credential files.
