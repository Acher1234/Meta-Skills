# coolify — Install

Official [`coolify`](https://github.com/coollabsio/coolify-cli) CLI, then the shared venv.

## CLI

Linux / macOS (installs to `/usr/local/bin`, needs `sudo`):

```bash
curl -fsSL https://raw.githubusercontent.com/coollabsio/coolify-cli/main/scripts/install.sh | bash
```

Linux / macOS without `sudo` (installs to `~/.local/bin`):

```bash
curl -fsSL https://raw.githubusercontent.com/coollabsio/coolify-cli/main/scripts/install.sh | bash -s -- --user
```

Homebrew:

```bash
brew install coollabsio/coolify-cli/coolify-cli
```

Windows (PowerShell; prefix with `$env:COOLIFY_USER_INSTALL=1;` to install without admin rights):

```powershell
irm https://raw.githubusercontent.com/coollabsio/coolify-cli/main/scripts/install.ps1 | iex
```

Go:

```bash
go install github.com/coollabsio/coolify-cli/coolify@latest
```

Check:

```bash
coolify version
```

## Shared venv

Bash / zsh:

```bash
~/.meta-skills/install.sh pip init ~/.meta-skills/skills/devops/coolify
```

PowerShell (Windows):

```powershell
& "$HOME/.meta-skills/install.ps1" pip init "$HOME/.meta-skills/skills/devops/coolify"
```
