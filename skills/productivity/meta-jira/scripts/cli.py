#!/usr/bin/env python3
"""Jira CLI — load credentials from SkillCred `.env` into the process env."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from env_load import (  # noqa: E402
    REQUIRED_KEYS,
    display_env_path,
    display_skill_home,
    env_cred,
    env_path,
    load_env,
    require_env,
)


def _print(data: Any) -> None:
    print(json.dumps(data, indent=2, default=str))


def _mask(value: str) -> str:
    if len(value) <= 4:
        return "****"
    return f"{value[:2]}…{value[-2:]}"


def cmd_env(_: argparse.Namespace) -> int:
    path = load_env()
    present = {k: bool(os.environ.get(k, "").strip()) for k in REQUIRED_KEYS}
    _print(
        {
            "env_path": str(path),
            "exists": path.is_file(),
            "display_env_path": display_env_path(),
            "skill_home": display_skill_home(),
            "CURRENT_SKILL_DIRECTORY": str(env_cred().workspace),
            "present": present,
        }
    )
    return 0


def cmd_env_check(_: argparse.Namespace) -> int:
    values = require_env()
    _print(
        {
            "ok": True,
            "env_path": str(env_path()),
            "JIRA_SITE_URL": values["JIRA_SITE_URL"],
            "JIRA_EMAIL": values["JIRA_EMAIL"],
            "JIRA_API_TOKEN": _mask(values["JIRA_API_TOKEN"]),
        }
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="meta-jira skill CLI")
    sub = p.add_subparsers(dest="command", required=True)

    env_p = sub.add_parser("env", help="Load .env and show resolved paths")
    env_p.set_defaults(func=cmd_env)

    check_p = sub.add_parser(
        "env-check",
        help="Load .env and verify JIRA_SITE_URL / JIRA_EMAIL / JIRA_API_TOKEN",
    )
    check_p.set_defaults(func=cmd_env_check)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
