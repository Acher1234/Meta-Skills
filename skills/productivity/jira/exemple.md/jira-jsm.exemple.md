## Quick Start

```bash
# 1. List service desks to find your ID
jira-as jsm service-desk list

# 2. List request types for your service desk
jira-as jsm request-type list 1

# 3. Create an incident (--summary is required, --description is optional)
jira-as jsm request create 1 10 --summary "Email service down" --description "Production email server is not responding to connections"

# 3a. Create request on behalf of a customer (requires account ID, not email)
jira-as jsm request create 1 10 --summary "Password reset" --on-behalf-of "5b10ac8d82e05b22cc7d4ef5"

# 3b. Preview request creation without executing (dry-run)
jira-as jsm request create 1 10 --summary "Test request" --dry-run

# 4. Check SLA status
jira-as jsm sla get SD-123

# 5. Add a comment to a request (body is positional, before flags)
jira-as jsm request comment SD-123 "Looking into this issue now"

# 6. Add an internal comment (agent-only, not visible to customers)
jira-as jsm request comment SD-123 "Escalating to Tier 2 support" --internal

# 7. Approve a pending request
jira-as jsm approval approve SD-124 --approval-id 1001 --yes

# 8. Preview approval without executing (dry-run)
jira-as jsm approval approve SD-124 --approval-id 1001 --dry-run

# 9. Decline a pending request
jira-as jsm approval decline SD-124 --approval-id 1001 --yes

# 9a. Preview decline without executing (dry-run)
jira-as jsm approval decline SD-124 --approval-id 1001 --dry-run
```

For detailed setup instructions, see [docs/QUICK_START.md](docs/QUICK_START.md).
