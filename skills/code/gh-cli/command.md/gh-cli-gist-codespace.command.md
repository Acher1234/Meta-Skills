# gh-cli-gist-codespace — Commands

`gh` 2.103.0. Flags not listed: `gh <command> --help`. Rules: `gh-cli` SKILL.md.

## Gists

`<gist>` = id or URL.

| Command | Description |
|---------|-------------|
| `gh gist list [-L <n>] [--public\|--secret] [--filter "<regex>" [--include-content]]` | My gists (default 10; text only, no `--json`) |
| `gh gist view <gist> [-f <filename>] [--files] [-r]` | Content (`-r` raw, `--files` = file names only) |
| `gh gist clone <gist> [<dir>]` | Clone as a git repo |
| `gh gist create <files…> [-d "<desc>"] [-p]` | New gist from files — confirm first |
| `gh gist create - -f <filename> [-d "<desc>"] < <file>` | New gist from stdin |
| `gh gist edit <gist> -f <filename> <local-file>` | Replace one file with a local file |
| `gh gist edit <gist> -a <new-file>` / `-r <filename>` / `-d "<desc>"` | Add a file / remove a file / change description |
| `gh gist rename <gist> <old-filename> <new-filename>` | Rename a file |
| `gh gist delete <gist> --yes` | Delete — confirm first |

A gist is **secret by default** (unlisted, but readable by anyone with the
URL); `-p` makes it public. There is no `--private` flag. Never put
credentials in a gist. `gh gist edit` without `<local-file>`, `-a`, `-r` or
`-d` opens an editor. JSON for gists: `gh api gists`.

## Codespaces

Needs the `codespace` token scope. Alias `gh cs`. Select a codespace with
`-c <name>` (names from `gh codespace list`); without it `gh` opens a picker.

| Command | Description |
|---------|-------------|
| `gh codespace list [-R <repo>] [-L <n>] [--json <fields>]` | My codespaces (`name`, `state`, `repository`, `gitStatus`, `machineName`, …) |
| `gh codespace view -c <name> [--json <fields>]` | Details of one codespace |
| `gh codespace create -R <repo> [-b <branch>] [-m <machine>] [-l <location>] [-d "<display-name>"] [--idle-timeout 30m] [--retention-period 72h] [--devcontainer-path <path>] [--default-permissions] [-s]` | Create — billed, confirm first |
| `gh codespace ssh -c <name> [-- <ssh-flags>] [<command>]` | Run a command (or open a shell) in the codespace |
| `gh codespace ssh -c <name> --config` | Print an OpenSSH config block for it |
| `gh codespace cp [-r] [-e] -c <name> <sources…> <dest>` | Copy files; prefix remote paths with `remote:` (`-e` expands remote globs) |
| `gh codespace logs -c <name> [-f]` | Creation / startup logs |
| `gh codespace ports -c <name> [--json <fields>]` | Forwarded ports |
| `gh codespace ports forward <remote>:<local>… -c <name>` | Forward ports to localhost (blocks) |
| `gh codespace ports visibility <port>:public\|private\|org… -c <name>` | Change port visibility — confirm first |
| `gh codespace edit -c <name> [-d "<display-name>"] [-m <machine>]` | Rename / change machine type |
| `gh codespace rebuild -c <name> [--full]` | Rebuild the container — confirm first |
| `gh codespace stop -c <name>` | Stop (stops compute billing) |
| `gh codespace delete -c <name> [-f]` | Delete — unpushed work is lost, confirm first |
| `gh codespace delete --all [--days <n>] [-R <repo>]` | Delete all / those older than N days — confirm first |
| `gh codespace code -c <name> [-w] [--insiders]` / `gh codespace jupyter -c <name>` | Open in VS Code / JupyterLab (opens a GUI) |

Org admins: `-o <org> [-u <user>]` on `list`, `stop`, `delete`.
`<machine>` values depend on the repo: `gh api repos/{owner}/{repo}/codespaces/machines`.
