"""Resize images. Raster uses Pillow; SVG → SVG stays vector (viewBox + width/height)."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageOps

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
from svg import (
    add_svg_arguments,
    is_svg_path,
    planned_svg_size,
    raster_image_to_svg,
    resize_svg,
    svg_kwargs,
)

FITS = ("contain", "cover", "stretch")


class Resize:
    def resize(
        self,
        source: Path,
        *,
        width: int | None = None,
        height: int | None = None,
        fit: str = "contain",
        output: Path | None = None,
        quality: int = 85,
        force: bool = False,
        svg_dpi: float = 96,
        svg_width: int | None = None,
        svg_scale: float = 1.0,
    ) -> dict:
        if not width and not height:
            raise SystemExit("--width and/or --height is required")
        if width is not None and width <= 0:
            raise SystemExit("--width must be > 0")
        if height is not None and height <= 0:
            raise SystemExit("--height must be > 0")
        mode = fit.lower()
        if mode not in FITS:
            raise SystemExit(f"unsupported --fit: {fit} (use contain, cover, stretch)")

        src = resolve_input(source)
        if is_svg_path(src) and (output is None or is_svg_path(output.expanduser())):
            w, h = planned_svg_size(
                src,
                width=width,
                height=height,
                fit=mode,
                scale=svg_scale,
                dpi=svg_dpi,
            )
            dest = resolve_output(
                output.expanduser()
                if output
                else src.with_name(f"{src.stem}-{w}x{h}{src.suffix}"),
                force=force,
            )
            resize_svg(
                src,
                dest,
                width=width,
                height=height,
                fit=mode,
                scale=svg_scale,
                dpi=svg_dpi,
            )
            return {
                "ok": True,
                "input": str(src),
                "output": str(dest),
                "width": w,
                "height": h,
                "fit": mode,
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

        resized = self._apply(img, width, height, mode)
        w, h = resized.size
        dest = resolve_output(
            output.expanduser()
            if output
            else src.with_name(f"{src.stem}-{w}x{h}{output_ext_for_input(src)}"),
            force=force,
        )
        if is_svg_path(dest):
            raster_image_to_svg(resized, dest)
        else:
            save_image(resized, dest, fmt=format_from_path(dest), quality=quality)
        img.close()
        return {
            "ok": True,
            "input": str(src),
            "output": str(dest),
            "width": w,
            "height": h,
            "fit": mode,
            "bytes": dest.stat().st_size,
            "frames_read": frames,
            **meta,
        }

    @staticmethod
    def _apply(
        img: Image.Image,
        width: int | None,
        height: int | None,
        fit: str,
    ) -> Image.Image:
        ow, oh = img.size
        if width and not height:
            return img.resize(
                (width, max(1, round(oh * width / ow))),
                Image.Resampling.LANCZOS,
            )
        if height and not width:
            return img.resize(
                (max(1, round(ow * height / oh)), height),
                Image.Resampling.LANCZOS,
            )
        box = (width, height)
        if fit == "stretch":
            return img.resize(box, Image.Resampling.LANCZOS)
        if fit == "cover":
            return ImageOps.fit(img, box, method=Image.Resampling.LANCZOS)
        return ImageOps.contain(img, box, method=Image.Resampling.LANCZOS)

    def cmd_resize(self, args: argparse.Namespace) -> None:
        dump(
            self.resize(
                Path(args.input),
                width=args.width,
                height=args.height,
                fit=args.fit,
                output=Path(args.output) if args.output else None,
                quality=args.quality,
                force=args.force,
                **svg_kwargs(args),
            )
        )
        return None

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = Resize()
        p = sub.add_parser(
            "resize",
            help="Resize an image (SVG → SVG stays vector)",
        )
        p.add_argument("input", help="Source image path (webp, png, jpg, svg, svgz)")
        p.add_argument("--width", type=int, help="Target width in pixels")
        p.add_argument("--height", type=int, help="Target height in pixels")
        p.add_argument(
            "--fit",
            default="contain",
            choices=list(FITS),
            help="When both width and height are set (default: contain)",
        )
        p.add_argument(
            "-o",
            "--output",
            help="Destination path (default keeps input type; SVG stays .svg)",
        )
        p.add_argument("--quality", type=int, default=85, help="JPG/WebP quality 1–100")
        p.add_argument("--force", action="store_true", help="Overwrite existing output")
        add_svg_arguments(p)
        p.set_defaults(func=client.cmd_resize)
