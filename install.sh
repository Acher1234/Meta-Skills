#!/usr/bin/env bash
set -euo pipefail

META_SKILLS_HOME="${META_SKILLS_HOME:-$HOME/.meta-skills}"
EXT_DIR="$META_SKILLS_HOME/ext"
VENV_DIR="$META_SKILLS_HOME/.venv"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMON_PKG="$REPO_ROOT/meta-skill-common"

log() { printf '\033[1;36m[meta-skills]\033[0m %s\n' "$*"; }
err() { printf '\033[1;31m[meta-skills] error:\033[0m %s\n' "$*" >&2; }

# fetch <git-url> [name] — clone ONCE into the shared cache, else pull to update.
fetch_repo() {
  local url="${1:?git url required}" name="${2:-}"
  [ -n "$name" ] || name="$(basename "${url%.git}")"
  local dest="$EXT_DIR/$name"
  mkdir -p "$EXT_DIR"
  if [ -d "$dest/.git" ]; then
    log "Updating '$name' (git pull) in shared cache"
    git -C "$dest" pull --ff-only || log "pull failed for $name (keeping existing copy)"
  else
    log "Cloning '$name' → $dest"
    git clone --depth 1 "$url" "$dest"
  fi
  echo "$dest"
}

# pip init [dir] — ensure the shared venv, install meta-skill-common, then <dir> deps.
pip_init() {
  local dir="${1:-.}"
  if [ ! -x "$VENV_DIR/bin/python" ]; then
    log "Creating shared Python venv at $VENV_DIR"
    python3 -m venv "$VENV_DIR"
    "$VENV_DIR/bin/python" -m pip install --quiet --upgrade pip
  fi
  if [ -d "$COMMON_PKG" ]; then
    log "Installing meta-skill-common (importable as common) into shared venv"
    "$VENV_DIR/bin/pip" install --quiet -e "$COMMON_PKG"
  else
    err "meta-skill-common not found at $COMMON_PKG"
  fi
  if [ -f "$dir/requirements.txt" ]; then
    log "Installing $dir/requirements.txt into shared venv"
    "$VENV_DIR/bin/pip" install -r "$dir/requirements.txt"
  elif [ -f "$dir/pyproject.toml" ] || [ -f "$dir/setup.py" ]; then
    log "Installing $dir (editable) into shared venv"
    "$VENV_DIR/bin/pip" install -e "$dir"
  else
    log "Shared venv ready ($VENV_DIR) — no requirements found in $dir"
  fi
  log "Shared interpreter: $VENV_DIR/bin/python"
}

# npm init [dir] — install <dir>'s node deps (the skill dir is shared).
npm_init() {
  local dir="${1:-.}"
  command -v npm >/dev/null 2>&1 || { err "npm not found on PATH"; return 1; }
  if [ -f "$dir/package.json" ]; then
    log "npm install in $dir (shared skill dir)"
    ( cd "$dir" && npm install )
  else
    err "no package.json in $dir"; return 1
  fi
}

usage() { sed -n '2,/^set -euo pipefail/p' "$0" | sed '$d' | sed 's/^# \{0,1\}//'; }

cmd="${1:-}"; shift || true
case "$cmd" in
  fetch) fetch_repo "$@" ;;
  pip)
    if [ "${1:-}" = init ]; then shift; pip_init "$@"; else err "usage: install.sh pip init [dir]"; exit 2; fi ;;
  npm)
    if [ "${1:-}" = init ]; then shift; npm_init "$@"; else err "usage: install.sh npm init [dir]"; exit 2; fi ;;
  ""|-h|--help|help) usage ;;
  *) err "unknown command: $cmd"; echo; usage; exit 2 ;;
esac
