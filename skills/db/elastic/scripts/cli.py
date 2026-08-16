#!/usr/bin/env python3
"""Elasticsearch CLI — thin router."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from indices import Indices  # noqa: E402
from kibana import Kibana  # noqa: E402
from skill_env import register as register_env  # noqa: E402
from utils import Utils  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Elasticsearch / Kibana CLI")
    sub = parser.add_subparsers(required=True)
    register_env(sub)
    Utils.register(sub)
    Indices.register(sub)
    Kibana.register(sub)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
