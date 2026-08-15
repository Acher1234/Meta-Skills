# Saving animated GIFs

Official pattern: call `save()` on the **first** frame and pass the rest in `append_images`. Do not pass `append_images=frames` or frame 0 is duplicated.

```python
from PIL import Image

frames = [...]  # PIL Image, same size recommended (P, RGB, RGBA, …)

frames[0].save(
    "out.gif",
    save_all=True,
    append_images=frames[1:],
    duration=40,   # ms per frame
    loop=0,        # 0 = infinite
)
```

## Animation / multi-frame options

| Option | Type | Description |
|--------|------|-------------|
| `save_all` | `bool` | If `True` (or `append_images` is non-empty), save **all** frames. Otherwise only the first. |
| `append_images` | `list[Image]` | Extra frames. Each item may be single- or multi-frame. |
| `duration` | `int` \| `list` \| `tuple` | Display time in **milliseconds**. One value = constant; a list = per frame. |
| `loop` | `int` \| `None` | Loop count. **`0` = infinite**. Omitted / `None` → **does not loop**. |
| `disposal` | `int` \| `list` \| `tuple` | What to do with the frame after display (see below). |
| `transparency` | `int` | Transparent color index in the palette. |
| `optimize` | `bool` | Compresses the palette and marks unchanged pixels as transparent (often `True` by default). |
| `palette` | `bytes` \| `bytearray` \| `ImagePalette` | RGBRGB… palette (≤ 768 bytes) or `ImagePalette`. |
| `include_color_table` | `bool` | Include a local color table. |
| `interlace` | `bool` | Interlacing. Default: yes, unless width or height < 16. |
| `comment` | `str` / bytes | GIF comment. |

## `disposal` (official values)

| Value | Meaning |
|-------|---------|
| `0` | Unspecified |
| `1` | Do not dispose (leave the frame) |
| `2` | **Restore to background color** (recommended for transparent animations) |
| `3` | Restore previous content |

For a logo on a transparent background, almost always:

```python
disposal=2,
optimize=False,   # avoids transparency bugs / “eaten” pixels
```

## Quick `save()` reference

```python
im.save(
    "out.gif",
    format="GIF",          # optional if the extension is .gif
    save_all=True,         # required for multi-frame
    append_images=[...],   # frames 1..n
    duration=40,           # ms (int or list)
    loop=0,                # 0 = forever
    disposal=2,            # clear to background
    transparency=255,      # transparent palette index
    optimize=False,        # safer with transparency
    palette=None,          # optional
    interlace=False,       # optional
    comment="meta-skills", # optional
)
```

Based on Pillow **12.3.0** (handbook *Image file formats → GIF*). GIF options rarely change across majors, but `optimize` / transparency details can.
