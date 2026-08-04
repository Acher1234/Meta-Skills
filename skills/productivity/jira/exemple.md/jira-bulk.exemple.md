## Examples

### Bulk Transition

```bash
# By issue keys
jira-as bulk transition --issues PROJ-1,PROJ-2,PROJ-3 --to Done

# By JQL query
jira-as bulk transition --jql "project=PROJ AND status=\"In Progress\"" --to Done

# With resolution
jira-as bulk transition --jql "type=Bug AND status=Verified" --to Closed --resolution Fixed
```

### Bulk Assign

```bash
# Assign to user
jira-as bulk assign --jql "project=PROJ AND status=Open" --assignee "john.doe"

# Assign to self
jira-as bulk assign --jql "project=PROJ AND assignee IS EMPTY" --assignee self

# Unassign
jira-as bulk assign --jql "assignee=john.leaving" --unassign
```

### Bulk Set Priority

```bash
jira-as bulk set-priority --jql "type=Bug AND labels=critical" --priority Highest

# Output as JSON
jira-as bulk set-priority --jql "type=Bug" --priority High --dry-run -o json
```

### Bulk Clone

```bash
# ALWAYS preview first with dry-run (cloning creates many issues)
jira-as bulk clone --jql "sprint=\"Sprint 42\"" --include-subtasks --dry-run

# After reviewing the preview, execute without --dry-run
jira-as bulk clone --jql "sprint=\"Sprint 42\"" --include-subtasks --include-links

# Clone to different project
jira-as bulk clone --issues PROJ-1,PROJ-2 --target-project NEWPROJ --prefix "[Clone]"
```

### Bulk Delete (DESTRUCTIVE)

```bash
# ALWAYS preview first with dry-run
jira-as bulk delete --jql "project=CLEANUP" --dry-run

# Delete by issue keys (preview first)
jira-as bulk delete --issues DEMO-1,DEMO-2,DEMO-3 --dry-run

# Execute deletion (after confirming dry-run output)
jira-as bulk delete --jql "project=CLEANUP" --yes

# Keep subtasks when deleting parent issues (subtasks deleted by default)
jira-as bulk delete --jql "project=CLEANUP" --no-subtasks --dry-run
```

**Safety features:**
- `--dry-run` shows exactly what will be deleted before making changes
- Confirmation required for >10 issues (lower than other operations)
- Default `--max-issues 100` prevents accidental mass deletion
- Per-issue error tracking with summary of failures
