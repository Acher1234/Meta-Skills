# gh-cli-search — Commands

`gh` 2.103.0. Flags not listed: `gh <command> --help`. Rules: `gh-cli` SKILL.md.

Search across **all of GitHub** (not only the current repo). Narrow with
`-R OWNER/REPO` or `--owner <login>` (both repeatable). Every command takes
`-L <n>` (default 30), `--json <fields>`, `--jq`, and `--sort` / `--order asc|desc`.

| Command | Description |
|---------|-------------|
| `gh search repos [<query>] [--owner <o>] [--language <l>] [--topic <t>] [--stars "<range>"] [--forks "<range>"] [--license <l>] [--visibility public\|private\|internal] [--archived[=false]] [--include-forks false\|true\|only] [--match name\|description\|readme] [--created\|--updated "<date>"] [--sort stars\|forks\|updated\|help-wanted-issues]` | Repositories |
| `gh search issues [<query>] [-R <repo>] [--state open\|closed] [--assignee\|--author\|--mentions\|--commenter\|--involves <user>] [--label <l>] [--milestone <t>] [--no-assignee\|--no-label\|--no-milestone\|--no-project] [--match title\|body\|comments] [--created\|--updated\|--closed "<date>"] [--comments\|--reactions\|--interactions "<range>"] [--include-prs] [--search-type lexical\|semantic\|hybrid] [--sort created\|updated\|comments\|reactions\|interactions]` | Issues |
| `gh search prs [<query>] [-R <repo>] [--state open\|closed] [--merged] [--merged-at "<date>"] [--draft] [-B <base>] [-H <head>] [--review none\|required\|approved\|changes_requested] [--review-requested\|--reviewed-by <user>] [--checks pending\|success\|failure]` + the issue filters above | Pull requests |
| `gh search code <query> [-R <repo>] [--owner <o>] [--language <l>] [--filename <f>] [--extension <ext>] [--match file\|path] [--size "<range>"]` | Code (query required; no `--sort`) |
| `gh search commits [<query>] [-R <repo>] [--author\|--committer <user>] [--author-email\|--committer-email <e>] [--author-date\|--committer-date "<date>"] [--hash <sha>] [--parent <sha>] [--tree <sha>] [--merge] [--sort author-date\|committer-date]` | Commits |

## Values

- **Ranges** (numbers and dates): `">100"`, `"<=5"`, `"10..50"`, `">2026-01-01"`,
  `"2026-01-01..2026-06-30"` — quote them.
- **Users**: `@me` works for `--assignee`, `--author`, `--review-requested`, …
- **Merged PRs**: `--merged` (there is no `--state merged` here; `gh pr list -s merged` is repo-scoped).
- **Excluding a qualifier** (`-label:bug`): put the query after `--`.
  Bash: `gh search issues -- "crash -label:bug"`.
  PowerShell: `gh --% search issues -- "crash -label:bug"`.
- Raw GitHub search qualifiers are accepted inside `<query>` (`"org:my-org is:open sort:updated"`).

## JSON fields

| Command | Main fields |
|---------|-------------|
| `repos` | `fullName`, `description`, `url`, `stargazersCount`, `forksCount`, `language`, `license`, `visibility`, `isArchived`, `pushedAt`, `updatedAt` |
| `issues` / `prs` | `number`, `title`, `state`, `url`, `repository`, `author`, `assignees`, `labels`, `commentsCount`, `createdAt`, `updatedAt`, `closedAt`, `isPullRequest`, `isDraft` (no `mergedAt`: use `gh pr view`) |
| `code` | `repository`, `path`, `sha`, `url`, `textMatches` |
| `commits` | `sha`, `commit`, `author`, `committer`, `repository`, `url` |

Field names differ from `gh repo view` (`stargazersCount` here, `stargazerCount`
there): list them with `gh search <type> --json`.

## Limits

- Results are capped at 1000 per query; code search is rate-limited harder
  (about 10 requests / minute) — narrow the query rather than paging.
- Code search covers default branches only and needs a logged-in account.
- Inside one repo, `gh issue list -S "<query>"` / `gh pr list -S "<query>"`
  return richer fields.

## Status

| Command | Description |
|---------|-------------|
| `gh status [-o <org>] [-e <owner/repo>,…]` | My assigned issues and PRs, review requests, mentions and repo activity across all repos (text only, no `--json`) |
