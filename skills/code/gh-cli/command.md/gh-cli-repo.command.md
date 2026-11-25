# gh-cli-repo — Commands

`gh` 2.103.0. Flags not listed: `gh <command> --help`. Rules: `gh-cli` SKILL.md.
`<repo>` = `[HOST/]OWNER/REPO`; omitted → repo of the current directory.

## Read

| Command | Description |
|---------|-------------|
| `gh repo view [<repo>] [-b <branch>] [--json <fields>]` | Repo details / README |
| `gh repo list [<owner>] [-L <n>] [--visibility public\|private\|internal] [-l <lang>] [--topic <t>] [--fork\|--source] [--archived\|--no-archived] [--json <fields>]` | Repos of a user / org |
| `gh repo read-dir [<path>] [--ref <ref>] [--json <fields>]` | List a directory without cloning (preview) |
| `gh repo read-file <path> [--ref <ref>] [-o <file>] [--clobber]` | Read one file without cloning (preview) |
| `gh repo set-default [<repo>] [-v] [-u]` | Default repo of this directory (`-v` view, `-u` unset) |
| `gh org list [-L <n>]` | Organizations of the account |

Useful `repo view` fields: `nameWithOwner`, `description`, `url`, `sshUrl`,
`defaultBranchRef`, `visibility`, `isPrivate`, `isFork`, `parent`,
`stargazerCount`, `repositoryTopics`, `viewerPermission`, `latestRelease`.
`repo list` has no sort flag: sort with `--jq 'sort_by(.pushedAt)'`.
`repo read-dir --json name,type` returns an object: the list is under `.entries`.

## Create, clone, fork, sync

| Command | Description |
|---------|-------------|
| `gh repo clone <repo> [<dir>] [-- <git flags>]` | Clone (a fork also gets an `upstream` remote; `--no-upstream` to skip) |
| `gh repo create <name> --public\|--private\|--internal [-d <desc>] [--add-readme] [-g <gitignore>] [-l <license>] [-c]` | New repo on GitHub (`-c` clones it) |
| `gh repo create <name> --private -s . [-r <remote>] [--push]` | Publish an existing local repo |
| `gh repo create <name> -p <template-repo> [--include-all-branches] --private` | From a template |
| `gh repo fork [<repo>] [--clone] [--remote] [--org <org>] [--fork-name <n>] [--default-branch-only]` | Fork |
| `gh repo sync [<dest-repo>] [-s <source>] [-b <branch>] [--force]` | Update a fork / local branch from its parent (`--force` = hard reset, confirm first) |

`<name>` may be `OWNER/NAME`. Visibility is mandatory in non-interactive mode.

## Settings and lifecycle — confirm first

| Command | Description |
|---------|-------------|
| `gh repo edit [<repo>] [-d <desc>] [-h <url>] [--add-topic <t>] [--remove-topic <t>] [--default-branch <b>] [--enable-issues[=false]] [--enable-auto-merge] [--delete-branch-on-merge] …` | Settings (`--enable-*`, merge methods, security: see `--help`) |
| `gh repo edit --visibility public\|private\|internal --accept-visibility-change-consequences` | Change visibility |
| `gh repo rename [<new-name>] [-y]` | Rename |
| `gh repo archive [<repo>] [-y]` / `gh repo unarchive [<repo>] [-y]` | Archive / unarchive |
| `gh repo delete [<repo>] --yes` | Delete — irreversible, needs the `delete_repo` scope |

## Deploy keys, autolinks, templates

| Command | Description |
|---------|-------------|
| `gh repo deploy-key list` / `add <key-file> [-t <title>] [-w]` / `delete <key-id>` | Deploy keys (`-w` = write access) |
| `gh repo autolink list` / `view <id>` / `create <prefix> <url-template> [-n]` / `delete <id> [--yes]` | Autolink references (`TICKET-<num>` → URL) |
| `gh repo gitignore list` / `view <template>` | `.gitignore` templates |
| `gh repo license list` / `view <key\|spdx-id>` | License templates |
| `gh licenses` | Third-party licenses of `gh` itself |

## Rulesets (read-only)

| Command | Description |
|---------|-------------|
| `gh ruleset list [-o <org>] [-L <n>] [-p=false]` | Rulesets of the repo / org (`-p` includes inherited ones, default true) |
| `gh ruleset view [<id>] [-o <org>]` | One ruleset |
| `gh ruleset check [<branch>] [--default]` | Rules that apply to a branch |

Create / edit rulesets and branch protection through `gh api`
(`repos/{owner}/{repo}/rulesets`, `…/branches/<b>/protection`).

## Browse

| Command | Description |
|---------|-------------|
| `gh browse -n [<number> \| <path>[:<line>] \| <sha>] [-b <branch>] [-c[=<sha>]] [--blame]` | Print the GitHub URL (`-n`; without it a browser opens) |
| `gh browse -n -s` / `-a` / `-r` / `-w` / `-p` | URL of settings / actions / releases / wiki / projects |
