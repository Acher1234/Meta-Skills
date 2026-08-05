## Common Tasks (30-Second Solutions)

### Check cache status
```bash
# Basic status
jira-as ops cache-status

# Output as JSON
jira-as ops cache-status --json

# Verbose output (-v is short for --verbose)
jira-as ops cache-status -v
jira-as ops cache-status --verbose
```

### Warm the cache
```bash
# Cache project list
jira-as ops cache-warm --projects

# Cache field definitions
jira-as ops cache-warm --fields

# Cache assignable users (requires project context)
jira-as ops cache-warm --users

# Cache all available metadata with verbose output
jira-as ops cache-warm --all --verbose

# Output as JSON
jira-as ops cache-warm --all --json
```

### Clear cache
```bash
# Clear all cache (with confirmation)
jira-as ops cache-clear

# Clear all cache (skip confirmation, -f is short for --force)
jira-as ops cache-clear -f
jira-as ops cache-clear --force

# Clear only issue cache (-c is short for --category)
# Categories: issue, project, user, field, search, default
jira-as ops cache-clear -c issue -f
jira-as ops cache-clear --category issue --force

# Preview what would be cleared
jira-as ops cache-clear --dry-run

# Clear keys matching pattern
jira-as ops cache-clear --pattern "PROJ-*" -c issue -f

# Clear specific cache key (requires --category)
jira-as ops cache-clear --key "PROJ-123" -c issue -f

# Output as JSON
jira-as ops cache-clear -f --json
```

### Discover project context
```bash
# Discover and output project context (text format)
jira-as ops discover-project PROJ

# Output as JSON (-o is short for --output)
jira-as ops discover-project PROJ -o json
jira-as ops discover-project PROJ --output json

# Verbose output with detailed analysis (-v is short for --verbose)
jira-as ops discover-project PROJ -v

# Custom sample size and period (-s, -d are short forms)
jira-as ops discover-project PROJ -s 200 -d 60
jira-as ops discover-project PROJ --sample-size 200 --days 60
```

See [Commands Guide](docs/COMMANDS.md) for complete documentation.
