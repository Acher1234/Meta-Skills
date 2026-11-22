# gh-cli-auth — Commands

`gh` 2.103.0. Flags not listed: `gh <command> --help`. Rules: `gh-cli` SKILL.md.

## Auth

| Command | Description |
|---------|-------------|
| `gh auth status [-a] [-h <host>] [--json hosts]` | Accounts, active account, token scopes per host |
| `gh auth switch [-u <user>] [-h <host>]` | Change the active account (multi-account) |
| `gh auth setup-git [-h <host>]` | Use `gh` as git credential helper (HTTPS) |
| `gh auth login [-h <host>] [-p ssh\|https] [-s <scopes>] [-w] [--with-token]` | Log in — **interactive, the user runs it** |
| `gh auth refresh [-s <scopes>] [-r <scopes>] [--reset-scopes]` | Add / remove token scopes — **interactive, the user runs it** |
| `gh auth logout [-u <user>] [-h <host>]` | Log out — confirm first |
| `gh auth token [-u <user>] [-h <host>]` | Print the token — never display it; pipe it only (`$(gh auth token)`) |

### Scopes

Default token: `repo`, `read:org`, `gist`. Extra scopes, added by the user with
`gh auth refresh -s <scope>` — when one is missing, the error message names it:

| Scope | Needed for |
|-------|------------|
| `read:project` / `project` | `gh project …` — read / write |
| `workflow` | pushing changes to `.github/workflows/*` |
| `delete_repo` | `gh repo delete` |
| `admin:public_key` / `admin:ssh_signing_key` | `gh ssh-key add` (authentication / signing key) |
| `write:gpg_key` | `gh gpg-key add` |
| `codespace` | `gh codespace …` |
| `admin:org` | organization secrets and variables |
| `read:packages`, `user`, … | matching `gh api` endpoints |

## Config, alias, completion

| Command | Description |
|---------|-------------|
| `gh config list [-h <host>]` | All keys and values |
| `gh config get <key> [-h <host>]` | One value |
| `gh config set <key> <value> [-h <host>]` | Set (e.g. `git_protocol ssh`, `prompt disabled`, `pager cat`) |
| `gh config clear-cache` | Clear the CLI cache |
| `gh alias list` | Defined aliases |
| `gh alias set <alias> <expansion> [-s] [--clobber]` | Create a shortcut (`-s` = run through a shell) |
| `gh alias delete {<alias> \| --all}` | Remove aliases |
| `gh alias import [<file> \| -] [--clobber]` | Import aliases from YAML |
| `gh completion -s bash\|zsh\|fish\|powershell` | Shell completion script |

Config keys: `git_protocol`, `editor`, `prompt`, `prefer_editor_prompt`, `pager`,
`browser`, `clipboard`, `http_unix_socket`, `api_host`, `expiring_credentials`,
`color_labels`, `accessible_colors`, `accessible_prompter`, `spinner`, `telemetry`.

## SSH and GPG keys

| Command | Description |
|---------|-------------|
| `gh ssh-key list` | SSH keys of the account |
| `gh ssh-key add [<key-file>] [-t <title>] [--type authentication\|signing]` | Upload a public key |
| `gh ssh-key delete <id> [-y]` | Remove — confirm first |
| `gh gpg-key list` / `add [<key-file>] [-t <title>]` / `delete <key-id> [-y]` | GPG keys |

## Environment variables

| Variable | Effect |
|----------|--------|
| `GH_TOKEN`, `GITHUB_TOKEN` | Token for github.com (overrides the stored login) |
| `GH_ENTERPRISE_TOKEN`, `GITHUB_ENTERPRISE_TOKEN` | Token for a GitHub Enterprise Server host |
| `GH_HOST` | Default host when not in a git repo |
| `GH_REPO` | Default repo, `[HOST/]OWNER/REPO` — same as `-R` |
| `GH_PROMPT_DISABLED` | Any value: no interactive prompts |
| `GH_PAGER` / `PAGER` | Pager; `cat` disables paging |
| `GH_EDITOR`, `GIT_EDITOR`, `VISUAL`, `EDITOR` | Editor (in that order) |
| `GH_BROWSER` / `BROWSER` | Browser used by `--web` |
| `GH_DEBUG` | `1` = verbose, `api` = also log HTTP traffic |
| `GH_FORCE_TTY` | Force terminal-style output (value = columns or `%`) |
| `GH_CONFIG_DIR` | Config directory (default `~/.config/gh`) |
| `NO_COLOR`, `CLICOLOR`, `CLICOLOR_FORCE` | Color control |
| `GH_NO_UPDATE_NOTIFIER`, `GH_NO_EXTENSION_UPDATE_NOTIFIER` | Silence upgrade notices |
| `GH_SPINNER_DISABLED`, `GH_TELEMETRY`, `GH_MDWIDTH`, `GLAMOUR_STYLE` | Spinner, telemetry, Markdown rendering |

Full list: `gh help environment`.

## Exit codes

`0` success · `1` failure · `2` cancelled · `4` authentication required ·
`8` checks pending (`gh pr checks` only). `gh auth status` exits `1` when an
account has a problem (always `0` with `--json`).
