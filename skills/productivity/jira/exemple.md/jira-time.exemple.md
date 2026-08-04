## Examples

### Log time to an issue

```bash
# Log 2 hours of work
jira-as time log PROJ-123 -t 2h

# Log time with a comment
jira-as time log PROJ-123 -t "1d 4h" -c "Debugging authentication issue"

# Log time for yesterday
jira-as time log PROJ-123 -t 2h -s yesterday

# Log time without adjusting estimate
jira-as time log PROJ-123 -t 2h --adjust-estimate leave

# Log time and set new remaining estimate
jira-as time log PROJ-123 -t 2h --adjust-estimate new --new-estimate 4h

# Log time with visibility restriction
jira-as time log PROJ-123 -t 2h --visibility-type role --visibility-value Developers

# Output as JSON
jira-as time log PROJ-123 -t 2h -o json
```

### View worklogs

```bash
# List all worklogs for an issue
jira-as time worklogs PROJ-123

# Filter by author (-a is short for --author)
jira-as time worklogs PROJ-123 -a currentUser()
jira-as time worklogs PROJ-123 --author currentUser()

# Filter by date range (-s, -u are short forms)
jira-as time worklogs PROJ-123 -s 2026-01-01 -u 2026-01-31
jira-as time worklogs PROJ-123 --since 2026-01-01 --until 2026-01-31

# Output as JSON
jira-as time worklogs PROJ-123 -o json
```

### Manage estimates

```bash
# Set original estimate
jira-as time estimate PROJ-123 --original 2d

# Set remaining estimate
jira-as time estimate PROJ-123 --remaining "1d 4h"

# Set both estimates together (recommended)
jira-as time estimate PROJ-123 --original 2d --remaining 1d

# View time tracking summary
jira-as time tracking PROJ-123

# View time tracking as JSON
jira-as time tracking PROJ-123 -o json
```

### Update worklogs

```bash
# Update time on existing worklog
jira-as time update-worklog PROJ-123 -w 12345 -t 3h

# Update worklog comment
jira-as time update-worklog PROJ-123 -w 12345 -c "Updated description"

# Update worklog start time
jira-as time update-worklog PROJ-123 -w 12345 -s 2025-01-15

# Update with automatic estimate adjustment
jira-as time update-worklog PROJ-123 -w 12345 -t 4h --adjust-estimate auto

# Update and set new remaining estimate
jira-as time update-worklog PROJ-123 -w 12345 -t 4h --adjust-estimate new --new-estimate 2d

# Output as JSON
jira-as time update-worklog PROJ-123 -w 12345 -t 3h -o json
```

### Generate reports

```bash
# My time for last week
jira-as time report -u currentUser() --period last-week

# Project time for this month
jira-as time report -p PROJ --period this-month

# Report for specific month using YYYY-MM format
jira-as time report -p PROJ --period 2025-01

# Export to CSV for billing
jira-as time report -p PROJ -s 2025-01-01 --until 2025-01-31 -f csv > timesheet.csv

# Group by day for daily summary
jira-as time report -p PROJ --period this-week -g day

# Group by user for team summary
jira-as time report -p PROJ --period this-month -g user -f json

# JSON output for scripting (pipe to jq for processing)
jira-as time report -p PROJ --period this-week -f json | jq ".worklogs[] | {user: .author, hours: .timeSpentSeconds/3600}"
```

### Export timesheets

```bash
# Export last month's timesheets to CSV
jira-as time export -p PROJ --period last-month -o timesheets.csv

# Export specific month using YYYY-MM format
jira-as time export -p PROJ --period 2025-01 -o january.csv

# Export to JSON for integration
jira-as time export -p PROJ -s 2025-01-01 --until 2025-01-31 -f json -o timesheets.json

# Export user's timesheets for billing
jira-as time export -u alice@company.com --period this-month -o billing.csv
```

**Note:** For export, `-o/--output` specifies the file path and `-f/--format` specifies the format (csv or json).

### Bulk operations

```bash
# Preview bulk time logging (dry run)
jira-as time bulk-log -i PROJ-1,PROJ-2 -t 15m -c "Sprint planning" -n

# Log standup time to multiple issues
jira-as time bulk-log -i PROJ-1,PROJ-2 -t 15m -c "Sprint planning"

# Log time to JQL results with dry run
jira-as time bulk-log -j "sprint = 456" -t 15m -c "Daily standup" -n

# Execute after confirming dry run output
jira-as time bulk-log -j "sprint = 456" -t 15m -c "Daily standup"

# Skip confirmation prompt with force flag
jira-as time bulk-log -i PROJ-1,PROJ-2 -t 15m -c "Team meeting" -f

# Output results as JSON
jira-as time bulk-log -i PROJ-1,PROJ-2 -t 15m -c "Meeting" -o json
```

### Delete worklogs

```bash
# Preview worklog deletion (dry run)
jira-as time delete-worklog PROJ-123 -w 12345 --dry-run

# Delete with automatic estimate adjustment
jira-as time delete-worklog PROJ-123 -w 12345 --adjust-estimate auto

# Delete without modifying estimate
jira-as time delete-worklog PROJ-123 -w 12345 --adjust-estimate leave

# Delete and set new remaining estimate
jira-as time delete-worklog PROJ-123 -w 12345 --adjust-estimate new --new-estimate 3d

# Delete and increase estimate by specific amount (manual mode)
jira-as time delete-worklog PROJ-123 -w 12345 --adjust-estimate manual --increase-by 2h

# Delete without confirmation prompt
jira-as time delete-worklog PROJ-123 -w 12345 --yes
```
