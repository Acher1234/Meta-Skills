### Quick Examples

```bash
# Generate branch name with default prefix (feature)
jira-as dev branch-name PROJ-123

# Generate branch name with explicit prefix (-p is short for --prefix)
jira-as dev branch-name PROJ-123 -p bugfix
jira-as dev branch-name PROJ-123 --prefix bugfix

# Auto-detect prefix from issue type (Bug -> bugfix, Story -> feature, etc.)
jira-as dev branch-name PROJ-123 --auto-prefix

# Output git checkout command directly (-o is short for --output)
jira-as dev branch-name PROJ-123 -o git

# Extract issues from a single commit message
jira-as dev parse-commits "feat(PROJ-123): add login"

# Extract issues from git log via pipe
git log --oneline -10 | jira-as dev parse-commits --from-stdin

# Filter to specific project (-p is short for --project)
jira-as dev parse-commits "Fix PROJ-123 and OTHER-456" -p PROJ

# Generate PR description with testing checklist (-c is short for --include-checklist)
jira-as dev pr-description PROJ-123 -c
jira-as dev pr-description PROJ-123 --include-checklist

# Generate PR description with labels (-l is short for --include-labels)
jira-as dev pr-description PROJ-123 -l --include-components

# Generate PR description and copy to clipboard
jira-as dev pr-description PROJ-123 --copy

# Link PR to issue (-p is short for --pr)
jira-as dev link-pr PROJ-123 -p https://github.com/org/repo/pull/456

# Link PR with title (-t is short for --title)
jira-as dev link-pr PROJ-123 -p https://github.com/org/repo/pull/456 -t "Fix authentication bug"

# Link PR with status and author (-s, -a are short forms)
jira-as dev link-pr PROJ-123 -p https://github.com/org/repo/pull/456 -s merged -a "Jane Doe"

# Link commit to issue (-c is short for --commit, -m for --message, -r for --repo)
jira-as dev link-commit PROJ-123 -c abc123def -m "feat: add login" -r https://github.com/org/repo

# Link commit with additional metadata (-a for --author, -b for --branch)
jira-as dev link-commit PROJ-123 -c abc123def -a "John Doe" -b feature/login

# Get commits linked to issue
jira-as dev get-commits PROJ-123

# Get commits with detailed information
jira-as dev get-commits PROJ-123 --detailed

# Get commits filtered by repository (-o is short for --output)
jira-as dev get-commits PROJ-123 --repo "org/repo" -o table
```
