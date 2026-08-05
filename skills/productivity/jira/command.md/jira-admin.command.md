# jira-admin — Commands

All commands support `--help` for full options.

### Project Management

| Command | Description |
|---------|-------------|
| `jira-as admin project list` | List all projects |
| `jira-as admin project get` | Get project details |
| `jira-as admin project create` | Create a new project |
| `jira-as admin project update` | Update project settings |
| `jira-as admin project delete` | Delete a project |
| `jira-as admin project archive` | Archive a project |
| `jira-as admin project restore` | Restore archived project |
| `jira-as admin config get` | Get project configuration |
| `jira-as admin category list` | List project categories |
| `jira-as admin category create` | Create a category |
| `jira-as admin category assign` | Assign category to project |

### Automation Rules

| Command | Description |
|---------|-------------|
| `jira-as admin automation list` | List automation rules |
| `jira-as admin automation get` | Get rule details |
| `jira-as admin automation search` | Search automation rules |
| `jira-as admin automation enable` | Enable a rule |
| `jira-as admin automation disable` | Disable a rule |
| `jira-as admin automation toggle` | Toggle rule enabled state |
| `jira-as admin automation invoke` | Invoke manual rule |
| `jira-as admin automation-template list` | List rule templates |
| `jira-as admin automation-template get` | Get template details |

### Permission Schemes

| Command | Description |
|---------|-------------|
| `jira-as admin permission-scheme list` | List permission schemes |
| `jira-as admin permission-scheme get` | Get scheme details |
| `jira-as admin permission-scheme create` | Create new scheme |
| `jira-as admin permission-scheme assign` | Assign scheme to project |
| `jira-as admin permission list` | List available permissions |

### Permission Diagnostics

| Command | Description |
|---------|-------------|
| `jira-as admin permission check` | Check permissions on a project |

### User and Group Management

| Command | Description |
|---------|-------------|
| `jira-as admin user search` | Search for users by name or email |
| `jira-as admin user get` | Get user details |
| `jira-as admin group list` | List all groups |
| `jira-as admin group members` | Get group members |
| `jira-as admin group create` | Create a group |
| `jira-as admin group delete` | Delete a group |
| `jira-as admin group add-user` | Add user to group |
| `jira-as admin group remove-user` | Remove user from group |

### Notification Schemes

| Command | Description |
|---------|-------------|
| `jira-as admin notification-scheme list` | List notification schemes |
| `jira-as admin notification-scheme get` | Get scheme details |
| `jira-as admin notification-scheme create` | Create new scheme |
| `jira-as admin notification add` | Add notification to scheme |
| `jira-as admin notification remove` | Remove notification |

### Screen Management

| Command | Description |
|---------|-------------|
| `jira-as admin screen list` | List screens |
| `jira-as admin screen get` | Get screen details |
| `jira-as admin screen tabs` | List screen tabs |
| `jira-as admin screen fields` | Get fields on screen |
| `jira-as admin screen add-field` | Add field to screen |
| `jira-as admin screen remove-field` | Remove field from screen |
| `jira-as admin screen-scheme list` | List screen schemes |
| `jira-as admin screen-scheme get` | Get screen scheme details |

### Issue Types

| Command | Description |
|---------|-------------|
| `jira-as admin issue-type list` | List issue types |
| `jira-as admin issue-type get` | Get issue type details |
| `jira-as admin issue-type create` | Create issue type |
| `jira-as admin issue-type update` | Update issue type |
| `jira-as admin issue-type delete` | Delete issue type |

### Issue Type Schemes

| Command | Description |
|---------|-------------|
| `jira-as admin issue-type-scheme list` | List schemes |
| `jira-as admin issue-type-scheme get` | Get scheme details |
| `jira-as admin issue-type-scheme create` | Create new scheme |
| `jira-as admin issue-type-scheme assign` | Assign to project |
| `jira-as admin issue-type-scheme project` | Get project's scheme |

### Workflow Management

| Command | Description |
|---------|-------------|
| `jira-as admin workflow list` | List workflows |
| `jira-as admin workflow get` | Get workflow details |
| `jira-as admin workflow search` | Search workflows |
| `jira-as admin workflow for-issue` | Get workflow for specific issue |
| `jira-as admin workflow-scheme list` | List workflow schemes |
| `jira-as admin workflow-scheme get` | Get scheme details |
| `jira-as admin workflow-scheme assign` | Assign to project |
| `jira-as admin status list` | List all statuses |

---
