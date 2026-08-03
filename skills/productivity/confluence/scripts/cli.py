#!/usr/bin/env python3
"""Confluence skill CLI — resolve / load SkillCred `.env` for confluence-cli."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import sys
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from env_load import (  # noqa: E402
    REQUIRED_KEYS,
    confluence_cli_path,
    display_env_path,
    display_skill_home,
    env_cred,
    env_path,
    load_env,
    require_env,
)

EXPORT_KEYS = (
    *REQUIRED_KEYS,
    "CONFLUENCE_EMAIL",
    "CONFLUENCE_PROFILE",
    "CONFLUENCE_READ_ONLY",
    "CONFLUENCE_FORCE_CLOUD",
    "CONFLUENCE_LINK_STYLE",
)


def _print(data: Any) -> None:
    print(json.dumps(data, indent=2, default=str))


def _mask(value: str) -> str:
    if len(value) <= 4:
        return "****"
    return f"{value[:2]}…{value[-2:]}"


def cmd_env(_: argparse.Namespace) -> int:
    """Load `.env` into os.environ and show resolved paths."""
    path = load_env()
    present = {k: bool(os.environ.get(k, "").strip()) for k in REQUIRED_KEYS}
    present["CONFLUENCE_EMAIL"] = bool(os.environ.get("CONFLUENCE_EMAIL", "").strip())
    _print(
        {
            "env_path": str(path),
            "exists": path.is_file(),
            "display_env_path": display_env_path(),
            "skill_home": display_skill_home(),
            "CURRENT_SKILL_DIRECTORY": str(env_cred().workspace),
            "confluence_cli": confluence_cli_path(),
            "present": present,
        }
    )
    return 0


def cmd_env_check(_: argparse.Namespace) -> int:
    values = require_env()
    cli = confluence_cli_path()
    if not cli:
        raise SystemExit(
            "confluence-cli not found on PATH — run: npm install -g confluence-cli"
        )
    out: dict[str, Any] = {
        "ok": True,
        "env_path": str(env_path()),
        "confluence_cli": cli,
        "CONFLUENCE_DOMAIN": values["CONFLUENCE_DOMAIN"],
        "CONFLUENCE_API_PATH": values["CONFLUENCE_API_PATH"],
        "CONFLUENCE_AUTH_TYPE": values["CONFLUENCE_AUTH_TYPE"],
        "CONFLUENCE_API_TOKEN": _mask(values["CONFLUENCE_API_TOKEN"]),
    }
    if "CONFLUENCE_EMAIL" in values:
        out["CONFLUENCE_EMAIL"] = values["CONFLUENCE_EMAIL"]
    _print(out)
    return 0


def cmd_env_path(_: argparse.Namespace) -> int:
    path = env_path()
    print(path)
    return 0 if path.is_file() else 1


def cmd_print_exports(_: argparse.Namespace) -> int:
    load_env(override=True)
    require_env()
    for key in EXPORT_KEYS:
        value = os.environ.get(key, "").strip()
        if value:
            print(f"export {key}={shlex.quote(value)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="confluence skill CLI — load .env before confluence-cli"
    )
    sub = p.add_subparsers(dest="command", required=True)

    env_p = sub.add_parser("env", help="Load .env into process env; show paths")
    env_p.set_defaults(func=cmd_env)

    check_p = sub.add_parser(
        "env-check",
        help="Load .env, verify required keys, check confluence-cli on PATH",
    )
    check_p.set_defaults(func=cmd_env_check)

    path_p = sub.add_parser("env-path", help="Print resolved .env path")
    path_p.set_defaults(func=cmd_env_path)

    exp_p = sub.add_parser(
        "print-exports",
        help="Print export lines for eval (loads .env first)",
    )
    exp_p.set_defaults(func=cmd_print_exports)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
