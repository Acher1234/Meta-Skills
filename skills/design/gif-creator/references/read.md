# Read an existing GIF

Print metadata as JSON:

```python
from PIL import Image, ImageSequence
import json

with Image.open("anim.gif") as im:
    info = {
        "n_frames": getattr(im, "n_frames", 1),
        "size": list(im.size),
        "mode": im.mode,
        "info": {k: im.info.get(k) for k in (
            "background", "transparency", "version", "duration", "loop", "comment"
        ) if k in im.info},
        "frame_durations": [f.info.get("duration") for f in ImageSequence.Iterator(im)],
    }
    print(json.dumps(info, indent=2, default=str))
```

## `im.info` on open

| Key | Content |
|-----|---------|
| `background` | Background color index |
| `transparency` | Transparent index (absent if opaque) |
| `version` | `"GIF87a"` or `"GIF89a"` |
| `duration` | Current frame ms (may be absent) |
| `loop` | `0` = infinite (may be absent) |
| `comment` | Comment |
| `extension` | Application extension data |

## Walk frames

**A — `seek` / `tell`:**

```python
from PIL import Image

with Image.open("anim.gif") as im:
    print(im.n_frames, im.info)
    im.seek(0)
    while True:
        im.save(f"frame_{im.tell():03d}.png")
        try:
            im.seek(im.tell() + 1)
        except EOFError:
            break
```

**B — `ImageSequence.Iterator` (recommended):**

```python
from PIL import Image, ImageSequence

with Image.open("anim.gif") as im:
    for i, frame in enumerate(ImageSequence.Iterator(im)):
        frame.save(f"frame_{i:03d}.png")
```

**C — `ImageSequence.all_frames`:**

```python
from PIL import Image, ImageSequence

with Image.open("anim.gif") as im:
    frames = ImageSequence.all_frames(im)  # list[Image]
    frames = ImageSequence.all_frames(im, func=lambda f: f.convert("RGBA"))
```

## Palette loading strategy

```python
from PIL import GifImagePlugin

# Default: P → RGB/RGBA only after the first frame
GifImagePlugin.LOADING_STRATEGY = (
    GifImagePlugin.LoadingStrategy.RGB_AFTER_FIRST
)

# Always convert to RGB/RGBA
GifImagePlugin.LOADING_STRATEGY = (
    GifImagePlugin.LoadingStrategy.RGB_ALWAYS
)

# Stay in P while the global palette allows it
GifImagePlugin.LOADING_STRATEGY = (
    GifImagePlugin.LoadingStrategy.RGB_AFTER_DIFFERENT_PALETTE_ONLY
)
```
