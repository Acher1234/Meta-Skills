## Available Commands

### Epic Management
```bash
jira-as agile epic create --project PROJ --summary "Mobile App MVP"
jira-as agile epic create --project PROJ --summary "MVP" --epic-name "Mobile MVP" --color blue
jira-as agile epic get PROJ-100 --with-children
jira-as agile epic add-issues --epic PROJ-100 --issues PROJ-101,PROJ-102
jira-as agile epic add-issues --epic PROJ-100 --jql "project = PROJ AND type = Story AND status = Open"
jira-as agile epic add-issues --epic PROJ-100 --issues PROJ-101 --dry-run  # Preview changes
```

**Note:** To remove issues from an epic, move them to a different epic or use `jira-as issue update PROJ-103 --epic none` to clear the epic link.

### Subtask Management
```bash
jira-as agile subtask --parent PROJ-101 --summary "Implement login API"
jira-as agile subtask --parent PROJ-101 --summary "Task" --assignee self --estimate 4h
```

### Sprint Management
```bash
jira-as agile sprint list --project DEMO                    # List all sprints for project
jira-as agile sprint list --project DEMO --state active     # Find active sprint
jira-as agile sprint list --board 123 --state closed        # List closed sprints
jira-as agile sprint list --board 123 --max-results 50      # Limit results
jira-as agile sprint get --board 123 --active               # Get active sprint details
jira-as agile sprint get 456 --include-issues               # Get sprint with issues
jira-as agile sprint create --board 123 --name "Sprint 42" --goal "Launch MVP"
jira-as agile sprint create --board 123 --name "Sprint 42" --start-date 2026-02-01 --end-date 2026-02-14
jira-as agile sprint move-issues --sprint 456 --issues PROJ-101,PROJ-102
jira-as agile sprint move-issues --sprint 456 --jql "project = PROJ AND sprint IS EMPTY"
jira-as agile sprint move-issues --backlog --issues PROJ-101,PROJ-102  # Move to backlog
jira-as agile sprint manage --sprint 456 --start
jira-as agile sprint manage --sprint 456 --close --move-incomplete-to 457
jira-as agile sprint manage --sprint 456 --name "Sprint 42 - Revised" --goal "Updated goal"
```

### Backlog Management
```bash
jira-as agile backlog --board 123
jira-as agile backlog --board 123 --group-by epic
jira-as agile backlog --project PROJ                        # Use project instead of board
jira-as agile rank PROJ-101 --before PROJ-100
jira-as agile rank PROJ-101 --after PROJ-102
jira-as agile rank PROJ-101 --top --board 123               # Move to top (requires --board)
jira-as agile rank PROJ-101 --bottom --board 123            # Move to bottom (requires --board)
```

### Story Points and Estimation
```bash
jira-as agile estimate PROJ-101 --points 5
jira-as agile estimates --project PROJ
jira-as agile estimates --sprint 456 --group-by assignee
jira-as agile estimates --epic "Mobile MVP" --group-by status  # Filter by epic name
```

### Velocity Tracking
```bash
jira-as agile velocity --project PROJ                     # Last 3 sprints
jira-as agile velocity --project PROJ -n 5                # Last 5 sprints (-n is short for --sprints)
jira-as agile velocity --project PROJ --sprints 5         # Last 5 sprints
jira-as agile velocity --board 123 --output json          # JSON output
```

All commands support `--help` for full documentation.
