# TODO

## SKILL.md token budget (CI + pre-commit)

Add automated checks so every `SKILL.md` stays under a token limit.

### Scope

- Scan all `**/*.md` in the repo (root installer + `skills/**`).
- Fail if estimated tokens exceed the configured limit.
- Optional: different limits per file type (e.g. root `SKILL.md` vs registered slice `### TO COPY` only).

### Suggested limits (to tune)

| File | Max tokens (estimate) |
|------|------------------------|
| Root `SKILL.md` (meta-skills installer) | 2500 |
| Standard skill library `SKILL.md` | 2000 |
| `### TO COPY` slice only | 500 |

