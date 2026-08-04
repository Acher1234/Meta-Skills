## Examples

### Setting up Agile for a new project
```bash
# 1. Check what fields are available in the project
jira-as fields check-project NEWPROJ --check-agile

# 2. Find Agile field IDs in your instance
jira-as fields list --agile

# 3. Preview configuration changes (dry run)
jira-as fields configure-agile NEWPROJ --dry-run

# 4. Configure Agile fields with correct IDs
jira-as fields configure-agile NEWPROJ --story-points customfield_10016 --epic-link customfield_10014
```

### Creating a company-managed Scrum project
```bash
# Create project with Scrum template (includes Agile fields)
# Use the JIRA UI or:
# POST /rest/api/3/project with:
#   projectTemplateKey: com.pyxis.greenhopper.jira:gh-scrum-template
```

### Diagnosing missing fields
```bash
# Filter for fields by name
jira-as fields list --filter "story"

# Check what's available for the project
jira-as fields check-project PROJ

# Check Agile field availability
jira-as fields check-project PROJ --check-agile
```
