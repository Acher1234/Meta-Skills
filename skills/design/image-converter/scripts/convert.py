"""Convert images between WebP, PNG, JPG, and SVG."""

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
    result_fields,
    save_image,
)
from svg import add_svg_arguments, copy_svg, is_svg_path, raster_image_to_svg, resize_svg, svg_kwargs


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
        svg_dpi: float = 96,
        svg_width: int | None = None,
        svg_scale: float = 1.0,
    ) -> dict[str, Any]:
        src = resolve_input(source)
        dest_fmt = normalize_format(fmt)
        dest = resolve_output(
            output.expanduser() if output else src.with_suffix(EXTENSION[dest_fmt]),
            force=force,
        )
        if dest_fmt == "svg":
            return self._to_svg(
                src,
                dest,
                svg_dpi=svg_dpi,
                svg_width=svg_width,
                svg_scale=svg_scale,
            )

        img = open_image(src, svg_dpi=svg_dpi, svg_width=svg_width, svg_scale=svg_scale)
        frames = img.info.get("_frames_read", 1)
        meta = result_fields(img)
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
            **meta,
        }

    def _to_svg(
        self,
        src: Path,
        dest: Path,
        *,
        svg_dpi: float,
        svg_width: int | None,
        svg_scale: float,
    ) -> dict[str, Any]:
        if is_svg_path(src):
            sized = svg_width is not None or svg_scale != 1.0
            if sized:
                w, h = resize_svg(
                    src,
                    dest,
                    width=svg_width,
                    scale=svg_scale,
                    dpi=svg_dpi,
                )
            else:
                copy_svg(src, dest)
                w = h = None
            return {
                "ok": True,
                "input": str(src),
                "output": str(dest),
                "format": "svg",
                "bytes": dest.stat().st_size,
                "frames_read": 1,
                "input_kind": "svg",
                "svg_backend": "vector",
                **({"svg_px": [w, h]} if w and h else {}),
            }

        img = open_image(src, svg_dpi=svg_dpi, svg_width=svg_width, svg_scale=svg_scale)
        frames = img.info.get("_frames_read", 1)
        meta = result_fields(img)
        w, h = img.size
        raster_image_to_svg(img, dest)
        img.close()
        return {
            "ok": True,
            "input": str(src),
            "output": str(dest),
            "format": "svg",
            "bytes": dest.stat().st_size,
            "frames_read": frames,
            "width": w,
            "height": h,
            **meta,
            "svg_backend": "embed",
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
                **svg_kwargs(args),
            )
        )
        return None

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = Convert()
        p = sub.add_parser(
            "convert",
            help="Convert WebP / PNG / JPG / SVG (SVG stays vector unless rasterizing)",
        )
        p.add_argument("input", help="Source image path (webp, png, jpg, svg, svgz)")
        p.add_argument(
            "--to",
            required=True,
            choices=["webp", "png", "jpg", "jpeg", "svg"],
            help="Output format",
        )
        p.add_argument(
            "-o",
            "--output",
            help="Destination path (default: same stem + new ext)",
        )
        p.add_argument("--quality", type=int, default=85, help="JPG/WebP quality 1–100")
        p.add_argument(
            "--background",
            default="#ffffff",
            help="Flatten color when converting to JPG",
        )
        p.add_argument("--force", action="store_true", help="Overwrite existing output")
        add_svg_arguments(p)
        p.set_defaults(func=client.cmd_convert)
