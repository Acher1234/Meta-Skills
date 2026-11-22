# Origin

First-party skill written from the GitHub CLI's own help. Nothing is vendored.

- Reference: `gh help reference`, `gh help environment`, `gh help formatting`,
  `gh help exit-codes`
- Manual: [cli.github.com/manual](https://cli.github.com/manual)
- Source: [cli/cli](https://github.com/cli/cli)

**Compatible version: `gh` 2.103.0 (2026-10-21).** To refresh the skill, re-read
`gh help reference` on the new version, update the command files, then change
the version here and in `SKILL.md`.

Auth: handled by `gh` itself (`gh auth login`, credential store) — no `.env`.

## Inspiration

Structure and pitfalls were informed by these skills; no text was copied.

- [carapace-sh/carapace-bin — `skills/gh`](https://github.com/carapace-sh/carapace-bin/tree/master/skills/gh)
  (MIT): one reference file per domain, keyword router.
- [zeke/faster-gh-cli-skill](https://github.com/zeke/faster-gh-cli-skill) (MIT):
  agent pitfalls (JSON field names, Markdown quoting, explicit `--repo`).
- [holon-run/holon — `skills/ghx`](https://github.com/holon-run/holon/tree/main/skills/ghx)
  (Apache-2.0): long bodies through `--body-file`.
