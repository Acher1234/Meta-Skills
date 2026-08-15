# What a GIF is in Pillow

From the official docs:

| Point | Detail |
|-------|--------|
| Versions read | GIF87a and GIF89a |
| Writing | GIF87a by default; GIF89a when GIF89a features are used |
| Compression | LZW |
| Mode on open | `L` (grayscale) or `P` (palette, max **256 colors**) |
| Later frames | A `P` frame may become `RGB` / `RGBA` (each frame can have its own palette) |
| Transparency | **1 palette index** is transparent (not 0–255 alpha like PNG) |

**No true partial transparency** in a GIF. For a “30% / 70%” shadow, fake it (size, gray, or dither) — the format does not store partial alpha.
