#!/usr/bin/env python3
"""CLI: create animated GIFs with Pillow (toss / frames / info)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from gif_utils import gif_info, load_frames_from_dir, make_toss_gif, save_gif  # noqa: E402


def _cmd_toss(args: argparse.Namespace) -> int:
    dest = make_toss_gif(
        args.src,
        args.dest,
        max_width=args.max_width,
        lift=args.lift,
        fps=args.fps,
        duration_s=args.duration,
    )
    print(json.dumps({"ok": True, "path": str(dest)}, indent=2))
    return 0


def _cmd_from_frames(args: argparse.Namespace) -> int:
    frames = load_frames_from_dir(args.dir)
    duration_ms = args.duration_ms
    if duration_ms is None:
        duration_ms = max(1, 1000 // args.fps)
    dest = save_gif(frames, args.dest, duration_ms=duration_ms, loop=args.loop)
    print(json.dumps({"ok": True, "path": str(dest), "frames": len(frames)}, indent=2))
    return 0


def _cmd_info(args: argparse.Namespace) -> int:
    print(json.dumps(gif_info(args.path), indent=2, default=str))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Create / inspect animated GIFs (Pillow)")
    sub = p.add_subparsers(dest="command", required=True)

    toss = sub.add_parser("toss", help="Logo rises → spins → falls (transparent GIF)")
    toss.add_argument("src", type=Path, help="Source image (PNG/RGBA recommended)")
    toss.add_argument("dest", type=Path, help="Output .gif path")
    toss.add_argument("--max-width", type=int, default=220)
    toss.add_argument("--lift", type=int, default=48, help="Pixels to lift at apex")
    toss.add_argument("--fps", type=int, default=24)
    toss.add_argument("--duration", type=float, default=3.0, help="Animation length (s)")
    toss.set_defaults(func=_cmd_toss)

    frames = sub.add_parser("from-frames", help="Build GIF from images in a directory")
    frames.add_argument("dir", type=Path, help="Directory of frame images (sorted by name)")
    frames.add_argument("dest", type=Path, help="Output .gif path")
    frames.add_argument("--fps", type=int, default=24)
    frames.add_argument(
        "--duration-ms",
        type=int,
        default=None,
        help="Override per-frame duration in ms (default: 1000/fps)",
    )
    frames.add_argument("--loop", type=int, default=0, help="0 = infinite")
    frames.set_defaults(func=_cmd_from_frames)

    info = sub.add_parser("info", help="Print GIF metadata / frame durations as JSON")
    info.add_argument("path", type=Path, help="Existing .gif")
    info.set_defaults(func=_cmd_info)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
