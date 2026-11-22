# gh-cli-issue — Commands

`gh` 2.103.0. Flags not listed: `gh <command> --help`. Rules: `gh-cli` SKILL.md.
`<issue>` = number or URL. All accept `-R OWNER/REPO`.

## Read

| Command | Description |
|---------|-------------|
| `gh issue list [-s open\|closed\|all] [-l <label>] [-a <assignee>] [-A <author>] [-m <milestone>] [--type <name>] [--mention <user>] [-S "<search>"] [-L <n>] [--json <fields>]` | Issues of the repo |
| `gh issue view <issue> [-c] [--json <fields>]` | One issue (`-c` adds comments) |
| `gh issue status [--json <fields>]` | Issues assigned to me / mentioning me / opened by me |
| `gh issue develop <issue> -l` | Branches linked to the issue |

`issue view` fields: `number`, `title`, `body`, `state`, `stateReason`, `url`,
`author`, `assignees`, `labels`, `milestone`, `issueType`, `comments`, `parent`,
`subIssues`, `blockedBy`, `blocking`, `closedByPullRequestsReferences`, `isPinned`.

## Create and edit — confirm first

| Command | Description |
|---------|-------------|
| `gh issue create -t "<title>" -F <body-file> [-l <label>] [-a @me] [-m <milestone>] [-p <project>] [--type <name>] [-T <template>] [--parent <issue>] [--blocked-by <issues>] [--blocking <issues>] [--attach <file>]` | New issue (title **and** body required without a prompt) |
| `gh issue edit <issues…> [-t "<title>"] [-F <body-file>] [--add-label\|--remove-label <l>] [--add-assignee\|--remove-assignee <login>] [-m <milestone>\|--remove-milestone] [--type <name>\|--remove-type] [--add-project\|--remove-project <title>]` | Edit one or several issues |
| `gh issue edit <issue> --parent <issue>\|--remove-parent` / `--add-sub-issue\|--remove-sub-issue <issue>` | Parent / sub-issue links |
| `gh issue edit <issue> --add-blocked-by\|--remove-blocked-by <issue>` / `--add-blocking\|--remove-blocking <issue>` | Dependency links |
| `gh issue comment <issue> -F <body-file> [--attach <file>]` | Add a comment |
| `gh issue comment <issue> --edit-last [--create-if-none] -F <body-file>` / `--delete-last --yes` | Edit / delete my last comment |
| `gh issue develop <issue> [-n <branch>] [-b <base>] [-c] [--worktree <path>]` | Create a branch linked to the issue (`-c` checks it out) |

Logins accept `@me` and `@copilot` (assign to Copilot).

## State and lifecycle — confirm first

| Command | Description |
|---------|-------------|
| `gh issue close <issue> [-r completed\|"not planned"\|duplicate] [--duplicate-of <issue>] [-c "<comment>"]` | Close |
| `gh issue reopen <issue> [-c "<comment>"]` | Reopen |
| `gh issue pin <issue>` / `gh issue unpin <issue>` | Pin / unpin |
| `gh issue lock <issue> [-r off_topic\|resolved\|spam\|too_heated]` / `gh issue unlock <issue>` | Lock / unlock the conversation |
| `gh issue transfer <issue> <dest-repo>` | Move to another repo |
| `gh issue delete <issue> --yes` | Delete — irreversible |

## Issue artifacts (preview)

Documents, links and files attached to an issue. `<artifact>` = `<issue> <artifact-number>` or URL.

| Command | Description |
|---------|-------------|
| `gh issue artifact list <issue> [--type generic\|plan\|link\|embedded_html] [--json <fields>]` | Artifacts of an issue |
| `gh issue artifact view <artifact> [--version <n>] [--json <fields>]` | One artifact |
| `gh issue artifact download <issue> [<numbers…>] [-D <dir>] [-O <file>] [--clobber\|--skip-existing]` | Download |
| `gh issue artifact create <issue> [<file>[#<name>] \| <url>]… [-F <body-file> --name <name> --type generic\|plan\|embedded_html]` | Create — confirm first |
| `gh issue artifact edit <artifact> [-F <body-file>] [--name <name>] [--restore-version <n>]` | Edit — confirm first |
| `gh issue artifact delete <artifact> --yes` | Delete — confirm first |

## Labels

| Command | Description |
|---------|-------------|
| `gh label list [-S "<search>"] [--sort created\|name] [-L <n>] [--json <fields>]` | Labels of the repo |
| `gh label create <name> [-c <hex-color>] [-d "<desc>"] [-f]` | Create (`-f` updates if it exists) |
| `gh label edit <name> [-n <new-name>] [-c <hex-color>] [-d "<desc>"]` | Edit |
| `gh label clone <source-repo> [-f]` | Copy all labels from another repo |
| `gh label delete <name> --yes` | Delete — confirm first |

## Discussions (preview)

`<discussion>` = number or URL; comments are addressed by comment id or URL.

| Command | Description |
|---------|-------------|
| `gh discussion list [-s open\|closed\|all] [-c <category>] [-A <author>] [-l <label>] [--answered] [-S "<search>"] [--sort created\|updated] [-L <n>] [--after <cursor>] [--json <fields>]` | Discussions of the repo |
| `gh discussion view <discussion> [-c] [-L <n>] [--order oldest\|newest] [--json <fields>]` | One discussion (`-c` adds comments) |
| `gh discussion create -t "<title>" -F <body-file> -c <category> [-l <label>]` | New discussion — confirm first |
| `gh discussion edit <discussion> [-t "<title>"] [-F <body-file>] [-c <category>] [--add-label\|--remove-label <l>]` | Edit — confirm first |
| `gh discussion comment <discussion\|comment> -F <body-file>` | Comment, or reply to a comment — confirm first |
| `gh discussion comment <comment> --edit -F <body-file>` / `--delete --yes` | Edit / delete a comment — confirm first |

Mark an answer, close or lock a discussion: GraphQL through `gh api`.

## Bulk pattern

```bash
gh issue list -l stale --json number --jq '.[].number' |
  xargs -I{} gh issue close {} -r "not planned" -c "Closing as stale"
```

Show the list to the user and get confirmation before the write half.
