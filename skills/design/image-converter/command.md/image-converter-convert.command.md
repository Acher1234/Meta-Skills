# image-converter-convert — Commands

Convert WebP, PNG, and JPG with **Pillow** (`Image.open` / `Image.save`). Implemented in `scripts/convert.py`.

`--to` is `webp`, `png`, or `jpg`. `--output` defaults to the same stem + new extension. JPG flattens transparency onto `--background` (default `#ffffff`). Confirm before `--force` overwrite.

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/design/image-converter`.

| Slash | CLI | Description |
|-------|-----|-------------|
| `/image-converter_convert_webp` | `python scripts/cli.py convert {INPUT} --to webp --output {OUTPUT}` | Convert to WebP |
| `/image-converter_convert_png` | `python scripts/cli.py convert {INPUT} --to png --output {OUTPUT}` | Convert to PNG |
| `/image-converter_convert_jpg` | `python scripts/cli.py convert {INPUT} --to jpg --output {OUTPUT}` | Convert to JPG |

Placeholders: `{INPUT}`, `{OUTPUT}`. Optional: `--quality {QUALITY}` (JPG/WebP, default 85), `--background {HEX}`, `--force`.
