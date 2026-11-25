# gh-cli-api — Commands

`gh` 2.103.0. Flags not listed: `gh api --help`, `gh help formatting`. Rules: `gh-cli` SKILL.md.

`gh api` = authenticated call to any GitHub REST or GraphQL endpoint. Use it
when no dedicated `gh` command exists. API reference: <https://docs.github.com/rest>.

## REST

| Command | Description |
|---------|-------------|
| `gh api <endpoint>` | `GET` (endpoint without leading `/`, e.g. `repos/{owner}/{repo}/topics`) |
| `gh api <endpoint> -f <key>=<string> -F <key>=<typed>` | Adding a field switches to `POST` |
| `gh api -X GET <endpoint> -f <key>=<value>` | Fields as query string |
| `gh api -X PATCH\|PUT\|DELETE <endpoint> …` | Other methods — confirm first |
| `gh api <endpoint> --input <file.json>` | Raw JSON body from a file (`-` = stdin) — use for nested / complex payloads |
| `gh api <endpoint> --paginate [--slurp]` | Follow all pages (`--slurp` wraps the pages in one array) |
| `gh api <endpoint> -q '<jq>'` / `-t '<go-template>'` | Filter / format the response |
| `gh api <endpoint> -H "<header>: <value>"` | Extra header |
| `gh api <endpoint> -i` / `--verbose` / `--silent` | Show status + headers / full exchange / no body |
| `gh api <endpoint> --cache 1h` | Cache the response |
| `gh api --hostname <host> <endpoint>` | GitHub Enterprise Server |

### Fields

- `-f key=value` → always a **string**.
- `-F key=value` → typed: `true` / `false` / `null` / integers become JSON
  values; `@<file>` reads the value from a file (`@-` = stdin); `{owner}`,
  `{repo}`, `{branch}` are filled in.
- A boolean or number sent with `-f` arrives as a string → HTTP 422.
- Nested: `-f 'key[subkey]=value'`; arrays: `-f 'key[]=a' -f 'key[]=b'`; empty array: `-f 'key[]'`.
- `{owner}`, `{repo}`, `{branch}` in the endpoint come from the current
  directory or `GH_REPO`. PowerShell: quote any argument containing `{…}`.

### Recipes

```bash
gh api repos/{owner}/{repo}/contents/<path> -H "Accept: application/vnd.github.raw"   # raw file
gh api repos/{owner}/{repo}/pulls/<n>/files --paginate --jq '.[] | {filename, status}'
gh api -X GET search/issues -f q='repo:OWNER/REPO is:pr is:open' --jq '.items[].number'
gh api rate_limit --jq '.resources | {core, search, graphql}'
gh api user --jq .login
```

`--paginate` + `--jq` runs the filter on each page; to aggregate across pages
use `--paginate --slurp` and pipe to an external `jq`.

## GraphQL

```bash
gh api graphql -F owner='{owner}' -F name='{repo}' -F number=<n> -f query='
  query($owner: String!, $name: String!, $number: Int!) {
    repository(owner: $owner, name: $name) {
      pullRequest(number: $number) {
        reviewThreads(first: 50) { nodes { id isResolved comments(first: 1) { nodes { path body } } } }
      }
    }
  }' --jq '.data.repository.pullRequest.reviewThreads.nodes'
```

- Every field other than `query` / `operationName` is a GraphQL variable; use
  `-F` for `Int` / `Boolean` variables, `-f` for strings.
- Pagination: `--paginate` needs an `$endCursor: String` variable and
  `pageInfo { hasNextPage endCursor }` in the query.
- Errors come back with HTTP 200 in `.errors` — check them.
- Put long queries in a file: `-F query=@<file.graphql>`.

## Output formatting (all `gh` commands)

| Flag | Description |
|------|-------------|
| `--json <f1,f2>` | JSON with those fields; `--json` alone lists the valid field names |
| `-q` / `--jq '<expr>'` | Built-in jq filter (no `jq` binary needed); requires `--json` (except on `gh api`) |
| `-t` / `--template '<tpl>'` | Go template; requires `--json` (except on `gh api`) |
| `--format json` | Used instead of `--json` by `gh project`, `gh release verify`, `gh attestation verify` |

```bash
gh pr list --json number,title,author --jq '.[] | "\(.number)\t\(.author.login)\t\(.title)"'
gh pr list --json number,labels --jq 'map(select(any(.labels[]; .name == "bug"))) | map(.number)'
gh issue list --json number,title,updatedAt \
  --template '{{range .}}{{tablerow .number .title (timeago .updatedAt)}}{{end}}{{tablerender}}'
```

Template helpers: `tablerow`, `tablerender`, `timeago`, `timefmt`, `truncate`,
`join`, `pluck`, `color`, `autocolor`, `hyperlink`, `contains`, `hasPrefix`,
`hasSuffix`, `regexMatch`. jq string output is raw (no quotes) — good for piping.
PowerShell: wrap jq / template expressions in single quotes.

## Errors

| Status | Meaning | Do |
|--------|---------|----|
| 401 | Bad / expired token | `gh auth status`; the user logs in again |
| 403 | Missing scope, no permission, or rate limit | Read the message; scope → user runs `gh auth refresh -s <scope>`; rate limit → `gh api rate_limit` |
| 404 | Wrong path **or** no access to a private resource | Check owner / repo / id and the account in use |
| 422 | Invalid payload | Check field types (`-f` vs `-F`) and required fields |
