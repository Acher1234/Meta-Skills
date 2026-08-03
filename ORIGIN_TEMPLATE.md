# Origin

<!-- Pick ONE pattern (vendored skill OR first-party API skill), then delete the other. -->

## Pattern A — vendored from another repo

Vendored (copied, not a git submodule) from:

[{ORG}/{REPO} — `{upstream/path}`](https://github.com/{ORG}/{REPO}/tree/{ref}/{upstream/path})

Upstream license: {LICENSE}. Re-copy from that path to refresh.

Adapted for Meta-Skills: shared CLI under
`~/.meta-skills/skills/{category}/…/{SKILL_NAME}`, per-workspace credentials via
`$CURRENT_SKILL_DIRECTORY` / `SkillCred`.

What was taken: {files / folders copied}.
Local additions (not upstream): {SKILL.md tweaks, .env.example, scripts/, …}.

## Pattern B — first-party / API docs (no upstream skill tree)

{Product} API — {short scope}.

- {Area}: [{doc title}]({docs URL})
- Auth: [{auth doc}]({auth URL})

Base URL: `{API_BASE_URL}`  
Auth: `{scheme}` (e.g. `Authorization: Bearer ${TOKEN_ENV}`)
