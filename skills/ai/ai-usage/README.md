# ai-usage

How much of your AI plan is left, for **Claude Code**, **Codex** and **OpenCode**.

```bash
~/.meta-skills/.venv/bin/python scripts/cli.py all --text
```

```
== claude ==
  credentials: ~/.claude/.credentials.json
  plan: team (default_claude_max_5x)
  session_5h               1.0% used ·  99.0% left · resets in 4h 54m
  weekly_Fable             0.0% used · 100.0% left · resets in 5d 11h 34m
  local usage (last activity 2026-10-25T13:25:19+00:00):
    period        msgs         input      output     cache read          total    cost $
    last_5h         22            44      26 686      1 692 029      1 800 735      0.00
    today          240           486     165 113     41 680 491     42 857 302      0.00
    …
```

Subcommands: `claude`, `codex`, `opencode` (incl. OpenCode Go quota), `all`. Flags: `--text`,
`--extra`, `--scope auto|project|global`, `--source auto|tool|hermes|openclaw|env`, `--no-remote`, `--no-local`.
Tokens come from the tool's own files, else Hermes / OpenClaw configs. Details and token lookup order: [`SKILL.md`](SKILL.md).
