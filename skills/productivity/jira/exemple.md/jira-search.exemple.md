## Examples by Category

### Search

```bash
# Basic search
jira-as search query "project = PROJ AND status = Open"

# With field selection
jira-as search query "project = PROJ" --fields key,summary,status,assignee

# With result limit
jira-as search query "project = PROJ" --max-results 50
```

### JQL Building

```bash
# Validate syntax (--show-structure shows parse tree, --output for format)
jira-as search validate "project = PROJ AND status = Open"
jira-as search validate "project = PROJ" --show-structure
jira-as search validate "project = PROJ" --output json

# Build JQL from clauses (--operator selects AND or OR between clauses)
jira-as search build --clause "project = PROJ" --clause "status = Open" --validate
jira-as search build --clause "status = Open" --clause "status = Closed" --operator OR
jira-as search build --clause "assignee = currentUser()" --order-by created --desc
jira-as search build --template sprint-backlog  # Use a predefined template
jira-as search build --list-templates           # List available templates

# Get field suggestions
jira-as search suggest --field status
jira-as search suggest --field status --prefix "In"
jira-as search suggest --field assignee --prefix "john"
jira-as search suggest --field priority --no-cache   # Skip cache
jira-as search suggest --field status --refresh      # Refresh cached values

# List available fields and operators
jira-as search fields
jira-as search fields --custom-only             # Only custom fields
jira-as search fields --system-only             # Only system fields
jira-as search fields --filter priority         # Filter by name

# List available JQL functions (-t is short for --type)
jira-as search functions
jira-as search functions -t list                # Only list-returning functions
jira-as search functions --list-only            # Only list-returning functions
jira-as search functions --with-examples        # Include usage examples
```

### Saved Filters

```bash
# Create filter (use -n and -j options, or long forms --name and --jql)
jira-as search filter create -n "Sprint Issues" -j "sprint IN openSprints()" -f
jira-as search filter create -n "Team Filter" -j "project = PROJ" -d "Team issues" --share-project PROJ

# List filters
jira-as search filter list --favourites          # Your favourite filters
jira-as search filter list --my                  # Your own filters
jira-as search filter list --search "Sprint"     # Search by name
jira-as search filter list --owner "john@co.com" # By owner
jira-as search filter list --project PROJ        # By project scope
jira-as search filter list --id 10042            # Get specific filter by ID

# Run filter (use --id or --name option)
jira-as search filter run --id 10042
jira-as search filter run --name "Sprint Issues"
jira-as search filter run --id 10042 --max-results 50  # Limit results

# Update filter
jira-as search filter update 10042 --name "New Name" --jql "updated JQL"
jira-as search filter update 10042 --description "New description"

# Toggle favourite status
jira-as search filter favourite 10042 --add
jira-as search filter favourite 10042 --remove

# Share filter
jira-as search filter share 10042 --project PROJ
jira-as search filter share 10042 --project PROJ --role Developers
jira-as search filter share 10042 --group jira-users
jira-as search filter share 10042 --global
jira-as search filter share 10042 --list         # View current permissions
jira-as search filter share 10042 --unshare 10100  # Remove permission by ID (use --list first)

# Delete filter (use --yes to skip confirmation, --dry-run to preview)
jira-as search filter delete 10042 --dry-run     # Preview deletion
jira-as search filter delete 10042 --yes         # Skip confirmation
```

### Bulk Update

```bash
# Add labels to all matching issues (dry-run first!)
jira-as search bulk-update "project = PROJ AND status = Open" --add-labels needs-review --dry-run
jira-as search bulk-update "project = PROJ AND status = Open" --add-labels needs-review --yes

# Remove labels
jira-as search bulk-update "type = Bug AND labels = stale" --remove-labels stale --dry-run

# Change priority
jira-as search bulk-update "project = PROJ AND priority = Low" --priority Medium --dry-run

# Limit number of issues updated
jira-as search bulk-update "project = PROJ" --add-labels batch1 --max-issues 50 --dry-run
```

### Export

```bash
# CSV export
jira-as search export "project = PROJ" -o report.csv

# JSON export
jira-as search export "project = PROJ" -o data.json --format json

# Export specific fields
jira-as search export "project = PROJ" -o report.csv --fields key,summary,status,assignee

# Limit results
jira-as search export "project = PROJ" -o report.csv --max-results 500
```

### Using Filters in Queries

```bash
# Run a query using a saved filter ID
jira-as search query --filter 10042

# Combine filter with additional criteria
jira-as search query --filter 10042 --max-results 100

# Save search results as a new filter
jira-as search query "project = PROJ" --save-as "My New Filter"
```
