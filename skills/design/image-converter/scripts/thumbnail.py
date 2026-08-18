"""Make square-box thumbnails with Pillow (`Image.thumbnail`)."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from base_image import dump, format_from_path, open_image, resolve_input, resolve_output, save_image


class Thumbnail:
    def thumbnail(
        self,
        source: Path,
        *,
        size: int,
        output: Path | None = None,
        quality: int = 85,
        force: bool = False,
    ) -> dict:
        if size <= 0:
            raise SystemExit("--size must be > 0")

        src = resolve_input(source)
        dest = resolve_output(
            output.expanduser() if output else src.with_name(f"{src.stem}-thumb{src.suffix}"),
            force=force,
        )

        img = open_image(src)
        frames = img.info.get("_frames_read", 1)
        if img.mode == "P":
            img = img.convert("RGBA" if "transparency" in img.info else "RGB")
        if img.mode == "CMYK":
            img = img.convert("RGB")

        img.thumbnail((size, size), Image.Resampling.LANCZOS)
        w, h = img.size
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
        }

    def cmd_thumbnail(self, args: argparse.Namespace) -> None:
        dump(
            self.thumbnail(
                Path(args.input),
                size=args.size,
                output=Path(args.output) if args.output else None,
                quality=args.quality,
                force=args.force,
            )
        )
        return None

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = Thumbnail()
        p = sub.add_parser("thumbnail", help="Make a thumbnail with Pillow")
        p.add_argument("input", help="Source image path")
        p.add_argument(
            "--size",
            type=int,
            required=True,
            help="Max width and height in pixels (aspect ratio kept)",
        )
        p.add_argument(
            "-o",
            "--output",
            help="Destination path (default: {stem}-thumb{ext})",
        )
        p.add_argument("--quality", type=int, default=85, help="JPG/WebP quality 1–100")
        p.add_argument("--force", action="store_true", help="Overwrite existing output")
        p.set_defaults(func=client.cmd_thumbnail)
