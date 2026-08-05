## Getting Started

### 30-Second Start

```bash
# List all projects
jira-as admin project list

# See project configuration
jira-as admin config get PROJ

# Search for users
jira-as admin user search "john" --include-groups
```

---

## Common Patterns

### Preview Before Changing
```bash
jira-as admin project delete PROJ --dry-run
jira-as admin group delete GROUP_NAME --dry-run
jira-as admin permission-scheme assign --project PROJ --scheme 10050 --dry-run
```

### JSON Output for Scripting
```bash
jira-as admin project list --output json
jira-as admin workflow get --name "Workflow" --output json
```

### Profile Selection
```bash
```

---
