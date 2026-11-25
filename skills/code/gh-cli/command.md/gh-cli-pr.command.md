# gh-cli-pr — Commands

`gh` 2.103.0. Flags not listed: `gh <command> --help`. Rules: `gh-cli` SKILL.md.
`<pr>` = number, URL or branch; omitted → PR of the current branch. All accept `-R OWNER/REPO`.

## Read

| Command | Description |
|---------|-------------|
| `gh pr list [-s open\|closed\|merged\|all] [-B <base>] [-H <head>] [-A <author>] [-a <assignee>] [-l <label>] [-d] [-S "<search>"] [-L <n>] [--json <fields>]` | PRs of the repo |
| `gh pr view [<pr>] [-c] [--json <fields>]` | One PR (`-c` adds comments) |
| `gh pr status [-c] [--json <fields>]` | PRs relevant to me (current branch, mine, review requested) |
| `gh pr diff [<pr>] [--name-only] [--patch] [-e <glob>] [--color never]` | Diff (no `--stat`: use `--json additions,deletions,changedFiles`) |
| `gh pr checks [<pr>] [--required] [--watch [--fail-fast] [-i <sec>]] [--json <fields>]` | CI status; exit code 8 = still pending |
| `gh pr checkout <pr> [-b <local-branch>] [-f] [--detach] [--recurse-submodules] [--worktree <path>]` | Check out locally — alias `gh co` |

`pr view` fields: `number`, `title`, `body`, `state`, `isDraft`, `url`, `author`,
`headRefName`, `headRefOid`, `baseRefName`, `mergeable`, `mergeStateStatus`,
`reviewDecision`, `reviews`, `latestReviews`, `reviewRequests`, `statusCheckRollup`,
`comments`, `commits`, `files`, `additions`, `deletions`, `changedFiles`, `labels`,
`closingIssuesReferences`, `mergedAt`, `mergeCommit`, `isCrossRepository`.
`pr checks` fields: `name`, `state`, `bucket` (pass / fail / pending / skipping /
cancel), `link`, `workflow`.

## Create — confirm first

Before creating: branch pushed (`git push -u origin HEAD`) and ahead of the base
(`git log --oneline origin/<base>..HEAD`). "No commits between" / "Head sha can't
be blank" = wrong branch names or nothing pushed — inspect, do not retry.

| Command | Description |
|---------|-------------|
| `gh pr create -B <base> -H <head> -t "<title>" -F <body-file> [-d] [-r <reviewer>] [-a @me] [-l <label>] [-m <milestone>] [-p <project>]` | Open a PR (`-d` = draft) |
| `gh pr create -f` / `--fill-first` / `--fill-verbose` | Title and body from the commits |
| `gh pr create -H <user>:<branch> -R <upstream-repo> …` | PR from a fork |
| `gh pr create --dry-run …` | Print what would be created (may still push) |
| `gh pr revert <pr> [-t "<title>"] [-F <body-file>] [-d]` | Open a PR that reverts a merged PR |

`Fixes #123` / `Closes #123` in the body links and auto-closes the issue.
Always pass `-H`: it skips the "where to push / fork?" prompt.

## Update — confirm first

| Command | Description |
|---------|-------------|
| `gh pr edit [<pr>] [-t "<title>"] [-F <body-file>] [-B <base>] [--add-label\|--remove-label <l>] [--add-reviewer\|--remove-reviewer <login>] [--add-assignee\|--remove-assignee <login>] [-m <milestone>\|--remove-milestone] [--add-project\|--remove-project <title>]` | Edit metadata (`@me`, `@copilot` accepted as logins) |
| `gh pr ready [<pr>] [--undo]` | Draft → ready (`--undo` = back to draft) |
| `gh pr update-branch [<pr>] [--rebase]` | Bring the PR branch up to date with its base |
| `gh pr comment [<pr>] -F <body-file>` | Add a comment |
| `gh pr comment [<pr>] --edit-last [--create-if-none] -F <body-file>` / `--delete-last --yes` | Edit / delete my last comment |
| `gh pr review [<pr>] -a\|-r\|-c [-F <body-file>]` | Approve / request changes / comment (body required for `-r` and `-c`) |
| `gh pr lock <pr> [-r off_topic\|resolved\|spam\|too_heated]` / `gh pr unlock <pr>` | Lock / unlock the conversation |
| `gh pr close <pr> [-c "<comment>"] [-d]` / `gh pr reopen <pr> [-c "<comment>"]` | Close (`-d` deletes the branch) / reopen |

## Merge — confirm first

| Command | Description |
|---------|-------------|
| `gh pr merge [<pr>] -s\|-m\|-r [-d] [-t "<subject>"] [-F <body-file>]` | Squash / merge commit / rebase (`-d` deletes the branch). A strategy flag is mandatory without a prompt |
| `gh pr merge <pr> --auto -s` / `--disable-auto` | Auto-merge once requirements pass / cancel it |
| `gh pr merge <pr> --match-head-commit <sha> …` | Merge only if the head is still that commit |
| `gh pr merge <pr> --admin …` | Bypass requirements / merge queue — only on explicit request |

Merge queue on the base branch: no strategy flag; the PR is queued.

## Review comments on lines (`gh api`)

```bash
gh api repos/{owner}/{repo}/pulls/<n>/comments --paginate \
  --jq '.[] | {id, path, line, user: .user.login, body}'       # read inline comments
gh api repos/{owner}/{repo}/pulls/<n>/comments/<id>/replies -f body="<text>"   # reply in a thread
gh api repos/{owner}/{repo}/pulls/<n>/comments -f body="<text>" -f path=<file> \
  -F line=<n> -f side=RIGHT -f commit_id="$(gh pr view <n> --json headRefOid --jq .headRefOid)"
```

Reply in the existing thread rather than adding a top-level comment. A wrong
`path` / `line` / `commit_id` returns HTTP 422. Resolved state of threads:
GraphQL `reviewThreads` (`gh-cli-api.command.md`).

## Stacked PRs

A PR whose `baseRefName` is another feature branch is part of a stack. Stacks
are managed by the official extension, not by core `gh`:
`gh extension install github/gh-stack`, then `gh stack --help`. Do not
`gh pr merge` the middle of a stack.
