# Origin

Bitwarden Password Manager **CLI** (`bw`) — vault read/write and Send, wrapped by a
Python CLI so the agent gets JSON output and secrets stay masked by default.

- CLI reference: [bitwarden.com/help/cli](https://bitwarden.com/help/cli/)
- Auth via API key: [bitwarden.com/help/cli-auth-challenges](https://bitwarden.com/help/cli-auth-challenges/)
- Personal API key: [bitwarden.com/help/personal-api-key](https://bitwarden.com/help/personal-api-key/)
- Send from CLI: [bitwarden.com/help/send-cli](https://bitwarden.com/help/send-cli/)
- npm package: [@bitwarden/cli](https://www.npmjs.com/package/@bitwarden/cli)

Binary: `@bitwarden/cli` pinned in `package.json`, installed into the shared library
skill dir by `install.sh npm init` (`node_modules/.bin/bw`), with a fallback to `bw`
on `PATH`.

`package-lock.json` is committed: it pins the ~200 transitive packages by sha512, so
every machine runs the audited tree. The flip side is that `npm install` will not move
past the locked release on its own — upstream security fixes need a deliberate bump:

```bash
cd ~/.meta-skills/skills/security/bitwarden
npm update @bitwarden/cli && ./node_modules/.bin/bw --version   # commit the new lock
```

Auth: `bw login --apikey` reads `BW_CLIENTID` / `BW_CLIENTSECRET`. Vault data then
requires a session key from `bw unlock`, which always asks for the master password.
