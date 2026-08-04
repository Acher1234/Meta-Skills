## Examples

### Quick Start - Common Operations

```bash
# View available link types in your JIRA instance
jira-as relationships link-types
jira-as relationships link-types --filter block
jira-as relationships link-types --output json

# Create links using semantic flags
jira-as relationships link PROJ-1 --blocks PROJ-2
jira-as relationships link PROJ-1 --is-blocked-by PROJ-2   # Inverse direction
jira-as relationships link PROJ-1 --duplicates PROJ-2
jira-as relationships link PROJ-1 --clones PROJ-2          # Mark as clone
jira-as relationships link PROJ-1 --relates-to PROJ-2
jira-as relationships link PROJ-1 --type "Blocks" --to PROJ-2

# View and remove links
jira-as relationships get-links PROJ-123
jira-as relationships get-links PROJ-123 --direction outward
jira-as relationships unlink PROJ-1 PROJ-2
jira-as relationships unlink PROJ-1 PROJ-2 --dry-run
jira-as relationships unlink PROJ-1 --type blocks --all

# Clone an issue with its relationships
jira-as relationships clone PROJ-123 --clone-subtasks -l  # -l is short for --clone-links
jira-as relationships clone PROJ-123 -p OTHER  # -p is short for --to-project
jira-as relationships clone PROJ-123 --summary "Custom summary"
jira-as relationships clone PROJ-123 --no-link  # Skip creating "clones" link
```

### Advanced - Blocker Analysis & Statistics

```bash
# Find blocker chains for sprint planning
jira-as relationships get-blockers PROJ-123 --recursive
jira-as relationships get-blockers PROJ-123 --recursive --include-done
jira-as relationships get-blockers PROJ-123 -r --depth 3  # Limit recursion depth (0 = unlimited)
jira-as relationships get-blockers PROJ-123 -r --depth 0  # Unlimited depth
jira-as relationships get-blockers PROJ-123 -d inward  # -d/--direction: inward or outward

# Analyze dependencies (with link type filtering)
jira-as relationships get-dependencies PROJ-123
jira-as relationships get-dependencies PROJ-123 -t blocks,relates  # -t/--type for filtering

# Link statistics - multiple modes
# KEY_OR_PROJECT: optional positional argument for issue key or project key
# -p/--project: alternative option to specify project for project-wide analysis
jira-as relationships stats PROJ-123                       # Single issue stats (positional arg)
jira-as relationships stats PROJ                           # Project-wide stats (positional arg)
jira-as relationships stats -p PROJ                        # Project-wide stats (-p/--project option)
jira-as relationships stats --jql "type = Epic"            # JQL-filtered stats
jira-as relationships stats -p PROJ -t 20                  # Show top 20 connected (-t/--top)
jira-as relationships stats -p PROJ --max-results 100      # Limit issues analyzed

# Bulk link issues from JQL query (--output json for JSON output)
jira-as relationships bulk-link --jql "project=PROJ AND fixVersion=1.0" --relates-to PROJ-500 --dry-run
jira-as relationships bulk-link --issues PROJ-1,PROJ-2,PROJ-3 --blocks PROJ-100
jira-as relationships bulk-link --issues PROJ-1,PROJ-2 --blocks PROJ-100 --output json
jira-as relationships bulk-link --jql "sprint in openSprints()" --relates-to PROJ-500 --skip-existing  # Skip already linked
```

### Visualization - Dependency Graphs

```bash
# Export for documentation (Mermaid for GitHub/GitLab)
jira-as relationships get-dependencies PROJ-123 --output mermaid

# Export for publication (Graphviz)
jira-as relationships get-dependencies PROJ-123 --output dot > deps.dot
dot -Tpng deps.dot -o deps.png

# Export for PlantUML
jira-as relationships get-dependencies PROJ-123 --output plantuml > deps.puml

# Export for D2/Terrastruct
jira-as relationships get-dependencies PROJ-123 --output d2 > deps.d2
d2 deps.d2 deps.svg
```
