"""Shared Pillow open/save helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps

FORMATS = ("webp", "png", "jpg")
ALIASES = {"jpeg": "jpg"}
PIL_FORMAT = {"webp": "WEBP", "png": "PNG", "jpg": "JPEG"}
EXTENSION = {"webp": ".webp", "png": ".png", "jpg": ".jpg"}
INPUT_SUFFIXES = {".webp", ".png", ".jpg", ".jpeg"}


def dump(data: Any) -> None:
    print(json.dumps(data, indent=2))


def normalize_format(fmt: str) -> str:
    key = ALIASES.get(fmt.lower(), fmt.lower())
    if key not in FORMATS:
        raise SystemExit(f"unsupported output format: {fmt} (use webp, png, jpg)")
    return key


def format_from_path(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".jpeg":
        return "jpg"
    key = suffix.lstrip(".")
    if key not in FORMATS:
        raise SystemExit(f"unsupported format: {path.suffix} (use webp, png, jpg)")
    return key


def resolve_input(source: Path) -> Path:
    src = source.expanduser().resolve()
    if not src.is_file():
        raise SystemExit(f"input not found: {src}")
    if src.suffix.lower() not in INPUT_SUFFIXES:
        raise SystemExit(f"unsupported input format: {src.suffix} (use webp, png, jpg)")
    return src


def resolve_output(dest: Path, *, force: bool) -> Path:
    dest = dest.expanduser().resolve()
    if dest.exists() and not force:
        raise SystemExit(f"output exists: {dest} (pass --force to overwrite)")
    dest.parent.mkdir(parents=True, exist_ok=True)
    return dest


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


def open_image(src: Path) -> Image.Image:
    img = Image.open(src)
    img.load()
    frames = getattr(img, "n_frames", 1) or 1
    img = ImageOps.exif_transpose(img)
    img.info["_frames_read"] = frames
    return img


def save_image(
    img: Image.Image,
    dest: Path,
    *,
    fmt: str | None = None,
    quality: int = 85,
) -> None:
    dest_fmt = normalize_format(fmt) if fmt else format_from_path(dest)
    kwargs: dict[str, Any] = {}
    if dest_fmt == "jpg":
        kwargs.update(quality=quality, optimize=True)
    elif dest_fmt == "webp":
        kwargs.update(quality=quality, method=6)
    elif dest_fmt == "png":
        kwargs.update(optimize=True)
    img.save(dest, format=PIL_FORMAT[dest_fmt], **kwargs)
