#!/usr/bin/env python3
"""Copy .env files (and user-defined extra items) from one checkout to another.

Does NOT create worktrees. Copies every `.env` / `.env.*` file (any depth) plus
the paths / globs of SYNC_EXTRA (skill `.env`) and `--extra`, keeping relative
paths. Files already present in the target are never overwritten.

Commands:
  copy        [--from <dir>] [--to <dir>] [--extra <path-or-glob>]... [--dry-run]
  list-paths  [--from <dir>] [--extra <path-or-glob>]...

--from defaults to the main worktree, --to to the current repo root.
Linux / macOS / Windows. Logs on stderr.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from skill_env import ENV

PRUNE = {".git", "node_modules", ".venv", "__pycache__", "worktrees"}


def log(msg: str) -> None:
    print(f"[worktree-sync] {msg}", file=sys.stderr, flush=True)


def die(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def out(*args: str) -> str:
    res = subprocess.run(["git", *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return res.stdout.strip() if res.returncode == 0 else ""


def main_worktree() -> Path:
    for line in out("worktree", "list", "--porcelain").splitlines():
        if line.startswith("worktree "):
            return Path(line[len("worktree "):])
    die("not in a git repo — pass --from")
    return Path()


def files_under(src: Path, start: Path) -> list[str]:
    """Relative paths of the files under *start* (a file or a folder), pruned."""
    if start.is_file() or start.is_symlink():
        return [start.relative_to(src).as_posix()]
    found = []
    for root, dirs, files in os.walk(start):
        dirs[:] = [d for d in dirs if d not in PRUNE]
        found += [Path(root, f).relative_to(src).as_posix() for f in files]
    return found


def env_files(src: Path) -> list[str]:
    return [rel for rel in files_under(src, src)
            if (n := rel.rsplit("/", 1)[-1]) == ".env" or n.startswith(".env.")]


def extra_files(src: Path, patterns: list[str]) -> list[str]:
    found: list[str] = []
    for pat in patterns:
        matches = list(src.glob(pat))
        if not matches:
            log(f"  ! extra '{pat}': nothing in {src}")
        for m in matches:
            found += files_under(src, m)
    return found


def collect(src: Path, extras: list[str]) -> list[str]:
    return sorted(set(env_files(src)) | set(extra_files(src, extras)))


def copy(src: Path, dst: Path, extras: list[str], dry: bool) -> None:
    src, dst = src.resolve(), dst.resolve()
    if src == dst:
        die(f"source and destination are the same: {src}")
    if not dst.is_dir():
        die(f"destination is not a folder: {dst}")
    copied = skipped = 0
    for rel in collect(src, extras):
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
    log(f"{'dry-run: ' if dry else ''}{copied} file(s) copied, {skipped} already present (kept)")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    for name in ("copy", "list-paths"):
        c = sp.add_parser(name)
        c.add_argument("--from", dest="src")
        c.add_argument("--extra", action="append", default=[], help="extra path or glob (repeatable)")
        if name == "copy":
            c.add_argument("--to")
            c.add_argument("--dry-run", action="store_true")
    a = p.parse_args()

    src = Path(a.src) if a.src else main_worktree()
    extras = ENV.extra_paths() + a.extra
    if extras:
        log(f"extra items: {', '.join(extras)}")
    if a.cmd == "list-paths":
        print("\n".join(collect(src.resolve(), extras)))
        return 0
    dst = Path(a.to) if a.to else Path(out("rev-parse", "--show-toplevel") or ".")
    log(f"{src} -> {dst}")
    copy(src, dst, extras, a.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
