#!/usr/bin/env python3
"""logo.dev finder CLI — search and download logos."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from search import Search
from skill_env import LogoDevSkillEnv


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Search logo.dev and download logos into a folder"
    )
    sub = parser.add_subparsers(required=True)
    LogoDevSkillEnv.register(sub)
    Search.register(sub)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
