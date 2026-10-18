# Meta-Skills shared env helper (Windows / PowerShell) — same 3 commands as install.sh
#   .\install.ps1 fetch <git-url> [name]   clone/pull → ~/.meta-skills/ext/<name>
#   .\install.ps1 pip init [dir]           shared venv + meta-skill-common + <dir> deps
#   .\install.ps1 npm init [dir]           install <dir> node deps (shared skill dir)
$ErrorActionPreference = "Stop"

$MetaSkillsHome = if ($env:META_SKILLS_HOME) { $env:META_SKILLS_HOME } else { Join-Path $HOME ".meta-skills" }
$ExtDir = Join-Path $MetaSkillsHome "ext"
$VenvDir = Join-Path $MetaSkillsHome ".venv"
$VenvPython = Join-Path $VenvDir "Scripts/python.exe"
$CommonPkg = Join-Path $PSScriptRoot "meta-skill-common"

function Log($msg) { Write-Host "[meta-skills] $msg" -ForegroundColor Cyan }
function Err($msg) { Write-Host "[meta-skills] error: $msg" -ForegroundColor Red }

function Fetch-Repo([string]$Url, [string]$Name) {
  if (-not $Url) { throw "git url required" }
  if (-not $Name) { $Name = [IO.Path]::GetFileNameWithoutExtension($Url.TrimEnd("/")) }
  $dest = Join-Path $ExtDir $Name
  New-Item -ItemType Directory -Force -Path $ExtDir | Out-Null
  if (Test-Path (Join-Path $dest ".git")) {
    Log "Updating '$Name' (git pull) in shared cache"
    git -C $dest pull --ff-only
    if ($LASTEXITCODE -ne 0) { Log "pull failed for $Name (keeping existing copy)" }
  } else {
    Log "Cloning '$Name' -> $dest"
    git clone --depth 1 $Url $dest
  }
  $dest
}

function Pip-Init([string]$Dir = ".") {
  if (-not (Test-Path $VenvPython)) {
    Log "Creating shared Python venv at $VenvDir"
    $py = if (Get-Command py -ErrorAction SilentlyContinue) { "py" } else { "python" }
    & $py -m venv $VenvDir
    & $VenvPython -m pip install --quiet --upgrade pip
  }
  if (Test-Path $CommonPkg) {
    Log "Installing meta-skill-common (importable as common) into shared venv"
    & $VenvPython -m pip install --quiet -e $CommonPkg
  } else {
    Err "meta-skill-common not found at $CommonPkg"
  }
  if (Test-Path (Join-Path $Dir "requirements.txt")) {
    Log "Installing $Dir/requirements.txt into shared venv"
    & $VenvPython -m pip install -r (Join-Path $Dir "requirements.txt")
  } elseif ((Test-Path (Join-Path $Dir "pyproject.toml")) -or (Test-Path (Join-Path $Dir "setup.py"))) {
    Log "Installing $Dir (editable) into shared venv"
    & $VenvPython -m pip install -e $Dir
  } else {
    Log "Shared venv ready ($VenvDir) - no requirements found in $Dir"
  }
  Log "Shared interpreter: $VenvPython"
}

function Npm-Init([string]$Dir = ".") {
  if (-not (Get-Command npm -ErrorAction SilentlyContinue)) { Err "npm not found on PATH"; exit 1 }
  if (-not (Test-Path (Join-Path $Dir "package.json"))) { Err "no package.json in $Dir"; exit 1 }
  Log "npm install in $Dir (shared skill dir)"
  Push-Location $Dir
  try { npm install } finally { Pop-Location }
}

function Usage { Get-Content $PSCommandPath | Select-Object -Skip 1 -First 3 | ForEach-Object { $_ -replace '^# ?', '' } }

$cmd = if ($args.Count -gt 0) { $args[0] } else { "" }
$rest = if ($args.Count -gt 1) { $args[1..($args.Count - 1)] } else { @() }
switch ($cmd) {
  "fetch" { Fetch-Repo @rest }
  "pip" {
    if ($rest.Count -ge 1 -and $rest[0] -eq "init") { Pip-Init @($rest | Select-Object -Skip 1) }
    else { Err "usage: install.ps1 pip init [dir]"; exit 2 }
  }
  "npm" {
    if ($rest.Count -ge 1 -and $rest[0] -eq "init") { Npm-Init @($rest | Select-Object -Skip 1) }
    else { Err "usage: install.ps1 npm init [dir]"; exit 2 }
  }
  { $_ -in "", "-h", "--help", "help" } { Usage }
  default { Err "unknown command: $cmd"; Usage; exit 2 }
}
