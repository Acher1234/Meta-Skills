"""Pillow GIF helpers — RGBA compose → P + binary transparency → save."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageSequence


TRANSPARENT_INDEX = 255


def ease_in_out(t: float) -> float:
    return 0.5 - 0.5 * math.cos(math.pi * t)


def rgba_to_gif_frame(
    im: Image.Image, transparent_index: int = TRANSPARENT_INDEX
) -> Image.Image:
    """RGBA → mode P with one transparent palette index (GIF has no partial alpha)."""
    im = im.convert("RGBA")
    alpha = im.getchannel("A")
    mask = alpha.point(lambda a: 255 if a >= 8 else 0)

    solid = Image.new("RGBA", im.size, (0, 0, 0, 0))
    solid.paste(im, mask=mask)

    quantized = solid.convert("RGB").quantize(
        colors=255,
        method=Image.Quantize.FASTOCTREE,
    )

    q_pixels = list(quantized.getdata())
    a_pixels = list(mask.getdata())
    mapped = [
        transparent_index
        if a < 8
        else (idx if idx < transparent_index else transparent_index - 1)
        for idx, a in zip(q_pixels, a_pixels)
    ]

    palette = quantized.getpalette() or []
    palette = palette[: transparent_index * 3]
    while len(palette) < transparent_index * 3:
        palette.extend([0, 0, 0])
    palette.extend([0, 0, 0])

    out = Image.new("P", im.size)
    out.putpalette(palette)
    out.putdata(mapped)
    out.info["transparency"] = transparent_index
    return out


def save_gif(
    frames_rgba: list[Image.Image],
    dest: Path | str,
    *,
    duration_ms: int | list[int] = 40,
    loop: int = 0,
    transparent_index: int = TRANSPARENT_INDEX,
) -> Path:
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    gif_frames = [rgba_to_gif_frame(f, transparent_index) for f in frames_rgba]
    if not gif_frames:
        raise ValueError("no frames to save")
    gif_frames[0].save(
        dest,
        format="GIF",
        save_all=True,
        append_images=gif_frames[1:],
        duration=duration_ms,
        loop=loop,
        disposal=2,
        transparency=transparent_index,
        optimize=False,
    )
    return dest.resolve()


def make_toss_frames(
    src: Path | str,
    *,
    max_width: int = 220,
    lift: int = 48,
    fps: int = 24,
    duration_s: float = 3.0,
) -> tuple[list[Image.Image], int]:
    """Build RGBA frames: logo rises → spins at top → falls (solid black shadow)."""
    logo = Image.open(src).convert("RGBA")
    if logo.width > max_width:
        r = max_width / logo.width
        logo = logo.resize(
            (max_width, max(1, int(logo.height * r))),
            Image.Resampling.LANCZOS,
        )

    pad = 28
    canvas_w = logo.width + pad * 2
    canvas_h = logo.height + lift + pad * 2
    n = max(2, int(fps * duration_s))
    duration_ms = max(1, 1000 // fps)

    frames_rgba: list[Image.Image] = []
    for i in range(n):
        t = i / (n - 1)

        if t <= 0.30:
            p = ease_in_out(t / 0.30)
            y, angle = -lift * p, 0.0
        elif t <= 0.60:
            p = (t - 0.30) / 0.30
            y, angle = -lift, 360.0 * ease_in_out(p)
        else:
            p = ease_in_out((t - 0.60) / 0.40)
            y, angle = -lift * (1.0 - p), 360.0

        height = min(1.0, max(0.0, abs(y) / lift if lift else 0.0))
        scale = 1.0 - 0.55 * height

        rotated = logo.rotate(-angle, resample=Image.Resampling.BICUBIC, expand=True)
        canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))

        sw = max(12, int(logo.width * 0.55 * scale))
        sh = max(4, int(10 * scale))
        shadow = Image.new("RGBA", (sw + 6, sh + 6), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).ellipse(
            (3, 3, 3 + sw - 1, 3 + sh - 1), fill=(0, 0, 0, 255)
        )
        floor_y = pad + lift + logo.height - 10
        canvas.alpha_composite(
            shadow, ((canvas_w - shadow.width) // 2, floor_y - shadow.height // 2)
        )

        x = (canvas_w - rotated.width) // 2
        y_pos = int(pad + lift + y - (rotated.height - logo.height) / 2)
        canvas.alpha_composite(rotated, (x, y_pos))
        frames_rgba.append(canvas)

    return frames_rgba, duration_ms


def make_toss_gif(
    src: Path | str,
    dest: Path | str,
    *,
    max_width: int = 220,
    lift: int = 48,
    fps: int = 24,
    duration_s: float = 3.0,
) -> Path:
    frames, duration_ms = make_toss_frames(
        src, max_width=max_width, lift=lift, fps=fps, duration_s=duration_s
    )
    return save_gif(frames, dest, duration_ms=duration_ms, loop=0)


def load_frames_from_dir(directory: Path | str) -> list[Image.Image]:
    directory = Path(directory)
    paths = sorted(
        p
        for p in directory.iterdir()
        if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}
    )
    if not paths:
        raise FileNotFoundError(f"no image frames in {directory}")
    return [Image.open(p).convert("RGBA") for p in paths]


def gif_info(path: Path | str) -> dict:
    path = Path(path)
    with Image.open(path) as im:
        info = {
            "path": str(path.resolve()),
            "n_frames": getattr(im, "n_frames", 1),
            "size": list(im.size),
            "mode": im.mode,
            "info": {k: im.info.get(k) for k in (
                "background", "transparency", "version", "duration", "loop", "comment"
            ) if k in im.info},
        }
        durations = []
        for frame in ImageSequence.Iterator(im):
            durations.append(frame.info.get("duration"))
        info["frame_durations"] = durations
        return info
