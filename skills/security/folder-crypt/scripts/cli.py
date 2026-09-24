#!/usr/bin/env python3
"""Encrypt or decrypt files and folders with a password (prompt, flag, or .env)."""

from __future__ import annotations

import argparse
import getpass
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from crypt import (  # noqa: E402
    CryptError,
    archive_path_for,
    decrypt_archive,
    encrypt_folder,
    folder_path_for,
)
from skill_env import ENV  # noqa: E402


def _print(data: Any) -> None:
    print(json.dumps(data, indent=2, default=str))


def _ask(prompt: str) -> str:
    if not sys.stdin.isatty():
        raise SystemExit(
            f"{prompt} required — pass it as an argument or set it in .env "
            f"(CURRENT_SKILL_DIRECTORY={ENV.env_cred().workspace})"
        )
    return input(f"{prompt}: ").strip()


def resolve_path(raw: str) -> Path:
    """Resolve a user path. Relative paths start at PROJECT_PATH when it is set."""
    path = Path(raw.strip()).expanduser()
    if not path.is_absolute():
        base = os.environ.get("PROJECT_PATH", "").strip()
        if base:
            root = Path(base).expanduser()
            if not root.is_absolute():
                root = Path.cwd() / root
            path = root / path
    return path.resolve()


def _targets(explicit: str | None, prompt: str) -> tuple[list[Path], bool]:
    """Return (paths, from_folder_list).

    A positional arg is that path only. With no arg, every FOLDER entry is used.
    Prompt only when FOLDER is empty.
    """
    if explicit is not None and explicit.strip():
        return [resolve_path(explicit)], False
    listed = ENV.folders()
    if listed:
        return [resolve_path(item) for item in listed], True
    answered = _ask(prompt)
    if not answered:
        raise SystemExit(f"{prompt} path is empty")
    return [resolve_path(answered)], False


def _reject_multi_output(output: str | None, count: int) -> bool:
    if output and count != 1:
        _print(
            {
                "error": True,
                "message": "--output is only valid for a single target",
            }
        )
        return True
    return False


def _as_archive(path: Path) -> Path:
    if path.is_file() and path.suffix == ".fcr":
        return path
    candidate = archive_path_for(path)
    if path.is_dir() or path.is_file() or candidate.is_file():
        return candidate
    return path


def _resolve_password(explicit: str | None, *, confirm: bool) -> str:
    password = explicit or ENV.password()
    if password:
        return password
    if not sys.stdin.isatty():
        raise SystemExit(
            "Password required — pass --password or set PASSWORD in .env "
            f"(CURRENT_SKILL_DIRECTORY={ENV.env_cred().workspace})"
        )
    password = getpass.getpass("Password: ")
    if not password:
        raise SystemExit("Password is empty")
    if confirm:
        again = getpass.getpass("Confirm password: ")
        if password != again:
            raise SystemExit("Passwords do not match")
    return password


def cmd_env(_: argparse.Namespace) -> int:
    path = ENV.env_path()
    values = ENV.read_env()
    project = os.environ.get("PROJECT_PATH", "").strip() or None
    _print(
        {
            "env_path": str(path),
            "exists": path.is_file(),
            "CURRENT_SKILL_DIRECTORY": str(ENV.env_cred().workspace),
            "PROJECT_PATH": project,
            "FOLDER": values.get("FOLDER") or None,
            "folders": ENV.folders(),
            "PASSWORD": "set" if values.get("PASSWORD", "").strip() else "missing",
        }
    )
    return 0


def _encrypt_one(folder: Path, password: str, output: Path, remove: bool) -> dict[str, Any]:
    try:
        size = encrypt_folder(folder, password, output)
        if remove:
            if folder.is_file():
                folder.unlink()
            else:
                shutil.rmtree(folder)
        return {
            "ok": True,
            "folder": str(folder),
            "archive": str(output),
            "bytes": size,
            "removed": remove,
        }
    except (CryptError, OSError) as exc:
        return {
            "ok": False,
            "folder": str(folder),
            "archive": str(output),
            "error": str(exc),
        }


def cmd_encrypt(args: argparse.Namespace) -> int:
    targets, batch = _targets(args.folder, "File or folder")
    if _reject_multi_output(args.output, len(targets)):
        return 1
    password = _resolve_password(args.password, confirm=True)
    items = [
        _encrypt_one(
            folder,
            password,
            resolve_path(args.output) if args.output else archive_path_for(folder),
            bool(args.remove),
        )
        for folder in targets
    ]
    if not batch:
        item = items[0]
        if not item["ok"]:
            _print({"error": True, "message": item["error"]})
            return 1
        _print(
            {
                "ok": True,
                "action": "encrypt",
                "folder": item["folder"],
                "archive": item["archive"],
                "bytes": item["bytes"],
                "removed": item["removed"],
            }
        )
        return 0
    ok = all(item["ok"] for item in items)
    _print({"ok": ok, "action": "encrypt", "items": items})
    return 0 if ok else 1


def _decrypt_one(archive: Path, password: str, dest: Path) -> dict[str, Any]:
    try:
        decrypt_archive(archive, password, dest)
        return {"ok": True, "archive": str(archive), "folder": str(dest)}
    except (CryptError, OSError) as exc:
        return {
            "ok": False,
            "archive": str(archive),
            "folder": str(dest),
            "error": str(exc),
        }


def cmd_decrypt(args: argparse.Namespace) -> int:
    targets, batch = _targets(args.archive, "Archive (.fcr)")
    archives = [_as_archive(path) for path in targets]
    if _reject_multi_output(args.output, len(archives)):
        return 1
    password = _resolve_password(args.password, confirm=False)
    items = [
        _decrypt_one(
            archive,
            password,
            resolve_path(args.output) if args.output else folder_path_for(archive),
        )
        for archive in archives
    ]
    if not batch:
        item = items[0]
        if not item["ok"]:
            _print({"error": True, "message": item["error"]})
            return 1
        _print(
            {
                "ok": True,
                "action": "decrypt",
                "archive": item["archive"],
                "folder": item["folder"],
            }
        )
        return 0
    ok = all(item["ok"] for item in items)
    _print({"ok": ok, "action": "decrypt", "items": items})
    return 0 if ok else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Encrypt or decrypt files and folders with a password",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    env = sub.add_parser("env", help="Resolve SkillCred .env path (does not print PASSWORD)")
    env.set_defaults(func=cmd_env)

    encrypt = sub.add_parser("encrypt", help="Encrypt a file or folder into a .fcr archive")
    encrypt.add_argument(
        "folder",
        nargs="?",
        help="File or folder to encrypt (else every FOLDER entry in .env, else prompt)",
    )
    encrypt.add_argument(
        "-o",
        "--output",
        help="Output .fcr path for a single target (default: <path>.fcr)",
    )
    encrypt.add_argument(
        "--password",
        help="Password (else PASSWORD in .env, else prompt)",
    )
    encrypt.add_argument(
        "--remove",
        action="store_true",
        help="Delete the original file or folder after a successful encrypt",
    )
    encrypt.set_defaults(func=cmd_encrypt)

    decrypt = sub.add_parser("decrypt", help="Decrypt a .fcr archive back to a file or folder")
    decrypt.add_argument(
        "archive",
        nargs="?",
        help="Archive, file, or folder (else every FOLDER entry in .env, else prompt)",
    )
    decrypt.add_argument(
        "-o",
        "--output",
        help="Destination for a single target (default: archive name without .fcr)",
    )
    decrypt.add_argument(
        "--password",
        help="Password (else PASSWORD in .env, else prompt)",
    )
    decrypt.set_defaults(func=cmd_decrypt)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except CryptError as exc:
        _print({"error": True, "message": str(exc)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
