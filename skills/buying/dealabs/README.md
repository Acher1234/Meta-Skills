# dealabs

Dealabs hot-deals CLI skill for Meta-Skills.

```bash
cd ~/.meta-skills/skills/buying/dealabs
~/.meta-skills/install.sh pip init .
~/.meta-skills/.venv/bin/dealabs hots --limit 10 --days 7
~/.meta-skills/.venv/bin/dealabs get-thread 3232541 --json-output
```

Do not use `python -m dealabs` — use `~/.meta-skills/.venv/bin/dealabs` or `python -m dealabs.cli`.

Upstream: [dealabs-api](https://github.com/IDerr/dealabs-api).
