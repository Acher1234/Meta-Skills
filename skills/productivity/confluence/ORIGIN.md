# Origin

Adapted from an earlier AI-skills Confluence skill that wraps
[confluence-cli](https://www.npmjs.com/package/confluence-cli) (npm).

Meta-Skills hybrid model: shared CLI under
`~/.meta-skills/skills/productivity/confluence`, per-workspace credentials via
`$CURRENT_SKILL_DIRECTORY` / `scripts/skill_env.py` (`SkillEnv`).

Python is only for resolving / exporting `.env`; all Confluence work uses
`confluence-cli` directly after `eval "$(python scripts/skill_env.py)"`.
