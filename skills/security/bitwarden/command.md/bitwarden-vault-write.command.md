# bitwarden-vault-write — Commands

Requires unlocked session. **Confirm** before create / edit / delete.
Do **not** invent flags or look up `bw --help` — copy a block below, fill placeholders, run it.
`create` / `edit` / `move` always need `bw encode` (base64). Types: login=`1` note=`2` card=`3` identity=`4` ssh=`5`.

Optional field in any item JSON `.fields[]`:
`{"type":0,"name":"<FIELD_NAME>","value":"<VALUE>"}` — `0` text · `1` hidden · `2` boolean.

---

## Create login (`type=1`)

```bash
echo '{"type":1,"name":"<NAME>","favorite":false,"reprompt":0,"notes":"<NOTES_OR_null>","folderId":"<FOLDER_ID_OR_null>","fields":[],"passwordHistory":[],"login":{"uris":[{"uri":"<URL>"}],"username":"<USERNAME>","password":"<PASSWORD>","totp":"<TOTP_OR_null>","fido2Credentials":[]}}' | bw encode | bw create item
```

## Create secure note (`type=2`)

```bash
echo '{"type":2,"name":"<NAME>","favorite":false,"reprompt":0,"notes":"<NOTES>","folderId":"<FOLDER_ID_OR_null>","fields":[],"passwordHistory":[],"secureNote":{"type":0}}' | bw encode | bw create item
```

## Create card (`type=3`)

```bash
echo '{"type":3,"name":"<NAME>","favorite":false,"reprompt":0,"notes":"<NOTES_OR_null>","folderId":"<FOLDER_ID_OR_null>","fields":[],"passwordHistory":[],"card":{"cardholderName":"<CARDHOLDER>","brand":"<visa|mastercard|amex>","number":"<NUMBER>","expMonth":"<MM>","expYear":"<YYYY>","code":"<CVC>"}}' | bw encode | bw create item
```

## Create identity (`type=4`)

```bash
echo '{"type":4,"name":"<NAME>","favorite":false,"reprompt":0,"notes":"<NOTES_OR_null>","folderId":"<FOLDER_ID_OR_null>","fields":[],"passwordHistory":[],"identity":{"title":"<Mr|Mrs|Ms|Mx|Dr>","firstName":"<FIRST>","middleName":"<MIDDLE_OR_null>","lastName":"<LAST>","address1":"<ADDRESS1>","address2":"<ADDRESS2_OR_null>","city":"<CITY>","state":"<STATE>","postalCode":"<ZIP>","country":"<COUNTRY>","company":"<COMPANY_OR_null>","email":"<EMAIL>","phone":"<PHONE>","ssn":"<SSN_OR_null>","username":"<USERNAME_OR_null>","passportNumber":"<PASSPORT_OR_null>","licenseNumber":"<LICENSE_OR_null>"}}' | bw encode | bw create item
```

## Create folder

```bash
echo '{"name":"<FOLDER_NAME>"}' | bw encode | bw create folder
```

## Create org-collection

Minimal ACL: empty `groups` / `users` arrays. Or keep slots and replace ids.

```bash
echo '{"organizationId":"<ORG_ID>","name":"<COLLECTION_NAME>","externalId":null,"groups":[],"users":[]}' | bw encode | bw create org-collection --organizationid <ORG_ID>
```

With ACL slots:

```bash
echo '{"organizationId":"<ORG_ID>","name":"<COLLECTION_NAME>","externalId":null,"groups":[{"id":"<GROUP_ID>","readOnly":false,"hidePasswords":false,"manage":false}],"users":[{"id":"<USER_ID>","readOnly":false,"hidePasswords":false,"manage":false}]}' | bw encode | bw create org-collection --organizationid <ORG_ID>
```

## Create attachment (no encode)

```bash
bw create attachment --file <PATH> --itemid <ITEM_ID>
```

---

## Edit login item

Prefer get → patch → encode → edit. Keep `id` and server fields from `get`.

```bash
bw get item <ITEM_ID> | jq '.name="<NAME>" | .notes="<NOTES_OR_null>" | .folderId="<FOLDER_ID_OR_null>" | .login.username="<USERNAME>" | .login.password="<PASSWORD>" | .login.uris=[{"uri":"<URL>"}] | .login.totp="<TOTP_OR_null>"' | bw encode | bw edit item <ITEM_ID>
```

Or full replace (must include `id`):

```bash
echo '{"id":"<ITEM_ID>","type":1,"name":"<NAME>","favorite":false,"reprompt":0,"notes":"<NOTES_OR_null>","folderId":"<FOLDER_ID_OR_null>","collectionIds":["<COLLECTION_ID>"],"fields":[],"passwordHistory":[],"login":{"uris":[{"uri":"<URL>"}],"username":"<USERNAME>","password":"<PASSWORD>","totp":"<TOTP_OR_null>","fido2Credentials":[]}}' | bw encode | bw edit item <ITEM_ID>
```

## Edit folder

```bash
echo '{"name":"<FOLDER_NAME>"}' | bw encode | bw edit folder <FOLDER_ID>
```

## Edit org-collection

```bash
echo '{"id":"<COL_ID>","organizationId":"<ORG_ID>","name":"<COLLECTION_NAME>","externalId":null,"groups":[],"users":[]}' | bw encode | bw edit org-collection <COL_ID> --organizationid <ORG_ID>
```

## Edit item collections

```bash
echo '["<COLLECTION_ID_1>","<COLLECTION_ID_2>"]' | bw encode | bw edit item-collections <ITEM_ID> --organizationid <ORG_ID>
```

## Move item to org

```bash
echo '["<COLLECTION_ID>"]' | bw encode | bw move <ITEM_ID> <ORG_ID>
```

---

## Delete / restore (no encode)

```bash
bw delete item <ITEM_ID>
bw delete item <ITEM_ID> --permanent
bw restore item <ITEM_ID>
bw delete folder <FOLDER_ID>
bw delete attachment <ATTACHMENT_ID> --itemid <ITEM_ID>
bw delete org-collection <COL_ID> --organizationid <ORG_ID>
```
