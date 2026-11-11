# orca-dev-repo — Commands

`ORCA` = resolved CLI (see `orca-dev` SKILL.md). Add `--json` everywhere; full
flags: `ORCA <command> --help`.

## Repos

| Command | Description |
|---------|-------------|
| `ORCA repo list` | Repos registered in Orca (`id`, `path`, `displayName`) |
| `ORCA repo add --path <path>` | Register a local repo/folder |
| `ORCA repo show --repo <sel>` | One repo |
| `ORCA repo set --repo <sel> --external-worktree-visibility show\|hide\|inherit` | Show non-Orca worktrees |
| `ORCA repo set-base-ref --repo <sel> --ref origin/main` | Default base for new worktrees |
| `ORCA repo search-refs --repo <sel> --query <text> [--limit <n>]` | Find branches / tags |

Repo selectors: `id:<id>`, `name:<name>`, `path:<path>`.

## Projects (durable, multi-host)

| Command | Description |
|---------|-------------|
| `ORCA project list` | Projects known to Orca |
| `ORCA project setups [--project <id>] [--host <host>]` | Host setups of a project |
| `ORCA project setup-existing-folder --project <id> --host <host> --path <path> [--kind git\|folder]` | Import an existing folder |
| `ORCA project setup-clone --project <id> --host <host> --url <git-url> --destination <path>` | Clone on a host |
| `ORCA project setup-create --project <id> --host <host> [--path] [--worktree-base-path] …` | Create setup metadata |
| `ORCA project setup-update --setup <id> [--path] [--worktree-base-path] [--state] …` | Update setup metadata |
| `ORCA project setup-delete --setup <id> [--force]` | Remove a setup — confirm first |

`--host`: `local`, `ssh:<target-id>`, `runtime:<environment-id>` or a name from `ORCA host list`.
