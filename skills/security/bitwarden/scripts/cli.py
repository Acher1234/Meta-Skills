#!/usr/bin/env python3
"""Bitwarden CLI — vault read/write and Send, with masked output by default."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import bw  # noqa: E402
import send_cmds  # noqa: E402
import session_cmds  # noqa: E402
import vault_cmds  # noqa: E402
from cli_io import emit  # noqa: E402
from bw import BitwardenError  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Bitwarden vault CLI (read, write, Send)")
    sub = p.add_subparsers(dest="command", required=True)
    session_cmds.register(sub)
    vault_cmds.register(sub)
    send_cmds.register(sub)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except BitwardenError as exc:
        payload: dict[str, Any] = {"error": True, "code": exc.code, "message": str(exc)}
        if exc.detail is not None:
            payload["detail"] = exc.detail
        if exc.code == "locked":
            bw.clear_session()
            payload["unlock_command"] = bw.unlock_hint()
        emit(payload)
        return 1
    except Exception as exc:  # noqa: BLE001 — stdout must stay JSON for the agent
        if os.environ.get("BITWARDEN_SKILL_DEBUG"):
            raise
        emit(
            {
                "error": True,
                "code": "internal_error",
                "exception": type(exc).__name__,
                "hint": "re-run with BITWARDEN_SKILL_DEBUG=1 to get the traceback",
            }
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
