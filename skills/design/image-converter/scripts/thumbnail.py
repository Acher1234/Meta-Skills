"""Make square-box thumbnails. SVG → SVG stays vector."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from base_image import (
    dump,
    format_from_path,
    open_image,
    output_ext_for_input,
    resolve_input,
    resolve_output,
    result_fields,
    save_image,
)
from svg import add_svg_arguments, is_svg_path, raster_image_to_svg, resize_svg, svg_kwargs


class Thumbnail:
    def thumbnail(
        self,
        source: Path,
        *,
        size: int,
        output: Path | None = None,
        quality: int = 85,
        force: bool = False,
        svg_dpi: float = 96,
        svg_width: int | None = None,
        svg_scale: float = 1.0,
    ) -> dict:
        if size <= 0:
            raise SystemExit("--size must be > 0")

        src = resolve_input(source)
        tentative = (
            output.expanduser()
            if output
            else src.with_name(f"{src.stem}-thumb{output_ext_for_input(src)}")
        )
        dest = resolve_output(tentative, force=force)

        if is_svg_path(src) and is_svg_path(dest):
            w, h = resize_svg(
                src,
                dest,
                width=size,
                height=size,
                fit="contain",
                scale=svg_scale,
                dpi=svg_dpi,
                no_upscale=True,
            )
            return {
                "ok": True,
                "input": str(src),
                "output": str(dest),
                "width": w,
                "height": h,
                "size": size,
                "bytes": dest.stat().st_size,
                "frames_read": 1,
                "input_kind": "svg",
                "svg_backend": "vector",
                "svg_px": [w, h],
            }

        img = open_image(src, svg_dpi=svg_dpi, svg_width=svg_width, svg_scale=svg_scale)
        frames = img.info.get("_frames_read", 1)
        meta = result_fields(img)
        if img.mode == "P":
            img = img.convert("RGBA" if "transparency" in img.info else "RGB")
        if img.mode == "CMYK":
            img = img.convert("RGB")

        img.thumbnail((size, size), Image.Resampling.LANCZOS)
        w, h = img.size
        if is_svg_path(dest):
            raster_image_to_svg(img, dest)
        else:
            save_image(img, dest, fmt=format_from_path(dest), quality=quality)
        img.close()
        return {
            "ok": True,
            "input": str(src),
            "output": str(dest),
            "width": w,
            "height": h,
            "size": size,
            "bytes": dest.stat().st_size,
            "frames_read": frames,
            **meta,
        }

    def cmd_thumbnail(self, args: argparse.Namespace) -> None:
        dump(
            self.thumbnail(
                Path(args.input),
                size=args.size,
                output=Path(args.output) if args.output else None,
                quality=args.quality,
                force=args.force,
                **svg_kwargs(args),
            )
        )
        return None

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = Thumbnail()
        p = sub.add_parser("thumbnail", help="Make a thumbnail (SVG → SVG stays vector)")
        p.add_argument("input", help="Source image path (webp, png, jpg, svg, svgz)")
        p.add_argument(
            "--size",
            type=int,
            required=True,
            help="Max width and height in pixels (aspect ratio kept)",
        )
        p.add_argument(
            "-o",
            "--output",
            help="Destination path (default: {stem}-thumb{ext}; SVG stays .svg)",
        )
        p.add_argument("--quality", type=int, default=85, help="JPG/WebP quality 1–100")
        p.add_argument("--force", action="store_true", help="Overwrite existing output")
        add_svg_arguments(p)
        p.set_defaults(func=client.cmd_thumbnail)
