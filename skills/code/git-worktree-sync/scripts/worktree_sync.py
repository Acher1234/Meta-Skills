#!/usr/bin/env python3
"""Create a git worktree, put every submodule on the worktree branch, copy .env files.

Cross-platform (Linux / macOS / Windows), stdlib only.

Commands:
  create      -b <branch> [-f <base>] [-p <path>] [--from <dir>] [--sub-base <b>]
              [--detach <ref>] [--no-submodules] [--dry-run]
  submodules  [--to <worktree>] [--sub-base <b>] [--branch <name>]
  copy        [--from <dir>] [--to <worktree>] [--dry-run]
  list-paths  [--from <dir>]

Only `.env` / `.env.*` files (any depth) are copied, never overwriting.
Logs go to stderr; the last stdout line of `create` is `WORKTREE=<path>`.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

PRUNE = {".git", "node_modules", ".venv", "__pycache__", "worktrees"}


def log(msg: str) -> None:
    print(f"[worktree-sync] {msg}", file=sys.stderr, flush=True)


def die(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def git(*args: str, cwd: str | Path | None = None, check: bool = True,
        quiet: bool = False) -> subprocess.CompletedProcess:
    res = subprocess.run(["git", *args], cwd=cwd, text=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL if quiet else None)
    if check and res.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed ({res.returncode})")
    return res


def out(*args: str, cwd: str | Path | None = None) -> str:
    res = git(*args, cwd=cwd, check=False, quiet=True)
    return res.stdout.strip() if res.returncode == 0 else ""


def ref_exists(ref: str, cwd: str | Path | None = None) -> bool:
    return git("show-ref", "-q", "--verify", ref, cwd=cwd, check=False, quiet=True).returncode == 0


def toplevel(cwd: str | Path | None = None) -> Path:
    top = out("rev-parse", "--show-toplevel", cwd=cwd)
    if not top:
        die("not in a git repo")
    return Path(top)


def main_worktree() -> Path:
    for line in out("worktree", "list", "--porcelain").splitlines():
        if line.startswith("worktree "):
            return Path(line[len("worktree "):])
    return toplevel()


# ---------- .env copy ----------

def list_env_files(src: Path) -> list[str]:
    found: list[str] = []
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in PRUNE]
        for name in files + [d for d in dirs if os.path.islink(os.path.join(root, d))]:
            if name == ".env" or name.startswith(".env."):
                found.append(Path(root, name).relative_to(src).as_posix())
    return sorted(found)


def copy_env(src: Path, dst: Path, dry: bool) -> None:
    src, dst = src.resolve(), dst.resolve()
    if src == dst:
        die(f"source and destination are the same: {src}")
    copied = skipped = 0
    for rel in list_env_files(src):
        target = dst / rel
        if target.exists() or target.is_symlink():
            skipped += 1
            continue
        copied += 1
        if dry:
            print(f"would copy: {rel}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src / rel, target, follow_symlinks=False)
        print(f"copied: {rel}")
    log(f"{'dry-run: ' if dry else ''}{copied} .env file(s) copied, {skipped} already present (kept)")


# ---------- submodules ----------

def submodule_paths(repo: Path) -> list[Path]:
    if not (repo / ".gitmodules").is_file():
        return []
    raw = out("config", "-f", ".gitmodules", "-z", "--get-regexp", r"^submodule\..*\.path$", cwd=repo)
    paths = []
    for entry in filter(None, raw.split("\0")):
        _, _, rel = entry.partition("\n")
        if (repo / rel / ".git").exists():
            paths.append(repo / rel)
    return paths


def sync_one(sub: Path, label: str, sub_base: str, branch: str) -> None:
    if git("fetch", "-q", "--prune", "origin", cwd=sub, check=False).returncode:
        log(f"  ! {label}: fetch failed")
    default = out("symbolic-ref", "-q", "--short", "refs/remotes/origin/HEAD", cwd=sub)
    default = default.removeprefix("origin/") or "main"
    base = sub_base or default
    if base != default and not ref_exists(f"refs/remotes/origin/{base}", sub):
        log(f"  ! {label}: no origin/{base} — using {default}")
        base = default
    ok = git("checkout", "-q", base, cwd=sub, check=False).returncode == 0
    ok = ok and git("pull", "-q", "--ff-only", "origin", base, cwd=sub, check=False).returncode == 0
    if not ok:
        log(f"  ! {label}: cannot update {base}")
    if ref_exists(f"refs/heads/{branch}", sub):
        args = ["checkout", "-q", branch]
    elif ref_exists(f"refs/remotes/origin/{branch}", sub):
        args = ["checkout", "-q", "--track", "-b", branch, f"origin/{branch}"]
    else:
        args = ["checkout", "-q", "-b", branch]
    if git(*args, cwd=sub, check=False).returncode:
        log(f"  ! {label}: cannot check out {branch}")
    git("submodule", "update", "-q", "--init", "--recursive", cwd=sub, check=False)
    log(f"  {label}: {out('branch', '--show-current', cwd=sub) or '(detached)'} (from {base})")


def walk_submodules(repo: Path, root: Path, sub_base: str, branch: str, off: list[str]) -> None:
    for sub in submodule_paths(repo):
        label = sub.relative_to(root).as_posix()
        sync_one(sub, label, sub_base, branch)
        if out("branch", "--show-current", cwd=sub) != branch:
            off.append(label)
        walk_submodules(sub, root, sub_base, branch, off)


def sync_submodules(wt: Path, sub_base: str = "", branch: str = "") -> bool:
    if not (wt / ".gitmodules").is_file():
        log("no submodules")
        return True
    branch = branch or out("branch", "--show-current", cwd=wt)
    log("init submodules")
    git("submodule", "update", "--init", "--recursive", cwd=wt, check=False)
    if not branch:
        log("detached worktree — submodules left on their recorded commit")
        return True
    log(f"submodules: base={sub_base or '<default branch>'} -> branch {branch}")
    off: list[str] = []
    walk_submodules(wt, wt, sub_base, branch, off)
    if off:
        log(f"NOT on {branch}: {' '.join(off)}")
        return False
    log(f"all submodules on {branch}")
    return True


# ---------- commands ----------

def default_base() -> str:
    b = out("symbolic-ref", "-q", "--short", "refs/remotes/origin/HEAD")
    if b:
        return b
    for cand in ("origin/main", "origin/master", "main", "master"):
        if out("rev-parse", "-q", "--verify", f"{cand}^{{commit}}"):
            return cand
    return "HEAD"


def cmd_create(a: argparse.Namespace) -> int:
    if not a.branch and not a.detach:
        die("-b <branch> or --detach <ref> required")
    root = toplevel()
    src = Path(a.src) if a.src else main_worktree()
    if git("fetch", "--prune", "origin", check=False, quiet=True).returncode:
        log("fetch failed (offline?) — continuing")

    slug = (a.branch or f"detached-{a.detach}").replace("/", "-")
    path = Path(a.path) if a.path else root.parent / f"{root.name}.worktrees" / slug
    if path.exists() and any(path.iterdir()):
        die(f"folder not empty: {path}")

    if a.detach:
        cmd = ["worktree", "add", "--detach", str(path), a.detach]
    elif ref_exists(f"refs/heads/{a.branch}"):
        if a.base:
            log(f"branch '{a.branch}' exists — base '{a.base}' ignored")
        cmd = ["worktree", "add", str(path), a.branch]
    elif ref_exists(f"refs/remotes/origin/{a.branch}"):
        cmd = ["worktree", "add", "--track", "-b", a.branch, str(path), f"origin/{a.branch}"]
    else:
        cmd = ["worktree", "add", "-b", a.branch, str(path), a.base or default_base()]

    log(f"source of .env files: {src}")
    log("run: git " + " ".join(cmd))
    if a.dry_run:
        log(f"dry-run: worktree not created, folder: {path}")
        for rel in list_env_files(src):
            print(f"would copy (if missing): {rel}")
        return 0
    git(*cmd)
    path = path.resolve()

    # before the .env copy: submodule folders must be checked out first
    if not a.no_submodules and not sync_submodules(path, a.sub_base or ""):
        log(f"submodule sync failed — fix it, then: worktree_sync.py submodules --to {path}")
    copy_env(src, path, False)  # MANDATORY step
    print(f"\nWORKTREE={path}")
    return 0


def cmd_submodules(a: argparse.Namespace) -> int:
    to = Path(a.to) if a.to else toplevel()
    return 0 if sync_submodules(to, a.sub_base or "", a.branch or "") else 1


def cmd_copy(a: argparse.Namespace) -> int:
    copy_env(Path(a.src) if a.src else main_worktree(), Path(a.to) if a.to else toplevel(), a.dry_run)
    return 0


def cmd_list(a: argparse.Namespace) -> int:
    print("\n".join(list_env_files(Path(a.src) if a.src else main_worktree())))
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)

    c = sp.add_parser("create", help="create worktree + submodules + .env copy")
    c.add_argument("-b", "--branch")
    c.add_argument("-f", "--base")
    c.add_argument("-p", "--path")
    c.add_argument("--from", dest="src")
    c.add_argument("--sub-base")
    c.add_argument("--detach")
    c.add_argument("--no-submodules", action="store_true")
    c.add_argument("--dry-run", action="store_true")
    c.set_defaults(func=cmd_create)

    s = sp.add_parser("submodules", help="pull each submodule from its base, then same branch everywhere")
    s.add_argument("--to")
    s.add_argument("--sub-base")
    s.add_argument("--branch")
    s.set_defaults(func=cmd_submodules)

    k = sp.add_parser("copy", help="copy .env files into an existing worktree")
    k.add_argument("--from", dest="src")
    k.add_argument("--to")
    k.add_argument("--dry-run", action="store_true")
    k.set_defaults(func=cmd_copy)

    lp = sp.add_parser("list-paths", help="list the .env files that would be copied")
    lp.add_argument("--from", dest="src")
    lp.set_defaults(func=cmd_list)

    a = p.parse_args()
    try:
        return a.func(a)
    except RuntimeError as e:
        die(str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
