# Generation pipeline

## A — Build frames in RGBA

Compose in `RGBA` (rotation, shadow, etc.):

```python
from PIL import Image, ImageDraw, ImageFilter

canvas = Image.new("RGBA", (400, 400), (0, 0, 0, 0))  # transparent background
logo = Image.open("logo.png").convert("RGBA")
rotated = logo.rotate(45, resample=Image.Resampling.BICUBIC, expand=True)
canvas.alpha_composite(rotated, (x, y))
```

Useful APIs:

| API | Use |
|-----|-----|
| `Image.open(...).convert("RGBA")` | Load as RGBA |
| `Image.new("RGBA", size, color)` | Canvas |
| `Image.rotate(angle, expand=True, resample=...)` | Rotation |
| `Image.resize((w, h), Image.Resampling.LANCZOS)` | Scale |
| `Image.alpha_composite(a, b)` | Composite with alpha |
| `Image.paste(im, box, mask)` | Paste with mask |
| `ImageDraw.Draw(im).ellipse(...)` | Draw shadow / shapes |
| `ImageFilter.GaussianBlur(radius=...)` | Blur |

## B — Convert RGBA → mode `P` + transparency

GIF needs a **palette**. Robust pattern (`rgba_to_gif_frame`):

```python
def rgba_to_gif_frame(im: Image.Image, transparent_index: int = 255) -> Image.Image:
    """RGBA → P with 1 transparent index (docs: transparency = color index)."""
    im = im.convert("RGBA")
    alpha = im.getchannel("A")

    # Threshold: below = transparent (GIF is binary)
    mask = alpha.point(lambda a: 255 if a >= 8 else 0)

    # Opaque image for quantization
    solid = Image.new("RGBA", im.size, (0, 0, 0, 0))
    solid.paste(im, mask=mask)

    # Palette ≤ 255 colors (keep index 255 for transparency)
    quantized = solid.convert("RGB").quantize(
        colors=255,
        method=Image.Quantize.FASTOCTREE,  # or MEDIANCUT
    )

    q_pixels = list(quantized.getdata())
    a_pixels = list(mask.getdata())
    mapped = [
        transparent_index if a < 8 else (idx if idx < transparent_index else transparent_index - 1)
        for idx, a in zip(q_pixels, a_pixels)
    ]

    palette = quantized.getpalette() or []
    palette = palette[: transparent_index * 3]
    while len(palette) < transparent_index * 3:
        palette.extend([0, 0, 0])
    palette.extend([0, 0, 0])  # entry for the transparent index

    out = Image.new("P", im.size)
    out.putpalette(palette)
    out.putdata(mapped)
    out.info["transparency"] = transparent_index
    return out
```

## From a folder of images

```python
from pathlib import Path
from PIL import Image

def load_frames_from_dir(directory: Path) -> list[Image.Image]:
    paths = sorted(
        p for p in directory.iterdir()
        if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}
    )
    if not paths:
        raise FileNotFoundError(f"no image frames in {directory}")
    return [Image.open(p).convert("RGBA") for p in paths]
```

Convert with `rgba_to_gif_frame`, then save (section C).

## C — Save

```python
gif_frames = [rgba_to_gif_frame(f) for f in frames_rgba]

gif_frames[0].save(
    "out.gif",
    format="GIF",
    save_all=True,
    append_images=gif_frames[1:],
    duration=1000 // 24,  # ~24 fps
    loop=0,
    disposal=2,
    transparency=255,
    optimize=False,
)
```
