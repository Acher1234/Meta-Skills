#!/usr/bin/env python3
"""Put every submodule of a worktree on the same branch as the worktree.

For each submodule (recursive): init -> check out its base branch and
`pull --ff-only` (--sub-base, else the submodule's origin/HEAD; falls back to it
when missing) -> check out the worktree branch (local or origin/<branch>) or
create it from that base. Exit 1 if any submodule ends on another branch.

Usage: submodules.py [--to <worktree>] [--sub-base <branch>] [--branch <name>]
Stdlib only, Linux / macOS / Windows. Logs on stderr.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def log(msg: str) -> None:
    print(f"[submodules] {msg}", file=sys.stderr, flush=True)


def git(*args: str, cwd: Path | None = None, quiet: bool = False) -> int:
    return subprocess.run(["git", *args], cwd=cwd,
                          stderr=subprocess.DEVNULL if quiet else None).returncode


def out(*args: str, cwd: Path | None = None) -> str:
    res = subprocess.run(["git", *args], cwd=cwd, text=True,
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return res.stdout.strip() if res.returncode == 0 else ""


def ref_exists(ref: str, cwd: Path) -> bool:
    return git("show-ref", "-q", "--verify", ref, cwd=cwd, quiet=True) == 0


def submodule_paths(repo: Path) -> list[Path]:
    if not (repo / ".gitmodules").is_file():
        return []
    raw = out("config", "-f", ".gitmodules", "-z", "--get-regexp", r"^submodule\..*\.path$", cwd=repo)
    paths = []
    for entry in filter(None, raw.split("\0")):
        rel = entry.partition("\n")[2]
        if (repo / rel / ".git").exists():
            paths.append(repo / rel)
    return paths


def sync_one(sub: Path, label: str, sub_base: str, branch: str) -> None:
    if git("fetch", "-q", "--prune", "origin", cwd=sub):
        log(f"  ! {label}: fetch failed")
    default = out("symbolic-ref", "-q", "--short", "refs/remotes/origin/HEAD", cwd=sub)
    default = default.removeprefix("origin/") or "main"
    base = sub_base or default
    if base != default and not ref_exists(f"refs/remotes/origin/{base}", sub):
        log(f"  ! {label}: no origin/{base} — using {default}")
        base = default
    if git("checkout", "-q", base, cwd=sub) or git("pull", "-q", "--ff-only", "origin", base, cwd=sub):
        log(f"  ! {label}: cannot update {base}")
    if ref_exists(f"refs/heads/{branch}", sub):
        args = ["checkout", "-q", branch]
    elif ref_exists(f"refs/remotes/origin/{branch}", sub):
        args = ["checkout", "-q", "--track", "-b", branch, f"origin/{branch}"]
    else:
        args = ["checkout", "-q", "-b", branch]
    if git(*args, cwd=sub):
        log(f"  ! {label}: cannot check out {branch}")
    git("submodule", "update", "-q", "--init", "--recursive", cwd=sub)
    log(f"  {label}: {out('branch', '--show-current', cwd=sub) or '(detached)'} (from {base})")


def walk(repo: Path, root: Path, sub_base: str, branch: str, off: list[str]) -> None:
    for sub in submodule_paths(repo):
        label = sub.relative_to(root).as_posix()
        sync_one(sub, label, sub_base, branch)
        if out("branch", "--show-current", cwd=sub) != branch:
            off.append(label)
        walk(sub, root, sub_base, branch, off)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--to", help="worktree (default: current repo root)")
    p.add_argument("--sub-base", default="", help="base branch of the submodules")
    p.add_argument("--branch", default="", help="target branch (default: the worktree branch)")
    a = p.parse_args()

    wt = Path(a.to or out("rev-parse", "--show-toplevel") or ".").resolve()
    if not (wt / ".gitmodules").is_file():
        log("no submodules")
        return 0
    branch = a.branch or out("branch", "--show-current", cwd=wt)
    log("init submodules")
    git("submodule", "update", "--init", "--recursive", cwd=wt)
    if not branch:
        log("detached worktree — submodules left on their recorded commit")
        return 0
    log(f"base={a.sub_base or '<default branch>'} -> branch {branch}")
    off: list[str] = []
    walk(wt, wt, a.sub_base, branch, off)
    if off:
        log(f"NOT on {branch}: {' '.join(off)}")
        return 1
    log(f"all submodules on {branch}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
