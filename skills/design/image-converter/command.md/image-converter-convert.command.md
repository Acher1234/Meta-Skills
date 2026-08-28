# image-converter-convert — Commands

Convert WebP, PNG, JPG, and **SVG / SVGZ**. Implemented in `scripts/convert.py`.

- **SVG → SVG** (`--to svg`): vector copy (optional `--svg-width` / `--svg-scale`). Does not rasterize.
- **SVG → PNG/JPG/WebP**: rasterize (`scripts/svg.py`) then Pillow `Image.save`.
- **Raster → SVG**: wrap as SVG with an embedded PNG (`<image href="data:image/png;base64,…">`), not a vector trace.

`--to` is `webp`, `png`, `jpg`, or `svg`. `--output` / `-o` defaults to the same stem + new extension. JPG flattens transparency onto `--background` (default `#ffffff`). Confirm before `--force` overwrite.

When rasterizing SVG: `--svg-dpi` (default 96), `--svg-width` (px), `--svg-scale` (default 1). Success JSON includes `input_kind` and, for SVG, `svg_backend` (`vector` | raster backend | `embed`) + `svg_px` when sized.

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/design/image-converter`.

| Slash | CLI | Description |
|-------|-----|-------------|
| `/image-converter_convert_webp` | `python scripts/cli.py convert {INPUT} --to webp --output {OUTPUT}` | Convert to WebP |
| `/image-converter_convert_png` | `python scripts/cli.py convert {INPUT} --to png --output {OUTPUT}` | Convert to PNG |
| `/image-converter_convert_jpg` | `python scripts/cli.py convert {INPUT} --to jpg --output {OUTPUT}` | Convert to JPG |
| `/image-converter_convert_svg` | `python scripts/cli.py convert {INPUT} --to svg -o {OUTPUT}` | Convert to SVG (vector if input is SVG) |
| `/image-converter_convert_svg_png` | `python scripts/cli.py convert {INPUT} --to png -o {OUTPUT}` | Rasterize SVG → PNG |

Placeholders: `{INPUT}`, `{OUTPUT}`. Optional: `--quality {QUALITY}` (JPG/WebP, default 85), `--background {HEX}`, `--force`, `--svg-dpi {DPI}`, `--svg-width {PX}`, `--svg-scale {N}`.

Examples:

```bash
python scripts/cli.py convert logo.svg --to svg
python scripts/cli.py convert logo.svg --to png
```
