"""Shared CLI I/O: JSON stdout, secret delivery, password sources, argparse flags."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import bw
from bw import BitwardenError


def emit(data: Any) -> None:
    print(json.dumps(data, indent=2, default=str))


def write_secret_file(path: Path, value: str) -> Path:
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(value)
    os.chmod(path, 0o600)
    return path


def _clipboard_command() -> list[str] | None:
    if sys.platform == "darwin":
        return ["pbcopy"]
    if sys.platform == "win32":
        return ["clip"]
    for candidate in (["wl-copy"], ["xclip", "-selection", "clipboard"], ["xsel", "-bi"]):
        if shutil.which(candidate[0]):
            return candidate
    return None


def copy_to_clipboard(value: str) -> bool:
    command = _clipboard_command()
    if not command:
        return False
    try:
        subprocess.run(command, input=value, text=True, check=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return False
    return True


def deliver_secret(value: str, args: argparse.Namespace, label: str) -> dict[str, Any]:
    """Return a payload for a secret: file, clipboard, revealed, or masked."""
    result: dict[str, Any] = {"object": label}
    if getattr(args, "output", None):
        path = write_secret_file(Path(args.output), value)
        result["written_to"] = str(path)
        result["value"] = bw.mask(value)
        return result
    if getattr(args, "clipboard", False):
        if copy_to_clipboard(value):
            result["copied_to_clipboard"] = True
            result["value"] = bw.mask(value)
            return result
        result["copied_to_clipboard"] = False
        result["warning"] = "no clipboard tool found"
    result["value"] = value if args.reveal else bw.mask(value)
    if not args.reveal:
        result["hint"] = "add --reveal, --clipboard or --output to obtain the value"
    return result


def resolve_password(args: argparse.Namespace) -> str | None:
    """Password from --generate, --password-stdin, or --password (in that order)."""
    if getattr(args, "generate", False):
        return bw.run(["generate", "--length", str(args.generate_length), "-uln", "-s"])
    if getattr(args, "password_stdin", False):
        value = sys.stdin.readline().rstrip("\n")
        if not value:
            raise BitwardenError("no password received on stdin", code="bad_input")
        return value
    return getattr(args, "password", None)


def parse_fields(pairs: list[str] | None, field_type: int) -> list[dict[str, Any]]:
    fields: list[dict[str, Any]] = []
    for raw in pairs or []:
        name, sep, value = raw.partition("=")
        if not sep:
            raise BitwardenError(f"field must be name=value, got {name!r}", code="bad_input")
        fields.append({"name": name, "value": value, "type": field_type})
    return fields


def add_secret_output_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--reveal", action="store_true", help="Print the secret in clear text")
    parser.add_argument("--clipboard", action="store_true", help="Copy the secret to the clipboard")
    parser.add_argument("--output", help="Write the secret to a file (chmod 600)")


def add_password_source_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--password", help="Visible in the process list — prefer --generate")
    parser.add_argument("--password-stdin", action="store_true", help="Read the password from stdin")
    parser.add_argument("--generate", action="store_true", help="Generate a strong password")
    parser.add_argument("--generate-length", type=int, default=20)


def add_item_content_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--notes")
    parser.add_argument("--folderid")
    parser.add_argument("--username")
    parser.add_argument("--totp", help="TOTP secret / otpauth URI")
    parser.add_argument("--uri", action="append", help="Login URI (repeatable)")
    parser.add_argument("--field", action="append", metavar="NAME=VALUE", help="Text field")
    parser.add_argument("--hidden-field", action="append", metavar="NAME=VALUE", help="Hidden field")
    parser.add_argument("--card-holder")
    parser.add_argument("--card-brand")
    parser.add_argument("--card-number")
    parser.add_argument("--card-exp-month")
    parser.add_argument("--card-exp-year")
    parser.add_argument("--card-code")
    parser.add_argument("--identity-first-name")
    parser.add_argument("--identity-last-name")
    parser.add_argument("--identity-email")
    parser.add_argument("--identity-phone")
    add_password_source_flags(parser)
    parser.add_argument("--reveal", action="store_true", help="Do not mask secrets in the response")
