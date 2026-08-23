"""Shared Pillow open/save helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps

from svg import SVG_SUFFIXES, is_svg_path, rasterize_svg

FORMATS = ("webp", "png", "jpg", "svg")
ALIASES = {"jpeg": "jpg"}
PIL_FORMAT = {"webp": "WEBP", "png": "PNG", "jpg": "JPEG"}
EXTENSION = {"webp": ".webp", "png": ".png", "jpg": ".jpg", "svg": ".svg"}
INPUT_SUFFIXES = {".webp", ".png", ".jpg", ".jpeg"} | SVG_SUFFIXES


def dump(data: Any) -> None:
    print(json.dumps(data, indent=2))


def normalize_format(fmt: str) -> str:
    key = ALIASES.get(fmt.lower(), fmt.lower())
    if key not in FORMATS:
        raise SystemExit(f"unsupported output format: {fmt} (use webp, png, jpg, svg)")
    return key


def format_from_path(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".jpeg":
        return "jpg"
    key = suffix.lstrip(".")
    if key not in FORMATS:
        raise SystemExit(f"unsupported format: {path.suffix} (use webp, png, jpg, svg)")
    return key


def resolve_input(source: Path) -> Path:
    src = source.expanduser().resolve()
    if not src.is_file():
        raise SystemExit(f"input not found: {src}")
    if src.suffix.lower() not in INPUT_SUFFIXES:
        raise SystemExit(f"unsupported input format: {src.suffix} (use webp, png, jpg, svg)")
    return src


def resolve_output(dest: Path, *, force: bool) -> Path:
    dest = dest.expanduser().resolve()
    if dest.exists() and not force:
        raise SystemExit(f"output exists: {dest} (pass --force to overwrite)")
    dest.parent.mkdir(parents=True, exist_ok=True)
    return dest


def output_ext_for_input(src: Path) -> str:
    return src.suffix


def parse_color(value: str) -> tuple[int, int, int]:
    raw = value.strip().lstrip("#")
    if len(raw) == 3:
        raw = "".join(ch * 2 for ch in raw)
    if len(raw) != 6:
        raise SystemExit(f"invalid background color: {value} (use #RRGGBB)")
    try:
        return int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)
    except ValueError as exc:
        raise SystemExit(f"invalid background color: {value}") from exc


def open_image(
    src: Path,
    *,
    svg_dpi: float = 96,
    svg_width: int | None = None,
    svg_scale: float = 1.0,
) -> Image.Image:
    if is_svg_path(src):
        return rasterize_svg(src, dpi=svg_dpi, width=svg_width, scale=svg_scale)
    img = Image.open(src)
    img.load()
    frames = getattr(img, "n_frames", 1) or 1
    img = ImageOps.exif_transpose(img)
    img.info["_frames_read"] = frames
    img.info["_input_kind"] = "raster"
    return img


def result_fields(img: Image.Image) -> dict[str, Any]:
    kind = img.info.get("_input_kind", "raster")
    fields: dict[str, Any] = {"input_kind": kind}
    if kind == "svg":
        backend = img.info.get("_svg_backend")
        if backend:
            fields["svg_backend"] = backend
        px = img.info.get("_svg_px")
        if px is not None:
            fields["svg_px"] = [int(px[0]), int(px[1])]
    return fields


def save_image(
    img: Image.Image,
    dest: Path,
    *,
    fmt: str | None = None,
    quality: int = 85,
) -> None:
    dest_fmt = normalize_format(fmt) if fmt else format_from_path(dest)
    if dest_fmt == "svg":
        raise SystemExit("SVG output is vector — use convert/resize SVG paths, not Pillow save")
    kwargs: dict[str, Any] = {}
    if dest_fmt == "jpg":
        kwargs.update(quality=quality, optimize=True)
    elif dest_fmt == "webp":
        kwargs.update(quality=quality, method=6)
    elif dest_fmt == "png":
        kwargs.update(optimize=True)
    img.save(dest, format=PIL_FORMAT[dest_fmt], **kwargs)
