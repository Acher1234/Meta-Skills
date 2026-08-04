# jira-jsm — Commands

All commands support `--help` for full options.

### Service Desk Core

| Command | Description |
|---------|-------------|
| `jira-as jsm service-desk create` | Create new service desk |
| `jira-as jsm service-desk list` | List all service desks |
| `jira-as jsm service-desk get` | Get service desk details |
| `jira-as jsm request-type list` | List available request types |
| `jira-as jsm request-type get` | Get request type details |
| `jira-as jsm request-type fields` | Get custom fields for request type |

### Request Management

| Command | Description |
|---------|-------------|
| `jira-as jsm request create` | Create service request |
| `jira-as jsm request get` | Get request details |
| `jira-as jsm request status` | Get request status/lifecycle |
| `jira-as jsm request transition` | Transition request through workflow |
| `jira-as jsm request list` | List requests with filtering |

### Customer Management

| Command | Description |
|---------|-------------|
| `jira-as jsm customer create` | Create new customer |
| `jira-as jsm customer list` | List service desk customers |
| `jira-as jsm customer add` | Add customer to service desk |
| `jira-as jsm customer remove` | Remove customer from service desk |
| `jira-as jsm request add-participant` | Add participant to request |
| `jira-as jsm request remove-participant` | Remove participant from request |
| `jira-as jsm request participants` | List request participants |

### Organization Management

| Command | Description |
|---------|-------------|
| `jira-as jsm organization create` | Create customer organization |
| `jira-as jsm organization list` | List all organizations |
| `jira-as jsm organization get` | Get organization details |
| `jira-as jsm organization delete` | Delete organization |
| `jira-as jsm organization add-customer` | Add customer to organization |
| `jira-as jsm organization remove-customer` | Remove customer from organization |

### SLA and Queue Management

| Command | Description |
|---------|-------------|
| `jira-as jsm sla get` | Get SLA information for request |
| `jira-as jsm sla check-breach` | Check for SLA breaches |
| `jira-as jsm sla report` | Generate SLA compliance report |
| `jira-as jsm queue list` | List service desk queues |
| `jira-as jsm queue get` | Get queue details |
| `jira-as jsm queue issues` | Get requests in queue |

### Comments and Approvals

| Command | Description |
|---------|-------------|
| `jira-as jsm request comment` | Add comment to request |
| `jira-as jsm request comments` | Get request comments |
| `jira-as jsm approval list` | Get approval status for request |
| `jira-as jsm approval pending` | List pending approvals |
| `jira-as jsm approval approve` | Approve request |
| `jira-as jsm approval decline` | Decline request |

### Knowledge Base and Assets

| Command | Description |
|---------|-------------|
| `jira-as jsm kb search` | Search knowledge base articles |
| `jira-as jsm kb get` | Get knowledge base article |
| `jira-as jsm kb suggest` | Get KB article suggestions for request |
| `jira-as jsm asset create` | Create new asset |
| `jira-as jsm asset list` | List assets |
| `jira-as jsm asset get` | Get asset details |
| `jira-as jsm asset update` | Update asset attributes |
| `jira-as jsm asset link` | Link asset to request |
| `jira-as jsm asset find-affected` | Find assets affected by request |

---
