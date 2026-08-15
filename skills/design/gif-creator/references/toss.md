# Toss recipe: rise → spin → fall

Copy `rgba_to_gif_frame` from [pipeline.md](pipeline.md), then run this with the shared venv Python.

```python
from PIL import Image, ImageDraw
import math
from pathlib import Path

def ease_in_out(t: float) -> float:
    return 0.5 - 0.5 * math.cos(math.pi * t)

def make_toss_gif(
    src: Path,
    dest: Path,
    *,
    max_width: int = 220,
    lift: int = 48,
    fps: int = 24,
    duration_s: float = 3.0,
) -> None:
    logo = Image.open(src).convert("RGBA")
    if logo.width > max_width:
        r = max_width / logo.width
        logo = logo.resize((max_width, int(logo.height * r)), Image.Resampling.LANCZOS)

    pad = 28
    canvas_w = logo.width + pad * 2
    canvas_h = logo.height + lift + pad * 2
    n = int(fps * duration_s)
    duration_ms = 1000 // fps

    frames_rgba = []
    for i in range(n):
        t = i / (n - 1)

        # 0–30% rise, 30–60% spin at the top, 60–100% fall
        if t <= 0.30:
            p = ease_in_out(t / 0.30)
            y, angle = -lift * p, 0.0
        elif t <= 0.60:
            p = (t - 0.30) / 0.30
            y, angle = -lift, 360.0 * ease_in_out(p)
        else:
            p = ease_in_out((t - 0.60) / 0.40)
            y, angle = -lift * (1.0 - p), 360.0

        height = min(1.0, max(0.0, abs(y) / lift))
        # smaller shadow at the top (fakes more transparency)
        scale = 1.0 - 0.55 * height

        rotated = logo.rotate(-angle, resample=Image.Resampling.BICUBIC, expand=True)
        canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))

        # Solid black shadow (no gray, no dither)
        sw = max(12, int(logo.width * 0.55 * scale))
        sh = max(4, int(10 * scale))
        shadow = Image.new("RGBA", (sw + 6, sh + 6), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).ellipse((3, 3, 3 + sw - 1, 3 + sh - 1), fill=(0, 0, 0, 255))
        floor_y = pad + lift + logo.height - 10
        canvas.alpha_composite(shadow, ((canvas_w - shadow.width) // 2, floor_y - shadow.height // 2))

        x = (canvas_w - rotated.width) // 2
        y_pos = int(pad + lift + y - (rotated.height - logo.height) / 2)
        canvas.alpha_composite(rotated, (x, y_pos))
        frames_rgba.append(canvas)

    gif_frames = [rgba_to_gif_frame(f) for f in frames_rgba]  # see pipeline.md
    gif_frames[0].save(
        dest,
        save_all=True,
        append_images=gif_frames[1:],
        duration=duration_ms,
        loop=0,
        disposal=2,
        transparency=255,
        optimize=False,
    )
```
