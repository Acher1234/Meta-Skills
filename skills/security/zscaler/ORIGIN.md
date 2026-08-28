# Origin

Zscaler APIs — ZPA, ZIA, and ZIdentity. First-party skill (no upstream skill tree).

- ZIA API: [Getting started](https://help.zscaler.com/zia/getting-started-zia-api)
- ZPA API: [API authentication](https://help.zscaler.com/zpa/about-api-authentication)
- ZIdentity: [ZIdentity API](https://help.zscaler.com/zidentity/about-zidentity-apis)

Auth:

- ZPA / ZIdentity: OAuth client credentials (`CLIENT_ID` / `CLIENT_SECRET`)
- ZIA: username + password + API key obfuscation

Credentials: nested JSON mapped to `.env` with `__` as the separator (`zpa.client_id` → `ZPA__CLIENT_ID`).
