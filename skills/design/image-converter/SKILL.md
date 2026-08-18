---
name: image-converter
description: >-
  Convert, resize, trim, and thumbnail images (WebP, PNG, JPG) with Pillow. Use
  when the user asks to convert an image, resize, trim a logo, make a
  thumbnail, pick a web format, export WebP/PNG/JPG, or invokes
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

Convert still images between **WebP**, **PNG**, and **JPG** with **Pillow** (`Image.open` / `Image.save`).

## When to use

Trigger phrases: "convert this image", "resize this image", "trim this logo", "make a thumbnail", "export as WebP", "PNG to JPG", "best format for a hero image", `/image-converter_*`.

Library: `~/.meta-skills/skills/design/image-converter/`. Python: `~/.meta-skills/.venv/bin/python`.

## Output Format Guide

| Use case | Format | Why |
|----------|--------|-----|
| Photos, hero images | WebP | Best compression, wide browser support |
| Logos, icons (need transparency) | PNG | Lossless, supports alpha |
| Fallback for older browsers | JPG | Universal support |
| Thumbnails | WebP or JPG | Small file size priority |
| OG cards | PNG | Social platforms handle PNG best |

Pick `--to` from this table, then run convert.

## image-converter-convert

Convert `{INPUT}` to WebP, PNG, or JPG.
Open the command file for `{INPUT}`, `{OUTPUT}`, `--quality`, `--background`.

Commands → `~/.meta-skills/skills/design/image-converter/command.md/image-converter-convert.command.md`

## image-converter-resize

Resize `{INPUT}` with `--width` / `--height` (Pillow LANCZOS).
Open the command file for `{WIDTH}`, `{HEIGHT}`, `--fit contain|cover|stretch`.

Commands → `~/.meta-skills/skills/design/image-converter/command.md/image-converter-resize.command.md`

## image-converter-trim

Trim background around a logo (`{INPUT}` → `{OUTPUT}`), then pad.
Open the command file for `-o`, `--padding`, `--tolerance`.

Commands → `~/.meta-skills/skills/design/image-converter/command.md/image-converter-trim.command.md`

## image-converter-thumbnail

Thumbnail `{INPUT}` into a `{SIZE}×{SIZE}` box (aspect kept, no upscale).
Open the command file for `--size` and `-o`.

Commands → `~/.meta-skills/skills/design/image-converter/command.md/image-converter-thumbnail.command.md`

## How to run

1. First run: `cd ~/.meta-skills/skills/design/image-converter && ~/.meta-skills/install.sh pip init .` (installs Pillow into `~/.meta-skills/.venv`).
2. Map `/image-converter_<…>` → `~/.meta-skills/.venv/bin/python scripts/cli.py …`; return JSON.

## Notes

- Confirm the output path with the user before `--force` overwrite.
- JPG has no alpha — transparency is flattened onto `--background` (default `#ffffff`).
- No credentials required.
- Docs: [Pillow image file formats](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html).
