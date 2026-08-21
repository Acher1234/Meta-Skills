#!/usr/bin/env python3
"""Dealabs CLI — deals + thread comments."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from dealabs import DealabsError
from deals import Deals
from thread_comments import ThreadComments


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Dealabs REST v2 CLI (deals + thread comments)"
    )
    sub = parser.add_subparsers(required=True)
    Deals.register(sub)
    ThreadComments.register(sub)
    args = parser.parse_args(argv)
    try:
        result = args.func(args)
    except DealabsError as exc:
        print(
            json.dumps(
                {"ok": False, "status": exc.status, "error": exc.body},
                indent=2,
                default=str,
                ensure_ascii=False,
            )
        )
        return 1
    return 0 if result is None else int(result)


if __name__ == "__main__":
    raise SystemExit(main())
