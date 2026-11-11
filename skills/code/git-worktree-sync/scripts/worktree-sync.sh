#!/usr/bin/env bash
# worktree-sync.sh — create a git worktree, put every submodule on the same
# branch as the worktree, and copy every .env file (`.env` and `.env.*`, at any
# depth — e.g. .claude/skills/<name>/.env) from the source checkout into it.
# Nothing else is copied. Files already present are never overwritten.
#
# Usage:
#   worktree-sync.sh create -b <branch> [-f <base>] [-p <path>] [--from <dir>]
#                           [--sub-base <branch>] [--detach <ref>]
#                           [--no-submodules] [--dry-run]
#   worktree-sync.sh submodules [--to <worktree>] [--sub-base <branch>] [--branch <name>]
#   worktree-sync.sh copy   [--from <dir>] [--to <worktree>] [--dry-run]
#   worktree-sync.sh list-paths [--from <dir>]
set -euo pipefail

die() { echo "error: $*" >&2; exit 1; }
log() { echo "[worktree-sync] $*" >&2; }

main_worktree() {
  git worktree list --porcelain | awk '/^worktree /{print substr($0,10); exit}'
}

list_env_files() {  # $1 = source root -> prints relative paths of .env files
  ( cd "$1" && find . \
      \( -name .git -o -name node_modules -o -name .venv -o -name __pycache__ -o -name worktrees \) -prune \
      -o \( -type f -o -type l \) \( -name .env -o -name '.env.*' \) -print ) | sed 's|^\./||' | sort
}

copy_files() {  # $1 src root, $2 dst root, $3 dry(0/1)
  local src dst dry=$3 f copied=0 skipped=0
  src=$(cd "$1" && pwd -P); dst=$(cd "$2" && pwd -P)
  [[ $src == "$dst" ]] && die "source and destination are the same: $src"
  while IFS= read -r f; do
    if [[ -e "$dst/$f" || -L "$dst/$f" ]]; then
      skipped=$((skipped+1)); continue
    fi
    if (( dry )); then echo "would copy: $f"
    else
      mkdir -p "$dst/$(dirname "$f")"
      cp -pP "$src/$f" "$dst/$f"
      echo "copied: $f"
    fi
    copied=$((copied+1))
  done < <(list_env_files "$src")
  log "$( ((dry)) && echo 'dry-run: ' )$copied .env file(s) copied, $skipped already present (kept)"
}

# Init submodules, update each one from its base branch (--sub-base, else the
# submodule's origin/HEAD), then create/check out <branch> in every submodule.
sync_submodules() {  # $1 worktree, $2 sub-base ("" = default), $3 branch ("" = worktree branch)
  local wt=$1 sub_base=$2 branch=$3
  [[ -f "$wt/.gitmodules" ]] || { log "no submodules"; return 0; }
  branch=${branch:-$(git -C "$wt" branch --show-current)}
  log "init submodules"
  git -C "$wt" submodule update --init --recursive
  [[ -n $branch ]] || { log "detached worktree — submodules left on their recorded commit"; return 0; }
  log "submodules: base=${sub_base:-<default branch>} -> branch $branch"
  # shellcheck disable=SC2016
  WT_SUB_BASE=$sub_base WT_BRANCH=$branch git -C "$wt" submodule foreach -q --recursive '
    git fetch -q --prune origin || echo "  ! $displaypath: fetch failed" >&2
    def=$(git symbolic-ref -q --short refs/remotes/origin/HEAD | sed "s|^origin/||")
    [ -n "$def" ] || def=main
    base=${WT_SUB_BASE:-$def}
    if [ "$base" != "$def" ] && ! git show-ref -q --verify "refs/remotes/origin/$base"; then
      echo "  ! $displaypath: no origin/$base — using $def" >&2; base=$def
    fi
    { git checkout -q "$base" && git pull -q --ff-only origin "$base"; } || echo "  ! $displaypath: cannot update $base" >&2
    if git show-ref -q --verify "refs/heads/$WT_BRANCH"; then git checkout -q "$WT_BRANCH"
    elif git show-ref -q --verify "refs/remotes/origin/$WT_BRANCH"; then git checkout -q --track -b "$WT_BRANCH" "origin/$WT_BRANCH"
    else git checkout -q -b "$WT_BRANCH"; fi || echo "  ! $displaypath: cannot check out $WT_BRANCH" >&2
    echo "  $displaypath: $(git branch --show-current) (from $base)" >&2
    true
  '
  # every submodule must end on the same branch
  local off
  off=$(WT_BRANCH=$branch git -C "$wt" submodule foreach -q --recursive \
        '[ "$(git branch --show-current)" = "$WT_BRANCH" ] || echo "$displaypath"')
  [[ -z $off ]] || { log "NOT on $branch: $(echo $off)"; return 1; }
  log "all submodules on $branch"
}

cmd_submodules() {
  local to="" sub_base="" branch=""
  while (($#)); do case $1 in
    --to) to=$2; shift 2;;
    --sub-base) sub_base=$2; shift 2;;
    --branch) branch=$2; shift 2;;
    *) die "unknown option: $1";; esac; done
  to=${to:-$(git rev-parse --show-toplevel)}
  sync_submodules "$to" "$sub_base" "$branch"
}

default_base() {
  local b
  b=$(git symbolic-ref -q --short refs/remotes/origin/HEAD 2>/dev/null || true)
  [[ -n $b ]] && { echo "$b"; return; }
  for b in origin/main origin/master main master; do
    git rev-parse -q --verify "$b^{commit}" >/dev/null && { echo "$b"; return; }
  done
  echo HEAD
}

cmd_create() {
  local branch="" base="" path="" from="" detach="" sub_base="" subs=1 dry=0
  while (($#)); do case $1 in
    -b|--branch) branch=$2; shift 2;;
    -f|--base) base=$2; shift 2;;
    -p|--path) path=$2; shift 2;;
    --from) from=$2; shift 2;;
    --detach) detach=$2; shift 2;;
    --sub-base) sub_base=$2; shift 2;;
    --no-submodules) subs=0; shift;;
    --dry-run) dry=1; shift;;
    *) die "unknown option: $1";; esac; done
  [[ -n $branch || -n $detach ]] || die "-b <branch> or --detach <ref> required"

  local root; root=$(git rev-parse --show-toplevel) || die "not in a git repo"
  from=${from:-$(main_worktree)}
  git fetch --prune origin >/dev/null 2>&1 || log "fetch failed (offline?) — continuing"

  local slug=${branch:-detached-${detach//\//-}}; slug=${slug//\//-}
  path=${path:-"$(dirname "$root")/$(basename "$root").worktrees/$slug"}
  [[ -e $path && -n "$(ls -A "$path" 2>/dev/null)" ]] && die "folder not empty: $path"

  local -a add
  if [[ -n $detach ]]; then
    add=(git worktree add --detach "$path" "$detach")
  elif git show-ref -q --verify "refs/heads/$branch"; then
    [[ -n $base ]] && log "branch '$branch' exists — base '$base' ignored"
    add=(git worktree add "$path" "$branch")
  elif git show-ref -q --verify "refs/remotes/origin/$branch"; then
    add=(git worktree add --track -b "$branch" "$path" "origin/$branch")
  else
    base=${base:-$(default_base)}
    add=(git worktree add -b "$branch" "$path" "$base")
  fi

  log "source of .env files: $from"
  log "run: ${add[*]}"
  if (( dry )); then
    log "dry-run: worktree not created, folder: $path"
    list_env_files "$from" | sed 's/^/would copy: /'
    return
  fi
  "${add[@]}"
  path=$(cd "$path" && pwd -P)

  if (( subs )); then   # before the .env copy: submodule folders must be checked out first
    sync_submodules "$path" "$sub_base" "" || log "submodule sync failed — fix it, then: $0 submodules --to $path"
  fi

  copy_files "$from" "$path" 0          # MANDATORY step
  echo
  git -C "$path" status -sb | head -1
  echo "WORKTREE=$path"
}

cmd_copy() {
  local from="" to="" dry=0
  while (($#)); do case $1 in
    --from) from=$2; shift 2;;
    --to) to=$2; shift 2;;
    --dry-run) dry=1; shift;;
    *) die "unknown option: $1";; esac; done
  from=${from:-$(main_worktree)}
  to=${to:-$(git rev-parse --show-toplevel)}
  copy_files "$from" "$to" "$dry"
}

case ${1:-} in
  create) shift; cmd_create "$@";;
  submodules) shift; cmd_submodules "$@";;
  copy) shift; cmd_copy "$@";;
  list-paths) shift; [[ ${1:-} == --from ]] && src=$2 || src=$(main_worktree); list_env_files "$src";;
  *) sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'; exit 1;;
esac
