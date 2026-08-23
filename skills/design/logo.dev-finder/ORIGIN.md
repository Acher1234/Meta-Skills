# Origin

## Pattern B — first-party / API docs (no upstream skill tree)

logo.dev Search API — company name or domain to logo images.

- REST search: [API reference](https://www.logo.dev/docs/api-reference/introduction)
- Keys: [API keys](https://www.logo.dev/docs/platform/api-keys)

Base URL: `https://api.logo.dev`  
Auth: `Authorization: Bearer ${API_KEY}` (secret `sk_…`)

Image download uses each hit’s `logo_url` (`https://img.logo.dev/{domain}?token=…`).
