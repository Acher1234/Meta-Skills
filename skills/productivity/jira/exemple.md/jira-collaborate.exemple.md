## Quick Start Examples

```bash
# Add a comment
jira-as collaborate comment add PROJ-123 --body "Starting work on this now"

# Rich text comment (--format supports: markdown, wiki, adf)
jira-as collaborate comment add PROJ-123 --body "**Bold** text" --format markdown

# Internal comment (role-restricted)
jira-as collaborate comment add PROJ-123 --body "Internal note" --visibility-role Administrators

# Internal comment (group-restricted)
jira-as collaborate comment add PROJ-123 --body "Team only" --visibility-group jira-developers

# List comments (supports --order asc or desc)
jira-as collaborate comment list PROJ-123
jira-as collaborate comment list PROJ-123 -l 10 --order desc

# Get specific comment by ID
jira-as collaborate comment list PROJ-123 --id 10001

# List comments with pagination
jira-as collaborate comment list PROJ-123 -l 10 --offset 20

# Update a comment (requires comment ID)
jira-as collaborate comment update PROJ-123 --id 10001 --body "Updated text"

# Delete a comment (preview first)
jira-as collaborate comment delete PROJ-123 --id 10001 --dry-run

# Delete a comment (confirmed)
jira-as collaborate comment delete PROJ-123 --id 10001 --yes

# Upload attachment (-f is short for --file)
jira-as collaborate attachment upload PROJ-123 -f screenshot.png
jira-as collaborate attachment upload PROJ-123 --file screenshot.png

# Upload attachment with custom name (-n is short for --name)
jira-as collaborate attachment upload PROJ-123 -f screenshot.png -n evidence-2024.png

# List attachments on issue
jira-as collaborate attachment list PROJ-123

# Download attachment by ID (-o is short for --output-dir)
jira-as collaborate attachment download PROJ-123 --id 12345 -o ./downloads/

# Download attachment by filename
jira-as collaborate attachment download PROJ-123 --name error.log -o ./downloads/

# Download all attachments from issue
jira-as collaborate attachment download PROJ-123 --all -o ./backups/

# List watchers (-l is short for --list)
jira-as collaborate watchers PROJ-123 -l
jira-as collaborate watchers PROJ-123 --list

# Add watcher (-a is short for --add)
jira-as collaborate watchers PROJ-123 -a user@example.com

# Remove watcher (-r is short for --remove)
jira-as collaborate watchers PROJ-123 -r user@example.com

# Send notification to watchers
jira-as collaborate notify PROJ-123 --watchers --subject "Update" --body "Issue resolved"

# Send notification to voters
jira-as collaborate notify PROJ-123 --voters --subject "Vote counted"

# Send notification to a group
jira-as collaborate notify PROJ-123 --group developers --subject "Team update"

# Send notification to specific users (requires account ID)
jira-as collaborate notify PROJ-123 --user 5b10ac8d82e05b22cc7d4ef5 --subject "Review needed"

# Send notification to assignee and reporter
jira-as collaborate notify PROJ-123 --assignee --reporter --subject "Please review"

# Preview notification without sending
jira-as collaborate notify PROJ-123 --watchers --dry-run

# View activity history
jira-as collaborate activity PROJ-123

# View activity with filters
jira-as collaborate activity PROJ-123 --field status --field assignee --output table
jira-as collaborate activity PROJ-123 --field-type custom --limit 10

# View activity with pagination
jira-as collaborate activity PROJ-123 --limit 10 --offset 20

# Update custom fields (JSON format)
jira-as collaborate update-fields PROJ-123 --fields '{"customfield_10014": "value"}'

# Update multiple fields
jira-as collaborate update-fields PROJ-123 --fields '{"customfield_10014": "Epic Name", "customfield_10016": 5}'

# Update with array values
jira-as collaborate update-fields PROJ-123 --fields '{"labels": ["urgent", "customer"]}'
```
