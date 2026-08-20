#!/usr/bin/env python3
"""Image converter CLI — Pillow convert + resize router; SVG input is rasterized."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from convert import Convert
from resize import Resize
from svg import register_svg_check
from thumbnail import Thumbnail
from trim import Trim


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Convert, resize, trim, and thumbnail images "
            "(WebP / PNG / JPG / SVG; SVG→SVG stays vector)"
        )
    )
    sub = parser.add_subparsers(required=True)
    Convert.register(sub)
    Resize.register(sub)
    Trim.register(sub)
    Thumbnail.register(sub)
    register_svg_check(sub)
    args = parser.parse_args(argv)
    result = args.func(args)
    return 0 if result is None else int(result)


if __name__ == "__main__":
    raise SystemExit(main())
