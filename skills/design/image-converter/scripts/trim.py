"""Trim extra background around a logo with Pillow (`ImageDraw.floodfill` + crop)."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

from base_image import (
    dump,
    format_from_path,
    open_image,
    parse_color,
    resolve_input,
    resolve_output,
    save_image,
)


class Trim:
    def trim(
        self,
        source: Path,
        *,
        output: Path | None = None,
        padding: int = 0,
        tolerance: int = 24,
        force: bool = False,
    ) -> dict:
        if padding < 0:
            raise SystemExit("--padding must be >= 0")
        if tolerance < 0:
            raise SystemExit("--tolerance must be >= 0")

        src = resolve_input(source)
        dest = resolve_output(
            output.expanduser() if output else src.with_name(f"{src.stem}-trim.png"),
            force=force,
        )
        dest_fmt = format_from_path(dest)

        img = open_image(src)
        frames = img.info.get("_frames_read", 1)
        if img.mode == "P":
            img = img.convert("RGBA" if "transparency" in img.info else "RGB")
        if img.mode == "CMYK":
            img = img.convert("RGB")
        rgba = img.convert("RGBA")
        img.close()

        cleaned = self._knockout_border(rgba, tolerance)
        bbox = cleaned.getchannel("A").getbbox()
        if bbox is None:
            raise SystemExit("trim found no foreground")
        cropped = cleaned.crop(bbox)
        if padding:
            cropped = ImageOps.expand(cropped, border=padding, fill=(0, 0, 0, 0))

        if dest_fmt == "jpg":
            canvas = Image.new("RGB", cropped.size, parse_color("#ffffff"))
            canvas.paste(cropped, mask=cropped.split()[-1])
            cropped = canvas

        save_image(cropped, dest, fmt=dest_fmt)
        w, h = cropped.size
        return {
            "ok": True,
            "input": str(src),
            "output": str(dest),
            "width": w,
            "height": h,
            "padding": padding,
            "tolerance": tolerance,
            "bbox": list(bbox),
            "bytes": dest.stat().st_size,
            "frames_read": frames,
        }

    @staticmethod
    def _knockout_border(rgba: Image.Image, tolerance: int) -> Image.Image:
        out = rgba.copy()
        w, h = out.size
        for xy in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
            ImageDraw.floodfill(out, xy, (0, 0, 0, 0), thresh=tolerance)
        return out

    def cmd_trim(self, args: argparse.Namespace) -> None:
        dump(
            self.trim(
                Path(args.input),
                output=Path(args.output) if args.output else None,
                padding=args.padding,
                tolerance=args.tolerance,
                force=args.force,
            )
        )
        return None

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = Trim()
        p = sub.add_parser("trim", help="Trim background around a logo")
        p.add_argument("input", help="Source image path")
        p.add_argument(
            "-o",
            "--output",
            help="Destination path (default: {stem}-trim.png)",
        )
        p.add_argument(
            "--padding",
            type=int,
            default=0,
            help="Transparent padding in pixels after trim",
        )
        p.add_argument(
            "--tolerance",
            type=int,
            default=24,
            help="Background match threshold (JPEG artifacts)",
        )
        p.add_argument("--force", action="store_true", help="Overwrite existing output")
        p.set_defaults(func=client.cmd_trim)
