# Origin

YouTrack via **yt-cli** ([youtrack-cli](https://pypi.org/project/youtrack-cli/) · [docs](https://yt-cli.readthedocs.io/en/stable/) · [ryancheley/yt-cli](https://github.com/ryancheley/yt-cli)).

Meta-Skills hybrid model: shared CLI under
`~/.meta-skills/skills/productivity/youtrack`, per-workspace credentials via
`$CURRENT_SKILL_DIRECTORY` / `scripts/skill_env.py` (`SkillEnv`).

Python is only for resolving / exporting `.env` (`URL`, `API_TOKEN`); all YouTrack
work uses `yt` after `eval "$(python scripts/skill_env.py)"` and
`yt auth login --base-url "$URL" --token "$API_TOKEN"`.

- Auth tokens: [Manage Permanent Tokens](https://www.jetbrains.com/help/youtrack/cloud/manage-permanent-token.html)
- REST API: [YouTrack REST API](https://www.jetbrains.com/help/youtrack/devportal/youtrack-rest-api.html)
