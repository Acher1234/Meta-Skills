"""Convert images between WebP, PNG, and JPG with Pillow."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from PIL import Image

from base_image import (
    EXTENSION,
    dump,
    normalize_format,
    open_image,
    parse_color,
    resolve_input,
    resolve_output,
    save_image,
)


class Convert:
    def convert(
        self,
        source: Path,
        fmt: str,
        *,
        output: Path | None = None,
        quality: int = 85,
        background: str = "#ffffff",
        force: bool = False,
    ) -> dict[str, Any]:
        src = resolve_input(source)
        dest_fmt = normalize_format(fmt)
        dest = resolve_output(
            output.expanduser() if output else src.with_suffix(EXTENSION[dest_fmt]),
            force=force,
        )
        img = open_image(src)
        frames = img.info.get("_frames_read", 1)
        prepared = self._prepare(img, dest_fmt, background)
        save_image(prepared, dest, fmt=dest_fmt, quality=quality)
        img.close()
        return {
            "ok": True,
            "input": str(src),
            "output": str(dest),
            "format": dest_fmt,
            "bytes": dest.stat().st_size,
            "frames_read": frames,
        }

    def _prepare(self, img: Image.Image, fmt: str, background: str) -> Image.Image:
        if img.mode == "P":
            img = img.convert("RGBA" if "transparency" in img.info else "RGB")
        if img.mode == "CMYK":
            img = img.convert("RGB")
        if fmt != "jpg" and img.mode == "LA":
            return img.convert("RGBA")
        if fmt == "jpg":
            if img.mode in {"RGBA", "LA"}:
                rgba = img.convert("RGBA")
                bg = Image.new("RGB", rgba.size, parse_color(background))
                bg.paste(rgba, mask=rgba.split()[-1])
                return bg
            return img.convert("RGB")
        if img.mode not in {"RGB", "RGBA", "L", "LA"}:
            return img.convert("RGBA")
        return img

    def cmd_convert(self, args: argparse.Namespace) -> None:
        dump(
            self.convert(
                Path(args.input),
                args.to,
                output=Path(args.output) if args.output else None,
                quality=args.quality,
                background=args.background,
                force=args.force,
            )
        )
        return None

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = Convert()
        p = sub.add_parser("convert", help="Convert WebP / PNG / JPG with Pillow")
        p.add_argument("input", help="Source image path")
        p.add_argument(
            "--to",
            required=True,
            choices=["webp", "png", "jpg", "jpeg"],
            help="Output format",
        )
        p.add_argument("--output", help="Destination path (default: same stem + new ext)")
        p.add_argument("--quality", type=int, default=85, help="JPG/WebP quality 1–100")
        p.add_argument(
            "--background",
            default="#ffffff",
            help="Flatten color when converting to JPG",
        )
        p.add_argument("--force", action="store_true", help="Overwrite existing output")
        p.set_defaults(func=client.cmd_convert)
