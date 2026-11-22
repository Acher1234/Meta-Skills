# gh-cli-extension — Commands

`gh` 2.103.0. Flags not listed: `gh <command> --help`. Rules: `gh-cli` SKILL.md.

## Extensions

An extension is a repo named `gh-<name>` that adds the command `gh <name>`.
It runs third-party code with the user's token: install only on request, from
a source the user trusts.

| Command | Description |
|---------|-------------|
| `gh extension list` | Installed extensions and versions |
| `gh extension search [<query>] [--owner <o>] [--license <l>] [--sort stars\|updated\|forks] [-L <n>] [--json <fields>]` | Find extensions |
| `gh extension install <owner>/gh-<name> [--pin <tag\|sha>] [--force]` | Install — confirm first |
| `gh extension install .` | Install the extension in the current directory (development) |
| `gh extension upgrade <name>\|--all [--dry-run] [--force]` | Upgrade (`--dry-run` only lists) |
| `gh extension remove <name>` | Uninstall |
| `gh extension exec <name> [<args>]` | Run an extension whose name clashes with a core command |
| `gh extension create <name> [--precompiled go\|other]` | Scaffold a new extension (always pass `<name>`) |
| `gh extension browse` | Full-screen TUI — do not run unattended |

Aliases: `gh ext`, `gh extensions`.

## Agent skills (preview)

Installs `SKILL.md`-based skills from GitHub repos into an agent's skills
folder. Separate from this library's `/meta-skills` installer: do not mix both
for the same skill.

| Command | Description |
|---------|-------------|
| `gh skill search <query> [--owner <o>] [-L <n>] [--page <n>] [--json <fields>]` | Find skills on GitHub |
| `gh skill preview <repo> [<skill>]` | Show a skill's content before installing |
| `gh skill list [--agent <agent>] [--scope project\|user] [--dir <dir>] [--json <fields>]` | Installed skills |
| `gh skill install <repo> <skill>[@<version>] --agent <agent> [--scope project\|user] [--pin <tag\|sha>] [-f]` | Install one skill — confirm first |
| `gh skill install <repo> --all --agent <agent>` | Install every skill of a repo |
| `gh skill install <dir> --from-local --agent <agent>` | Install from a local directory |
| `gh skill update [<skill>…] [--all] [--dry-run] [--force] [--unpin]` | Update installed skills |
| `gh skill publish [<dir>] [--dry-run] [--fix] [--tag v1.0.0]` | Validate (`--dry-run`) and publish skills — confirm first |

`--agent` values include `claude-code`, `cursor`, `codex`, `opencode`,
`openclaw`, `github-copilot`, `gemini-cli` (full list: `gh skill list --help`).
`--scope` defaults to `project`; `--dir <dir>` overrides agent and scope. Pass
the skill name and `--agent` explicitly, otherwise `gh` prompts. Preview a
skill before installing it: it is instructions an agent will follow.

## Agent tasks (preview)

Delegates work to the Copilot coding agent, which opens a pull request.
Aliases: `gh agent`, `gh agents`.

| Command | Description |
|---------|-------------|
| `gh agent-task list [-L <n>] [--json <fields>]` | My agent tasks |
| `gh agent-task view <session-id\|pr> [--log] [--follow] [--json <fields>]` | One task; `--log` prints the session log, `--follow` streams it |
| `gh agent-task create "<task>" [-b <base-branch>] [-a <custom-agent>] [-R <repo>]` | Start a task — confirm first |
| `gh agent-task create -F <task-file> [--follow]` | Same, task description from a file (`-` = stdin) |

## Copilot CLI (preview)

| Command | Description |
|---------|-------------|
| `gh copilot [<args>]` | Download on first use, then run the GitHub Copilot CLI — interactive |
| `gh copilot --remove` | Remove the downloaded Copilot CLI |

## Preview

| Command | Description |
|---------|-------------|
| `gh preview prompter [<prompt-type>]` | Test program for `gh`'s interactive prompts — no use for agents |
