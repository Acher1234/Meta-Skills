---
name: ai-usage
description: >-
  Show how much of your AI coding plan is left — Claude Code, Codex and OpenCode:
  5h session / weekly limits used and remaining (with reset time) plus local token
  usage per period (5h, today, week, month, 30d), OpenCode Go quota and optional extra
  usage. Reads the tool's own login token (project first, then the computer's), else
  Hermes / OpenClaw configs. Use when the user
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

```powershell
cd "$HOME/.meta-skills/skills/ai/ai-usage"; & "$HOME/.meta-skills/install.ps1" pip init .
```

## Where tokens / logs are read

Token order: **tool files** (project `.<tool>/` first if `IS_GLOBAL=FALSE`) → **Hermes**
(`$HERMES_HOME`, `~/.hermes`: `auth.json` + `.env`) → **OpenClaw** (`$OPENCLAW_STATE_DIR`, `~/.openclaw`:
`agents/*/agent/auth-profiles.json` + `.env`) → **process env**. `sources_found` lists every match (no secret).

| Tool | Tool files | Hermes / OpenClaw / env | Limits API |
|------|------|------|------|
| claude | `.claude/.credentials.json`, macOS keychain | pool `anthropic`; profile `anthropic:*`; `CLAUDE_CODE_OAUTH_TOKEN`, `ANTHROPIC_TOKEN` | `api.anthropic.com/api/oauth/usage` |
| codex | `.codex/auth.json` | `providers.openai-codex.tokens`, pool `openai-codex`; profile `openai-codex:*` | `chatgpt.com/backend-api/wham/usage` |
| opencode | `auth.json`, OpenCode 2 `opencode.db` (`credential` table) | `anthropic` / `openai` OAuth entries → APIs above | per provider |
| opencode-go | `opencode-go` / `opencode` key | pool `opencode-go` (+ last 429 status); profile `opencode*`; `OPENCODE_GO_API_KEY`, `OPENCODE_API_KEY` | `opencode.ai/zen/go/v1/usage` (rolling 5h / week / month), else Console `go/status` |
| zen (`--extra`) | `opencode` **Console sign-in** (OAuth, `opencode auth login opencode`) | — (no API-key route, opencode#10448) | Console `api/billing/status`, `billing/account`, `billing/auto-recharge`, `usage/cost-by-day` |

Local logs: `~/.claude/projects/**/*.jsonl`, `~/.codex/sessions/**/*.jsonl`, OpenCode `opencode.db` /
`storage/message/`; project scope keeps only sessions whose cwd is in the project.
`.env` keys (optional): `CLAUDE_CREDENTIALS_FILE`, `CODEX_AUTH_FILE`, `OPENCODE_AUTH_FILE`, `HTTP_*`, `PROXY_URL`.

## Slash commands

| Slash | CLI | Description |
|-------|-----|-------------|
| `/ai-usage_claude` | `python scripts/cli.py claude` | Claude Code limits left + token usage |
| `/ai-usage_codex` | `python scripts/cli.py codex` | Codex limits left + token usage |
| `/ai-usage_opencode` | `python scripts/cli.py opencode` | OpenCode providers' limits, OpenCode Go quota + token/cost usage |
| `/ai-usage_all` | `python scripts/cli.py all` | All three |

Flags (every subcommand): `--text` (human table, default JSON), `--scope auto|project|global`
(override `IS_GLOBAL`), `--source auto|tool|hermes|openclaw|env` (one token origin only),
`--extra` (extra usage: Claude credits / monthly cap / spend, Codex credits, OpenCode Zen balance —
also what Go Extra Usage draws from — monthly limit, month spend, auto-reload, local Zen/Go spend),
`--no-remote` (logs only), `--no-local` (limits only).

## Notes

- Answer with the remaining % and reset time first, then the period table.
- `used_percent` is consumed, not left. OpenCode Go: check every window — `blocked_by` names the
  one that is rate-limited even when `rolling_5h` is at 0 %.
- The limits APIs are undocumented endpoints used by the tools themselves; fields may change.
- Never print tokens; never commit `.env` or credential files.
