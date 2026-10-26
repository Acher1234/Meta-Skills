# Origin

First-party skill — no upstream skill tree. Reads the login files and session logs that
Claude Code, Codex CLI and OpenCode already write, and the usage endpoints those tools call.

- Claude Code: `GET https://api.anthropic.com/api/oauth/usage`
  (`Authorization: Bearer <claudeAiOauth.accessToken>`, `anthropic-beta: oauth-2025-04-20`);
  [Claude Code settings / credentials](https://docs.claude.com/en/docs/claude-code/settings)
- Codex CLI: `GET https://chatgpt.com/backend-api/wham/usage`
  (`Authorization: Bearer <tokens.access_token>`, `ChatGPT-Account-Id`);
  [openai/codex](https://github.com/openai/codex) (`auth.json`, rollout `token_count` events)
- OpenCode: [opencode.ai/docs](https://opencode.ai/docs/) — `auth.json` providers, message storage
- OpenCode Go: `GET https://opencode.ai/zen/go/v1/usage` (`Authorization: Bearer <key>`, explicit
  `User-Agent` — Cloudflare rejects urllib's default) → `usage.rolling|weekly|monthly` `{status, percent, resetsAt}`
- Hermes Agent: `~/.hermes/auth.json` (`credential_pool.<provider>[]`, `providers.openai-codex.tokens`),
  `~/.hermes/.env`; [hermes-agent providers](https://hermes-agent.nousresearch.com/docs/integrations/providers)
- OpenClaw: `~/.openclaw/agents/<id>/agent/auth-profiles.json` (`profiles.<provider>:<name>`);
  [OpenClaw OAuth](https://docs.openclaw.ai/concepts/oauth)

Endpoints are undocumented and read-only here; tokens are never refreshed or rewritten.
