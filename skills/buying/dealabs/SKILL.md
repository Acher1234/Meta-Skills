---
name: dealabs
description: >-
  Dealabs REST v2 CLI — search deals, merchants, comments
  (OAuth1). Use when the user asks about Dealabs, bons plans, deal search,
  merchant filter, deal comments, or invokes /dealabs_*.
disable-model-invocation: true
---

### TO COPY

# dealabs

Per-workspace registration slice. No credentials.

## Working directory

Placeholders changed by `/meta-skills` at copy time (NAME => {PLACEHOLDER}):

IS_GLOBAL => {IS_GLOBAL}
TYPE_OF_AI_TOOLS => {TYPE_OF_AI_TOOLS}
SKILL_PATH => {SKILL_PATH}

```bash
export CURRENT_SKILL_DIRECTORY="{SKILL_PATH}"
```

##### END TO COPY

# dealabs

Dealabs **REST v2** CLI (`thread/search`, `thread`, `merchant`, `merchant/search`, comments). OAuth1 consumer is hardcoded in `scripts/dealabs.py`. No `.env`.

Library: `~/.meta-skills/skills/buying/dealabs/`. Python: `~/.meta-skills/.venv/bin/python`.

## When to use

Trigger phrases: "cherche un deal Dealabs", "bons plans", "deals Amazon", "commentaires Dealabs", `/dealabs_*`.

## dealabs-deals

Search / hot / new / list / get deals. Filter with `--merchant-id`.

Commands → `~/.meta-skills/skills/buying/dealabs/command.md/dealabs-deals.command.md`

## dealabs-merchants

Search / list / get merchants (`GET merchant`, `merchant/search`).

Commands → `~/.meta-skills/skills/buying/dealabs/command.md/dealabs-merchants.command.md`

## dealabs-thread-comments

List comments on a thread.

Commands → `~/.meta-skills/skills/buying/dealabs/command.md/dealabs-thread-comments.command.md`

## How to run

1. First run: `cd ~/.meta-skills/skills/buying/dealabs && ~/.meta-skills/install.sh pip init .`
2. Map `/dealabs_<…>` → `~/.meta-skills/.venv/bin/python scripts/cli.py …`; return JSON.

## Notes

- Confirm before posting or mutating data (this CLI is read-only).
- No credentials required.
- Unofficial mobile REST API — not a public documented product API.
