# OAuth `--services` → scopes

Used by `python scripts/setup.py --auth-url --services …`.

Comma-separate values. `all` requests every scope below. `email` and `gmail` are aliases.

| Service | OAuth scopes |
|---------|--------------|
| `email` / `gmail` | `gmail.readonly`, `gmail.send`, `gmail.modify` |
| `calendar` | `calendar` |
| `drive` | `drive` |
| `contacts` | `contacts.readonly` |
| `sheets` | `spreadsheets` |
| `docs` | `documents` |
| `chat` | `chat.spaces`, `chat.messages` |
| `all` | all of the above |

Full scope URLs (prefix `https://www.googleapis.com/auth/`):

```
email/gmail → gmail.readonly gmail.send gmail.modify
calendar    → calendar
drive       → drive
contacts    → contacts.readonly
sheets      → spreadsheets
docs        → documents
chat        → chat.spaces chat.messages
```

Examples:

```bash
python scripts/setup.py --auth-url --services all
python scripts/setup.py --auth-url --services email,calendar
python scripts/setup.py --auth-url --services drive,sheets,docs
python scripts/setup.py --auth-url --services chat
```
