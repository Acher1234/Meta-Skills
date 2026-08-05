# Hexnode policy platform payloads

Create / edit policy bodies may include platform dictionaries. Official field
references (not separate REST endpoints):

| Platform | Docs |
|----------|------|
| iOS | https://www.hexnode.com/mobile-device-management/developers/policies/ios-policies/ |
| Android | https://www.hexnode.com/mobile-device-management/developers/policies/android-policies/ |
| macOS | https://www.hexnode.com/mobile-device-management/developers/policies/macos-policies/ |
| Windows | https://www.hexnode.com/mobile-device-management/developers/policies/windows-policies/ |

Minimal create example:

```json
{
  "name": "Sales Team Policy",
  "description": "",
  "ios": {
    "password": {
      "allow_simple": true,
      "require_alphanumeric": false,
      "max_failed_attempts": 4,
      "min_length": 1
    }
  }
}
```

Pass the full body with `python scripts/cli.py policies create --file policy.json`
(or `policies edit POLICY_ID --file policy.json`).
