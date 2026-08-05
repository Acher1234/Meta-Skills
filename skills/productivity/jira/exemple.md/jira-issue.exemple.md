## Example Workflows

### Create and View Issue

This is the most common workflow - create an issue, then immediately view its details:

```bash
# 1. Create a bug
jira-as issue create --project DEMO --type Bug --summary "Login fails on mobile" --priority High

# Output: Created DEMO-105

# 2. View the details of the bug we just created
jira-as issue get DEMO-105

# Output shows:
# - Issue Key: DEMO-105
# - Type: Bug
# - Summary: Login fails on mobile
# - Priority: High
# - Status: Open (or whatever the initial status is)
# - And all other fields
```

**When user says "Show me the details of the bug we just created"**, this skill should:
1. Identify the most recently created issue from context (e.g., DEMO-105)
2. Execute: `jira-as issue get DEMO-105`
3. Display the full issue details including key, type, summary, priority, status, etc.
