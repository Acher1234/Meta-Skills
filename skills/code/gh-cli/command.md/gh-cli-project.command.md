# gh-cli-project — Commands

`gh` 2.103.0. Flags not listed: `gh <command> --help`. Rules: `gh-cli` SKILL.md.

GitHub Projects (v2). **Needs a token scope the default login lacks**:
`read:project` to read, `project` to write — missing → the user runs
`gh auth refresh -s project`.

A project is addressed by `<number>` + `--owner <login>` (`@me` = current user,
or an org login) — not by repo, so `-R` does not apply. JSON output is
`--format json` (+ `-q <jq>`), not `--json <fields>`.

## Projects

| Command | Description |
|---------|-------------|
| `gh project list --owner <login> [--closed] [-L <n>] [--format json]` | Projects of a user / org |
| `gh project view <number> --owner <login> [--format json]` | One project |
| `gh project create --owner <login> --title "<title>" [--format json]` | New project — confirm first |
| `gh project edit <number> --owner <login> [--title "<t>"] [-d "<desc>"] [--readme "<text>"] [--visibility PUBLIC\|PRIVATE]` | Edit — confirm first |
| `gh project copy <number> --source-owner <login> --target-owner <login> --title "<title>" [--drafts]` | Duplicate — confirm first |
| `gh project close <number> --owner <login> [--undo]` | Close / reopen — confirm first |
| `gh project delete <number> --owner <login>` | Delete — irreversible, confirm first |
| `gh project mark-template <number> --owner <org> [--undo]` | Mark / unmark as org template |
| `gh project link <number> --owner <login> -R <repo>\|-T <team>` | Link to a repo or team |
| `gh project unlink <number> --owner <login> -R <repo>\|-T <team>` | Remove the link |

## Fields

| Command | Description |
|---------|-------------|
| `gh project field-list <number> --owner <login> [-L <n>] [--format json]` | Fields, their ids and single-select option ids |
| `gh project field-create <number> --owner <login> --name "<name>" --data-type TEXT\|NUMBER\|DATE\|SINGLE_SELECT [--single-select-options "<a>,<b>"]` | Add a field — confirm first |
| `gh project field-delete --id <field-id>` | Delete a field — confirm first |

## Items

| Command | Description |
|---------|-------------|
| `gh project item-list <number> --owner <login> [--query "<filter>"] [--field "<name>"]… [-L <n>] [--format json]` | Items (default 30 — raise `-L`); `--query` uses the Projects filter syntax, e.g. `"assignee:octocat -status:Done"` |
| `gh project item-add <number> --owner <login> --url <issue-or-pr-url>` | Add an existing issue / PR — confirm first |
| `gh project item-create <number> --owner <login> --title "<title>" [--body "<text>"]` | Add a draft issue — confirm first |
| `gh project item-edit <number> --owner <login> --url <issue-or-pr-url> --field "<name>" --value "<value>"` | Set a field by name (single-select: `--value` = option name) — confirm first |
| `gh project item-edit <number> --owner <login> --url <issue-or-pr-url> --field "<name>" --clear` | Clear a field value |
| `gh project item-edit --id <item-id> --project-id <project-id> --field-id <field-id> --text "<v>"\|--number <n>\|--date <YYYY-MM-DD>\|--single-select-option-id <id>\|--iteration-id <id>` | Same, by GraphQL node ids |
| `gh project item-edit --id <draft-item-id> --title "<title>" --body "<text>"` | Edit a draft issue item |
| `gh project item-archive <number> --owner <login> --id <item-id> [--undo]` | Archive / unarchive an item |
| `gh project item-delete <number> --owner <login> --id <item-id>` | Remove an item from the project — confirm first |

`--url` is the issue / PR URL (its owner may differ from the project owner).
One field value per `item-edit` call for non-draft items.

## Move an issue to a status column

```bash
gh project item-add 3 --owner my-org --url https://github.com/my-org/app/issues/42
gh project item-edit 3 --owner my-org \
  --url https://github.com/my-org/app/issues/42 --field Status --value "In progress"
```

Ids when needed: project `gh project view <n> --owner <o> --format json -q .id`;
items `gh project item-list … --format json -q '.items[] | {id, title}'`;
fields and options `gh project field-list … --format json`.

Issues and PRs can also be attached at creation: `gh issue create -p "<project title>"`,
`gh pr edit --add-project "<project title>"`.
