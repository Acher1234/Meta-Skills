# Origin

Adapted from an earlier AI-skills Confluence skill that wraps
[confluence-cli](https://www.npmjs.com/package/confluence-cli) (npm).

Meta-Skills hybrid model: shared CLI under
`~/.meta-skills/skills/productivity/confluence`, per-workspace credentials via
`$CURRENT_SKILL_DIRECTORY` / `SkillCred("confluence", [".env"])`.

Python is only for resolving / loading `.env`; all Confluence work uses
`confluence-cli` directly after env is loaded.
