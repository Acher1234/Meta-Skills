---
name: dealabs
description: >-
  Dealabs hot deals, thread details, comments, and webhook monitoring via the
  dealabs CLI (dealabs-api). Use when the user mentions Dealabs, French deals,
  bons plans, hot threads, or invokes /dealabs_*.
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
cd ~/.meta-skills/skills/buying/dealabs
~/.meta-skills/install.sh pip init .
~/.meta-skills/.venv/bin/dealabs hots --limit 10 --days 7
```

##### END TO COPY

# dealabs

Browse [Dealabs](https://www.dealabs.com/) hot deals via the **`dealabs` CLI**
([dealabs-api](https://github.com/IDerr/dealabs-api/blob/master/README.md)).
No API key — public read endpoints only.

## Prerequisites

Install once in the shared venv:

```bash
cd ~/.meta-skills/skills/buying/dealabs
~/.meta-skills/install.sh pip init .
dealabs --help
```

`install.sh pip init` reads `requirements.txt` (installs from GitHub). Then call the CLI via the shared venv — **not** `python -m dealabs` (no `__main__`):

```bash
cd ~/.meta-skills/skills/buying/dealabs
~/.meta-skills/.venv/bin/dealabs hots --limit 10 --days 7
```

Equivalent: `~/.meta-skills/.venv/bin/python -m dealabs.cli hots --limit 10 --days 7`

Do **not** use system `/usr/local/bin/python3` unless `dealabs-api` is installed in that interpreter.

## When to use

Trigger phrases: "Dealabs hot deals", "bons plans Dealabs", "thread Dealabs",
"commentaires Dealabs", "surveiller Dealabs", `/dealabs_*`.

Confirm with the user before **`monitor`** (starts a webhook listener).

## Slash commands

| Slash | CLI | Description |
|-------|-----|-------------|
| `/dealabs_hots` | `~/.meta-skills/.venv/bin/dealabs hots [--page PAGE] [--limit LIMIT] [--days DAYS]` | Hot deals (`days`: 1, 7, or 30) |
| `/dealabs_get-thread` | `~/.meta-skills/.venv/bin/dealabs get-thread THREAD_ID [--json-output]` | Thread details (title, merchant, temperature, …) |
| `/dealabs_get-comments` | `~/.meta-skills/.venv/bin/dealabs get-comments THREAD_ID [--page PAGE] [--limit LIMIT] [--sort SORT] [--json-output]` | Thread comments |
| `/dealabs_monitor` | `~/.meta-skills/.venv/bin/dealabs monitor --webhook WEBHOOK_URL [--keywords KEYWORDS...] [--categories CATEGORIES...]` | Monitor new deals → webhook |

Prefer `--json-output` on `get-thread` and `get-comments` so the agent can parse structured output.

## How to run

1. `cd ~/.meta-skills/skills/buying/dealabs`.
2. First run: `~/.meta-skills/install.sh pip init .`
3. Map `/dealabs_<…>` → `~/.meta-skills/.venv/bin/dealabs …` (or `python -m dealabs.cli …`); use `--json-output` when available.

### Examples

```bash
~/.meta-skills/.venv/bin/dealabs hots --limit 10 --days 7
~/.meta-skills/.venv/bin/dealabs get-thread 3232541 --json-output
~/.meta-skills/.venv/bin/dealabs get-comments 3232541 --limit 20 --sort hot --json-output
~/.meta-skills/.venv/bin/dealabs monitor --webhook https://example.com/webhook --keywords gaming --categories "Video games"
```

## Notes

- Respect Dealabs terms of use; avoid aggressive polling.
- `monitor` is long-running — confirm webhook URL and filters with the user first.
- Upstream: [IDerr/dealabs-api](https://github.com/IDerr/dealabs-api).
