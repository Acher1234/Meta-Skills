# bitwarden-vault-write — Commands

Requires unlocked session. **Confirm** before create / edit / delete.
Source of truth: `$BW get template <name>` (re-verified against CLI).
Pipe: JSON → `bw encode` → create/edit. Types: login=`1` note=`2` card=`3` identity=`4` ssh=`5`.

| Command | Description |
|---------|-------------|
| `bw create item` | Create item from encoded JSON |
| `bw create folder` | Create folder |
| `bw create attachment --file <PATH> --itemid <ITEM_ID>` | Attach file (no JSON) |
| `bw create org-collection --organizationid <ORG_ID>` | Create org collection |
| `bw edit item <ITEM_ID>` | Replace item (`get` → edit → `encode` → `edit`) |
| `bw edit folder <FOLDER_ID>` | Replace folder |
| `bw edit org-collection <COL_ID> --organizationid <ORG_ID>` | Replace org collection |
| `bw edit item-collections <ITEM_ID> --organizationid <ORG_ID>` | Set item collection membership |
| `bw delete item <ITEM_ID>` | Trash (30d) |
| `bw delete item <ITEM_ID> --permanent` | Irreversible |
| `bw delete attachment\|folder\|org-collection <ID>` | Delete other types |
| `bw restore item <ITEM_ID>` | Restore from trash |
| `bw encode` | Base64 stdin JSON |
| `bw move <ITEM_ID> <ORG_ID>` | Move item to org (+ encoded collection ids) |

---

## JSON placeholders (`bw get template` → swap values)

### `item` + `item.login` → `bw create item` (login, `type=1`)

Templates: `item`, `item.login`, `item.login.uri`

```json
{
  "type": 1,
  "name": "<NAME>",
  "favorite": false,
  "reprompt": 0,
  "notes": "<NOTES_OR_null>",
  "folderId": "<FOLDER_ID_OR_null>",
  "fields": [],
  "passwordHistory": [],
  "login": {
    "uris": [{ "uri": "<URL>" }],
    "username": "<USERNAME>",
    "password": "<PASSWORD>",
    "totp": "<TOTP_OR_null>",
    "fido2Credentials": []
  }
}
```

### `item` + `item.securenote` → secure note (`type=2`)

```json
{
  "type": 2,
  "name": "<NAME>",
  "favorite": false,
  "reprompt": 0,
  "notes": "<NOTES>",
  "folderId": "<FOLDER_ID_OR_null>",
  "fields": [],
  "passwordHistory": [],
  "secureNote": { "type": 0 }
}
```

### `item` + `item.card` → card (`type=3`)

```json
{
  "type": 3,
  "name": "<NAME>",
  "favorite": false,
  "reprompt": 0,
  "notes": "<NOTES_OR_null>",
  "folderId": "<FOLDER_ID_OR_null>",
  "fields": [],
  "passwordHistory": [],
  "card": {
    "cardholderName": "<CARDHOLDER>",
    "brand": "<visa|mastercard|amex|…>",
    "number": "<NUMBER>",
    "expMonth": "<MM>",
    "expYear": "<YYYY>",
    "code": "<CVC>"
  }
}
```

### `item` + `item.identity` → identity (`type=4`)

```json
{
  "type": 4,
  "name": "<NAME>",
  "favorite": false,
  "reprompt": 0,
  "notes": "<NOTES_OR_null>",
  "folderId": "<FOLDER_ID_OR_null>",
  "fields": [],
  "passwordHistory": [],
  "identity": {
    "title": "<Mr|Mrs|Ms|Mx|Dr|…>",
    "firstName": "<FIRST>",
    "middleName": "<MIDDLE_OR_null>",
    "lastName": "<LAST>",
    "address1": "<ADDRESS1>",
    "address2": "<ADDRESS2_OR_null>",
    "city": "<CITY>",
    "state": "<STATE>",
    "postalCode": "<ZIP>",
    "country": "<COUNTRY>",
    "company": "<COMPANY_OR_null>",
    "email": "<EMAIL>",
    "phone": "<PHONE>",
    "ssn": "<SSN_OR_null>",
    "username": "<USERNAME_OR_null>",
    "passportNumber": "<PASSPORT_OR_null>",
    "licenseNumber": "<LICENSE_OR_null>"
  }
}
```

### `item.field` → entry in `.fields[]`

```json
{ "type": 0, "name": "<FIELD_NAME>", "value": "<VALUE>" }
```

`type`: `0` text · `1` hidden · `2` boolean.

### `folder` → `bw create folder`

```json
{ "name": "<FOLDER_NAME>" }
```

### `org-collection` → `bw create org-collection --organizationid <ORG_ID>`

Live template includes sample `groups` / `users` slots — keep, replace ids, or use `[]`.

```json
{
  "organizationId": "<ORG_ID>",
  "name": "<COLLECTION_NAME>",
  "externalId": "<EXTERNAL_ID_OR_null>",
  "groups": [
    {
      "id": "<GROUP_ID>",
      "readOnly": false,
      "hidePasswords": false,
      "manage": false
    }
  ],
  "users": [
    {
      "id": "<USER_ID>",
      "readOnly": false,
      "hidePasswords": false,
      "manage": false
    }
  ]
}
```

Minimal (no ACL yet): `"groups": []`, `"users": []`.

### `bw edit item <ITEM_ID>`

Prefer `$BW get item <ITEM_ID>` then patch. Keep `id` / server fields:

```json
{
  "id": "<ITEM_ID>",
  "type": 1,
  "name": "<NAME>",
  "favorite": false,
  "reprompt": 0,
  "notes": "<NOTES_OR_null>",
  "folderId": "<FOLDER_ID_OR_null>",
  "collectionIds": ["<COLLECTION_ID>"],
  "fields": [],
  "passwordHistory": [],
  "login": {
    "uris": [{ "uri": "<URL>" }],
    "username": "<USERNAME>",
    "password": "<PASSWORD>",
    "totp": "<TOTP_OR_null>",
    "fido2Credentials": []
  }
}
```

### `bw edit folder <FOLDER_ID>`

```json
{ "name": "<FOLDER_NAME>" }
```

(`get folder` may also return `id` / `object` — keep them if present.)

### `bw edit org-collection <COL_ID> --organizationid <ORG_ID>`

Same shape as create, plus `id` from `$BW get org-collection <COL_ID> --organizationid <ORG_ID>`:

```json
{
  "id": "<COL_ID>",
  "organizationId": "<ORG_ID>",
  "name": "<COLLECTION_NAME>",
  "externalId": "<EXTERNAL_ID_OR_null>",
  "groups": [
    {
      "id": "<GROUP_ID>",
      "readOnly": false,
      "hidePasswords": false,
      "manage": false
    }
  ],
  "users": [
    {
      "id": "<USER_ID>",
      "readOnly": false,
      "hidePasswords": false,
      "manage": false
    }
  ]
}
```

### `item-collections` → `bw edit item-collections` / `bw move`

Template: `bw get template item-collections`

```json
["<COLLECTION_ID_1>", "<COLLECTION_ID_2>"]
```

```bash
echo '["<COLLECTION_ID>"]' | $BW encode | $BW move <ITEM_ID> <ORG_ID>
echo '["<COLLECTION_ID>"]' | $BW encode | $BW edit item-collections <ITEM_ID> --organizationid <ORG_ID>
```

### No JSON

- `bw create attachment --file <PATH> --itemid <ITEM_ID>`
- `bw delete …` / `bw restore item <ITEM_ID>`

### One-liner

```bash
echo '<JSON>' | $BW encode | $BW create item
$BW get item <ITEM_ID> | jq '…' | $BW encode | $BW edit item <ITEM_ID>
```
