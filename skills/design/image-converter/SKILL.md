---
name: image-converter
description: >-
  Convert, resize, trim, and thumbnail images (WebP, PNG, JPG, SVG). SVG→SVG
  stays vector. Use when the user asks to convert an image, convert this svg,
  svg to png, svg to svg, logo svg, resize an svg, trim a logo, make a
  thumbnail, pick a web format, export WebP/PNG/JPG/SVG, or invokes
  /image-converter_*.
disable-model-invocation: true
---

### TO COPY

# image-converter

Per-workspace registration slice. No credentials.

## Working directory

Placeholders changed by `/meta-skills` at copy time (NAME => {PLACEHOLDER}):

IS_GLOBAL => {IS_GLOBAL}
TYPE_OF_AI_TOOLS => {TYPE_OF_AI_TOOLS}
SKILL_PATH => {SKILL_PATH}

```bash
export CURRENT_SKILL_DIRECTORY="{SKILL_PATH}"
```

##### END TO COPY

# image-converter

Convert still images between **WebP**, **PNG**, **JPG**, and **SVG**. **SVG → SVG** (convert / resize / thumbnail) stays **vector** (width/height + viewBox). Rasterize only when the output is WebP / PNG / JPG (or trim).

## When to use

Trigger phrases: "convert this image", "convert this svg", "svg to png", "svg to svg", "logo svg", "resize this svg", "resize this image", "trim this logo", "make a thumbnail", "export as WebP", "PNG to JPG", "best format for a hero image", `/image-converter_*`.

Library: `~/.meta-skills/skills/design/image-converter/`. Python: `~/.meta-skills/.venv/bin/python`.

## Output Format Guide

| Use case | Format | Why |
|----------|--------|-----|
| Photos, hero images | WebP | Best compression, wide browser support |
| Logos, icons (need transparency) | PNG | Lossless, supports alpha |
| Logos that must stay vector | SVG | Convert/resize without rasterizing |
| Fallback for older browsers | JPG | Universal support |
| Thumbnails | WebP or JPG | Small file size priority |
| OG cards | PNG | Social platforms handle PNG best |

Pick `--to` from this table, then run convert.

## image-converter-convert

Convert `{INPUT}` (WebP / PNG / JPG / SVG) to WebP, PNG, JPG, or SVG.
Open the command file for `{INPUT}`, `{OUTPUT}`, `--quality`, `--background`, `--svg-dpi`.

Commands → `~/.meta-skills/skills/design/image-converter/command.md/image-converter-convert.command.md`

## image-converter-resize

Resize `{INPUT}` with `--width` / `--height`. SVG → SVG stays vector; rasters use Pillow LANCZOS.
Open the command file for `{WIDTH}`, `{HEIGHT}`, `--fit contain|cover|stretch`.

Commands → `~/.meta-skills/skills/design/image-converter/command.md/image-converter-resize.command.md`

## image-converter-trim

Trim background around a logo (`{INPUT}` → `{OUTPUT}`), then pad. Raster operation (default PNG).
Open the command file for `-o`, `--padding`, `--tolerance`.

Commands → `~/.meta-skills/skills/design/image-converter/command.md/image-converter-trim.command.md`

## image-converter-thumbnail

Thumbnail `{INPUT}` into a `{SIZE}×{SIZE}` box (aspect kept, no upscale). SVG stays SVG.
Open the command file for `--size` and `-o`.

Commands → `~/.meta-skills/skills/design/image-converter/command.md/image-converter-thumbnail.command.md`

## image-converter-svg-check

JSON probe of SVG raster backends (cairosvg / Cairo / svglib / PATH). Used when converting SVG → PNG/JPG/WebP.

Commands → `~/.meta-skills/skills/design/image-converter/command.md/image-converter-svg-check.command.md`

## How to run

1. First run: `cd ~/.meta-skills/skills/design/image-converter && ~/.meta-skills/install.sh pip init .` (Pillow + SVG rasterizers into `~/.meta-skills/.venv`).
2. Map `/image-converter_<…>` → `~/.meta-skills/.venv/bin/python scripts/cli.py …`; return JSON.
3. Optional: `python scripts/cli.py svg-check` — JSON probe of cairosvg / Cairo / svglib / PATH tools.

## Notes

- Confirm the output path with the user before `--force` overwrite.
- JPG has no alpha — transparency is flattened onto `--background` (default `#ffffff`).
- SVG → PNG/JPG/WebP: Pillow cannot decode SVG; the skill rasterizes first (cairosvg if Cairo is present, else svglib+reportlab). Cairo is optional quality; `brew install cairo` / `apt install libcairo2`.
- Raster → SVG embeds a PNG in an `<image>` (not a vector trace).
- svglib is good enough for logos when rasterizing without Cairo; filters, some CSS, and text may differ from cairosvg.
- No credentials required.
- Docs: [Pillow image file formats](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html), [CairoSVG](https://cairosvg.org/).
