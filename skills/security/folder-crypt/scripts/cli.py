#!/usr/bin/env python3
"""Encrypt or decrypt a folder with a password (prompt, flag, or .env)."""

from __future__ import annotations

import argparse
import getpass
import json
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


def _resolve_folder(arg: str | None) -> Path:
    raw = (arg or ENV.folder() or _ask("Folder")).strip()
    if not raw:
        raise SystemExit("Folder path is empty")
    return Path(raw).expanduser().resolve()


def _resolve_archive(arg: str | None) -> Path:
    raw = (arg or ENV.folder() or _ask("Archive (.fcr)")).strip()
    if not raw:
        raise SystemExit("Archive path is empty")
    path = Path(raw).expanduser().resolve()
    if not path.is_file():
        candidate = archive_path_for(path)
        if candidate.is_file():
            path = candidate
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
    _print(
        {
            "env_path": str(path),
            "exists": path.is_file(),
            "CURRENT_SKILL_DIRECTORY": str(ENV.env_cred().workspace),
            "FOLDER": values.get("FOLDER") or None,
            "PASSWORD": "set" if values.get("PASSWORD", "").strip() else "missing",
        }
    )
    return 0


def cmd_encrypt(args: argparse.Namespace) -> int:
    folder = _resolve_folder(args.folder)
    password = _resolve_password(args.password, confirm=True)
    output = (
        Path(args.output).expanduser().resolve()
        if args.output
        else archive_path_for(folder)
    )
    size = encrypt_folder(folder, password, output)
    if args.remove:
        shutil.rmtree(folder)
    _print(
        {
            "ok": True,
            "action": "encrypt",
            "folder": str(folder),
            "archive": str(output),
            "bytes": size,
            "removed": bool(args.remove),
        }
    )
    return 0


def cmd_decrypt(args: argparse.Namespace) -> int:
    archive = _resolve_archive(args.archive)
    password = _resolve_password(args.password, confirm=False)
    dest = (
        Path(args.output).expanduser().resolve()
        if args.output
        else folder_path_for(archive)
    )
    decrypt_archive(archive, password, dest)
    _print(
        {
            "ok": True,
            "action": "decrypt",
            "archive": str(archive),
            "folder": str(dest),
        }
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Encrypt or decrypt a folder with a password",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    env = sub.add_parser("env", help="Resolve SkillCred .env path (does not print PASSWORD)")
    env.set_defaults(func=cmd_env)

    encrypt = sub.add_parser("encrypt", help="Encrypt a folder into a .fcr archive")
    encrypt.add_argument(
        "folder",
        nargs="?",
        help="Folder to encrypt (else FOLDER in .env, else prompt)",
    )
    encrypt.add_argument("-o", "--output", help="Output .fcr path (default: <folder>.fcr)")
    encrypt.add_argument(
        "--password",
        help="Password (else PASSWORD in .env, else prompt)",
    )
    encrypt.add_argument(
        "--remove",
        action="store_true",
        help="Delete the original folder after a successful encrypt",
    )
    encrypt.set_defaults(func=cmd_encrypt)

    decrypt = sub.add_parser("decrypt", help="Decrypt a .fcr archive back to a folder")
    decrypt.add_argument(
        "archive",
        nargs="?",
        help="Archive or folder path (else FOLDER in .env, else prompt)",
    )
    decrypt.add_argument("-o", "--output", help="Destination folder (default: archive name without .fcr)")
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
