# ai-usage — providers reference

How `scripts/cli.py` finds each token, which endpoint it calls, what every field means, and what is
verified vs. assumed. Read only the section you need.

- [Commands and flags](#commands-and-flags)
- [Token lookup](#token-lookup)
- [Claude Code](#claude-code)
- [Codex](#codex)
- [OpenCode](#opencode) · [OpenCode Go](#opencode-go) · [Zen balance and Go extra usage](#zen-balance-and-go-extra-usage)
- [Local usage (logs)](#local-usage-logs)
- [Output fields](#output-fields)
- [Pitfalls](#pitfalls)
- [Verification status](#verification-status)
- [Security](#security)

## Commands and flags

| Subcommand | Shows |
|------------|-------|
| `claude` | Claude Code plan windows (5h session, weekly, per-model weekly) + local token usage |
| `codex` | ChatGPT plan windows for Codex (5h, weekly) + local token usage |
| `opencode` | Limits of each OpenCode login, OpenCode Go quota, local token/cost usage |
| `all` | The three above in one report |

| Flag | Effect |
|------|--------|
| `--text` | Human table (default: JSON on stdout) |
| `--extra` | Add extra usage: Claude credits / monthly cap / spend, Codex credits, OpenCode Zen balance (also what Go extra usage draws from), monthly limit, month spend, auto-reload, local Zen/Go spend |
| `--scope auto\|project\|global` | `auto` follows `$IS_GLOBAL`; `project` searches the project first; `global` only the computer |
| `--source auto\|tool\|hermes\|openclaw\|env` | Take the token from one origin only |
| `--no-remote` | Skip every API call (local logs only) |
| `--no-local` | Skip log scanning (limits only) |

```bash
python scripts/cli.py all --text                 # everything, readable
python scripts/cli.py opencode --extra --text    # + Zen balance / Go extra usage
python scripts/cli.py claude --source hermes     # use the Claude token stored by Hermes
```

The CLI is **read-only**: tokens are never refreshed or rewritten. An expired token is reported
(`OAuth token expired … run <tool> once`) — opening the tool refreshes it.

## Token lookup

Order, first usable match wins; `sources_found` in the output lists every match (never the secret):

1. **Tool files** — project `.<tool>/` first when the skill is registered in a project
   (`IS_GLOBAL=FALSE`, project = `$PROJECT_PATH`, else git root, else cwd), then the computer's.
   A global skill (`IS_GLOBAL=TRUE`) only reads the computer's.
2. **Hermes** — `$HERMES_HOME` (profile), then `.hermes/` (project if project scope, then `~`):
   `auth.json` and `.env`.
3. **OpenClaw** — `$OPENCLAW_STATE_DIR`, then `.openclaw/`: `agents/<id>/agent/auth-profiles.json`
   (agent `main` first) and `.env`.
4. **Process environment.**

For plan limits only OAuth / subscription tokens count: an API key (`sk-ant-api…`, `OPENAI_API_KEY`)
has no plan window and is skipped. Non-expired tokens are preferred over expired ones.

Optional skill `.env` (`$CURRENT_SKILL_DIRECTORY/.env`): `CLAUDE_CREDENTIALS_FILE`, `CODEX_AUTH_FILE`,
`OPENCODE_AUTH_FILE` force a file (checked first); `HTTP_*` / `PROXY_URL` as in `meta-skill-common/http`.

### Where each provider's token can live

| Provider | Tool files | Hermes | OpenClaw | Env |
|----------|-----------|--------|----------|-----|
| Claude | `.claude/.credentials.json` → `claudeAiOauth.accessToken` (`$CLAUDE_CONFIG_DIR` for `~`); macOS keychain `Claude Code-credentials` | `auth.json` `credential_pool.anthropic[].access_token`; `.env` `CLAUDE_CODE_OAUTH_TOKEN`, `ANTHROPIC_TOKEN`, `ANTHROPIC_API_KEY` (if OAuth) | profile `anthropic:*` (`access` / `token`) ; `.env` same keys | same keys |
| Codex | `.codex/auth.json` → `tokens.access_token`, `account_id` (`$CODEX_HOME` for `~`) | `auth.json` `providers.openai-codex.tokens`, `credential_pool.openai-codex[]` | profile `openai-codex:*` (`access`, `accountId`, `expires`) | — |
| OpenCode logins | `.opencode/auth.json`, `~/.local/share/opencode/auth.json` (`$XDG_DATA_HOME`), `~/.opencode/auth.json`, `~/.config/opencode/auth.json`; OpenCode 2 `opencode.db` table `credential` (`$OPENCODE_DB`) | — | — | — |
| OpenCode Go key | `opencode-go`, else `opencode` API-key login | `credential_pool.opencode-go[]`; `.env` `OPENCODE_GO_API_KEY`, `OPENCODE_API_KEY` | profile `opencode-go:*` / `opencode:*` (`key`); `.env` same keys | `OPENCODE_GO_API_KEY`, `OPENCODE_API_KEY` |
| Zen Console sign-in | `opencode` login of type `oauth` (`opencode auth login opencode`) with `metadata.accountID/orgID/server` | — | — | — |

Entries with Hermes `last_status: dead` are ignored.

## Claude Code

`GET https://api.anthropic.com/api/oauth/usage`
Headers: `Authorization: Bearer <accessToken>`, `anthropic-beta: oauth-2025-04-20`.

| Response key | Output window |
|--------------|---------------|
| `five_hour` `{utilization, resets_at}` | `session_5h` |
| `seven_day` | `week_7d` |
| `seven_day_opus` / `seven_day_sonnet` / `seven_day_oauth_apps` | `week_7d_opus` / … |
| `limits[]` `{group, percent, resets_at, scope.model.display_name, is_active}` | `<group>_<model>` (e.g. `weekly_Fable`, `active: false` when not enforced) |

Extra usage (`--extra`): `extra_usage` (`is_enabled`, `monthly_limit`, `used_credits`, `utilization`,
`currency`, `spend_limit_reached`, `disabled_reason`) + `spend.used` (`amount_minor` / 10^`exponent`).
There is **no monthly plan limit**: only the 5h and weekly windows; the monthly cap exists only for
extra-usage credits.

## Codex

`GET https://chatgpt.com/backend-api/wham/usage`
Headers: `Authorization: Bearer <access_token>`, `ChatGPT-Account-Id: <account_id>` (from `auth.json`,
else the `chatgpt_account_id` claim of the id/access JWT).

`rate_limit.primary_window` / `secondary_window` `{used_percent, limit_window_seconds, reset_at |
reset_after_seconds}` → `session_5h` (18 000 s), `week_7d` (604 800 s), else `<n>h` / `<n>d`.
Also `plan_type`, `allowed`, `limit_reached`. Extra usage (`--extra`): `credits`.

Offline fallback: Codex logs a `rate_limits` snapshot in every `token_count` event; the newest one is
returned as `last_logged_limits` (`as_of`, `stale` when older than 1 h).

## OpenCode

Each login (auth.json + `opencode.db`) is reported under `limits.<provider>`:

| Login | Limits |
|-------|--------|
| `anthropic` OAuth | Claude endpoint above |
| `openai` OAuth | Codex endpoint above (`accountId` or JWT claim) |
| `opencode-go`, `opencode` | see OpenCode Go / Zen below |
| API keys (`type: api`) | none — billed per token |
| other OAuth (e.g. `github-copilot`) | none — no public usage endpoint |

### OpenCode Go

`GET https://opencode.ai/zen/go/v1/usage` — `Authorization: Bearer <Go key>`, **explicit User-Agent**.

```json
{"usage": {
  "rolling": {"status": "ok",           "percent": 0,   "resetsAt": "2026-10-26T11:56:32.100Z"},
  "weekly":  {"status": "ok",           "percent": 0,   "resetsAt": "2026-11-02T00:00:00.000Z"},
  "monthly": {"status": "rate-limited", "percent": 100, "resetsAt": "2026-10-30T06:42:30.000Z"}}}
```

→ windows `rolling_5h`, `week`, `month` with `status`; `limit_reached` + `blocked_by` name the windows
that are not `ok`. Plan allowances (OpenCode docs): 5h = 20 % of the monthly dollar limit, week = 50 %,
month = 100 %.

Every found key is tried in order until one is accepted (a Zen `opencode` key may have no Go
subscription). If none works and a Console sign-in exists, the CLI falls back to the Console meters
(`GET <server>/api/go/status` → `access.meters.{fiveHour,week,month}.{limitMicroCents, usedMicroCents,
resetsAt}`, `access.endsAt`) and adds `used_usd` / `limit_usd` per window; `key_error` keeps the key
error. 404 = no Go subscription on that account.

Hermes records the last error per pooled key; it is shown as `hermes_last_status` (`last_status`
`exhausted`, `last_error_code` 429, `GoUsageLimitError`, `last_error_reset_at` in local time).

### Zen balance and Go extra usage

Zen is pay-as-you-go from a workspace balance. Go **Extra Usage** (toggle on the Go page) makes Go fall
back to that same balance when a Go window is blocked. So `--extra` reports the Zen balance for both.

There is **no API-key endpoint** for the balance ([opencode#10448](https://github.com/anomalyco/opencode/issues/10448),
open). It needs the **OpenCode Console sign-in** (`opencode auth login opencode`, OAuth, stored in
`opencode.db`). Base `metadata.server` or `https://opencode.ai/console`; headers
`Authorization: Bearer <access>`, `x-org-id: <orgID>`, `Accept: application/json`. Amounts are
micro-cents (1 USD = 100 000 000). Routes (as used by [opencode-quota](https://github.com/slkiser/opencode-quota)):

| Route | Field | Output |
|-------|-------|--------|
| `api/billing/status` | `balanceMicroCents` | `balance_usd` |
| `api/billing/account` | `creditLimitMicroCents` (null = no limit) | `monthly_limit_usd` |
| `api/billing/auto-recharge` | `enabled`, `rechargeAmountDollars`, `thresholdDollars` | `auto_reload` |
| `api/usage/cost-by-day` | `[{date, totalCostMicroCents}]`, current UTC month summed | `month_spent_usd` (+ `month_used_percent`, `month_remaining_usd`) |

Always added (no sign-in needed): `local_spend_this_month` — cost logged by OpenCode for `opencode/…`
(Zen) and `opencode-go/…` (Go) models. Without a sign-in, `zen_balance.error` explains how to sign in.
An expired session (redirect to an HTML login page or 401) asks to sign in again.

Not available: whether the Go Extra Usage toggle is on (no known route) and member budgets
(`api/policies/members/<accountID>`, not implemented).

## Local usage (logs)

| Tool | Logs | Dedupe / notes |
|------|------|----------------|
| Claude | `~/.claude/projects/**/*.jsonl` (`$CLAUDE_CONFIG_DIR`), assistant `message.usage` | by `message.id` + `requestId`; `<synthetic>` skipped |
| Codex | `~/.codex/sessions/**/*.jsonl`, `archived_sessions/` — `token_count.info.last_token_usage` | skipped when `total_token_usage` did not change; `input` excludes `cached_input_tokens` |
| OpenCode | `opencode.db` table `message` (`data` JSON) or legacy `storage/message/*/*.json` | assistant messages with `tokens`, `cost`, `providerID/modelID` |

Files older than 31 days are skipped. Project scope keeps only sessions whose cwd / root is inside
the project. Periods: `last_5h`, `today`, `last_7d`, `this_week` (Monday), `this_month` (1st, local
time), `last_30d`; plus `this_month_by_model`. `total` = input + output + cache read + cache write
(reasoning is part of output). `cost_usd` is only filled by OpenCode.

## Output fields

| Field | Meaning |
|-------|---------|
| `credentials`, `credentials_origin` | Source used (path + key, origin `tool` / `hermes` / `openclaw` / `env`) |
| `sources_found[]` | Every candidate `{origin, source, kind, expired?}` — no secret |
| `limits.windows[]` | `{window, used_percent, remaining_percent, resets_at (local), resets_in, status?, active?}` |
| `limits.error` | Why no live limits (no token, expired, HTTP status) |
| `extra_usage` | Only with `--extra` |
| `local_usage.periods.<period>` | `{messages, input, output, cache_read, cache_write, reasoning, total, cost_usd}` |

## Pitfalls

- `percent` / `used_percent` is **consumed**, not remaining.
- OpenCode Go: `rolling` at 0 % does not mean usable — a `monthly` at 100 % `rate-limited` blocks
  every call. Read `blocked_by`, not only the first window. Each window has its own reset.
- Reset times arrive in UTC; the CLI converts them to the local timezone (DST-aware).
- Cloudflare rejects urllib's default User-Agent on `opencode.ai` (HTTP 403, error 1010); the CLI
  always sends `ai-usage-skill/1.0`.
- Local logs count tokens actually used on this machine; they are not the plan quota.
- Claude's weekly window can be scoped to one model (`weekly_Fable`, `active: false`) and stay at 0 %.

## Verification status

| Part | Status |
|------|--------|
| Claude limits, extra usage, local logs | Verified live |
| Codex `wham/usage`, OpenCode Go key endpoint, Console routes | Request shape from upstream code / user doc; reachable (401 with fake tokens); parsing tested on sample responses; **not yet run with a real account** |
| Hermes / OpenClaw file formats | From their docs and Hermes source; tested with fixture files only |
| Project vs global lookup, log filters, dedupe | Tested with fixtures |

Endpoints are undocumented and may change; failures are reported per provider without hiding the
others.

## Security

- Never print, log or commit a token; outputs only show where a token was found.
- Hermes `.env` and OpenClaw `.env` hold many secrets: the CLI parses only the keys listed above and
  never `source`s the files.
- Keep `~/.hermes/.env` and credential files `chmod 600`. If a key leaks, rotate it at the provider.
