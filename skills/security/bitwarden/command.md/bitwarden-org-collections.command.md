# bitwarden-org-collections — Commands

Org collection administration via **`bw` CLI** (Vaultwarden / self-hosted).

Requires unlocked session (see SKILL.md connect: `skill_env.py` then `bw unlock`).
Do **not** invent flags — copy a block below, fill placeholders, run it.

---

## Rules (read first)

| Topic | Rule |
| ----- | ---- |
| Hierarchy | No `parentId`. Path is in **name**: `VO2-IT/test`, `Vo2-Canada/Medfar`. |
| Read ACL | `bw get org-collection <id> --organizationid <ORG_ID>` — **not** `bw get collection` (→ Not found). |
| Create + users | `bw create org-collection` **ignores** `users[]` (only `groups[]` are sent). Always **create → edit → get** for user ACL. |
| Public API | Do **not** use `/public/members` or `client_credentials` on Vaultwarden self-hosted for ACL. |
| Member id | Use `id` from `bw list org-members` (org-member uuid), not email. |
| Admin | `manage: true`, `readOnly: false`, `hidePasswords: false` |
| Read-only | `manage: false`, `readOnly: true` |
| Hide passwords | `hidePasswords: true` |

---

## Resolve org id

```bash
bw list organizations | jq '.[] | {id, name}'
```

---

## List org-collections

All collections for one org:

```bash
ORG_ID="<ORG_ID>"
bw list org-collections --organizationid "$ORG_ID"
```

### Root collections (1st depth — no `/` in name)

```bash
ORG_ID="<ORG_ID>"
bw list org-collections --organizationid "$ORG_ID" \
  | jq '[.[] | select(.name | contains("/") | not)] | sort_by(.name) | .[] | {id, name}'
```

### Direct children of a parent (e.g. `VO2-IT/*` only one level deep)

```bash
ORG_ID="<ORG_ID>"
PARENT="VO2-IT"
bw list org-collections --organizationid "$ORG_ID" \
  | jq --arg p "$PARENT" '[.[] | select(.name | startswith($p + "/")) | select(.name | split("/") | length == 2)] | sort_by(.name) | .[] | {id, name}'
```

### All descendants under a parent prefix

```bash
ORG_ID="<ORG_ID>"
PARENT="VO2-IT"
bw list org-collections --organizationid "$ORG_ID" \
  | jq --arg p "$PARENT" '[.[] | select(.name | startswith($p + "/"))] | sort_by(.name) | .[] | {id, name}'
```

---

## Find org-member by email

```bash
ORG_ID="<ORG_ID>"
EMAIL="samuel.abettan@vo2-group.com"
bw list org-members --organizationid "$ORG_ID" \
  | jq --arg e "$EMAIL" '.[] | select(.email == $e) | {id, email, type, status}'
```

Save `id` as `USER_ID` for ACL blocks below.

---

## Get one org-collection (with ACL)

```bash
ORG_ID="<ORG_ID>"
COL_ID="<COL_ID>"
bw get org-collection "$COL_ID" --organizationid "$ORG_ID"
```

---

## Create org-collection (name only — no user ACL)

Sub-collection under parent: set `name` to `Parent/Child`.

```bash
ORG_ID="<ORG_ID>"
COL_NAME="VO2-IT/test"
echo "{\"organizationId\":\"$ORG_ID\",\"name\":\"$COL_NAME\",\"externalId\":null,\"groups\":[],\"users\":[]}" \
  | bw encode | bw create org-collection --organizationid "$ORG_ID"
```

Capture `id` from JSON response → `COL_ID`.

---

## Assign user ACL (required after create if users needed)

```bash
ORG_ID="<ORG_ID>"
COL_ID="<COL_ID>"
COL_NAME="VO2-IT/test"
USER_ID="<ORG_MEMBER_ID>"

echo "{\"id\":\"$COL_ID\",\"organizationId\":\"$ORG_ID\",\"name\":\"$COL_NAME\",\"externalId\":null,\"groups\":[],\"users\":[{\"id\":\"$USER_ID\",\"readOnly\":false,\"hidePasswords\":false,\"manage\":true}]}" \
  | bw encode | bw edit org-collection "$COL_ID" --organizationid "$ORG_ID"
```

Verify (do not trust create/edit response for `users`):

```bash
bw get org-collection "$COL_ID" --organizationid "$ORG_ID"
```

---

## Create sub-collection + assign user as admin (full workflow)

```bash
ORG_ID="<ORG_ID>"
PARENT="VO2-IT"
CHILD="test"
COL_NAME="${PARENT}/${CHILD}"
EMAIL="samuel.abettan@vo2-group.com"

USER_ID=$(bw list org-members --organizationid "$ORG_ID" \
  | jq -r --arg e "$EMAIL" '.[] | select(.email == $e) | .id')

COL_ID=$(echo "{\"organizationId\":\"$ORG_ID\",\"name\":\"$COL_NAME\",\"externalId\":null,\"groups\":[],\"users\":[]}" \
  | bw encode | bw create org-collection --organizationid "$ORG_ID" | jq -r .id)

echo "{\"id\":\"$COL_ID\",\"organizationId\":\"$ORG_ID\",\"name\":\"$COL_NAME\",\"externalId\":null,\"groups\":[],\"users\":[{\"id\":\"$USER_ID\",\"readOnly\":false,\"hidePasswords\":false,\"manage\":true}]}" \
  | bw encode | bw edit org-collection "$COL_ID" --organizationid "$ORG_ID"

bw get org-collection "$COL_ID" --organizationid "$ORG_ID"
```

---

## Assign group ACL on org-collection

```bash
ORG_ID="<ORG_ID>"
COL_ID="<COL_ID>"
COL_NAME="VO2-IT/test"
GROUP_ID="<GROUP_ID>"

echo "{\"id\":\"$COL_ID\",\"organizationId\":\"$ORG_ID\",\"name\":\"$COL_NAME\",\"externalId\":null,\"groups\":[{\"id\":\"$GROUP_ID\",\"readOnly\":false,\"hidePasswords\":false,\"manage\":false}],\"users\":[]}" \
  | bw encode | bw edit org-collection "$COL_ID" --organizationid "$ORG_ID"
```

Groups can be set on **create** or **edit** (unlike `users` on create).

---

## Edit org-collection name

```bash
ORG_ID="<ORG_ID>"
COL_ID="<COL_ID>"
NEW_NAME="VO2-IT/test-renamed"

# Preserve ACL from get → change name only
bw get org-collection "$COL_ID" --organizationid "$ORG_ID" \
  | jq --arg n "$NEW_NAME" '.name = $n' \
  | bw encode | bw edit org-collection "$COL_ID" --organizationid "$ORG_ID"
```

---

## Delete org-collection

```bash
ORG_ID="<ORG_ID>"
COL_ID="<COL_ID>"
bw delete org-collection "$COL_ID" --organizationid "$ORG_ID"
```

Confirm with the user before delete.

---

## Template reference

```bash
bw get template org-collection
```

Fields: `organizationId`, `name`, `externalId`, `groups[]`, `users[]` — each ACL entry: `id`, `readOnly`, `hidePasswords`, `manage`.
