# Origin

## Pattern B — first-party / API docs (no upstream skill tree)

Dealabs unofficial mobile **REST v2** (Pepper). Same shape as the Android app.

- Base: `https://www.dealabs.com/rest_api/v2/`
- `GET thread/search`
- `GET thread`
- `GET thread/{thread_id}`
- `GET thread/{thread_id}/comments`

Auth: OAuth1 consumer hardcoded in `scripts/dealabs.py`.
