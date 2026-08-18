"""Resize images with Pillow (`Image.resize` / `ImageOps.contain` / `ImageOps.fit`)."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageOps

from base_image import dump, format_from_path, open_image, resolve_input, resolve_output, save_image

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
        img = open_image(src)
        frames = img.info.get("_frames_read", 1)
        if img.mode == "P":
            img = img.convert("RGBA" if "transparency" in img.info else "RGB")
        if img.mode == "CMYK":
            img = img.convert("RGB")

        resized = self._apply(img, width, height, mode)
        w, h = resized.size
        dest = resolve_output(
            output.expanduser() if output else src.with_name(f"{src.stem}-{w}x{h}{src.suffix}"),
            force=force,
        )
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
            )
        )
        return None

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = Resize()
        p = sub.add_parser("resize", help="Resize an image with Pillow")
        p.add_argument("input", help="Source image path")
        p.add_argument("--width", type=int, help="Target width in pixels")
        p.add_argument("--height", type=int, help="Target height in pixels")
        p.add_argument(
            "--fit",
            default="contain",
            choices=list(FITS),
            help="When both width and height are set (default: contain)",
        )
        p.add_argument("--output", help="Destination path (default: {stem}-{w}x{h}{ext})")
        p.add_argument("--quality", type=int, default=85, help="JPG/WebP quality 1–100")
        p.add_argument("--force", action="store_true", help="Overwrite existing output")
        p.set_defaults(func=client.cmd_resize)
