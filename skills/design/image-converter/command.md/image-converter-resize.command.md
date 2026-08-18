# image-converter-resize — Commands

Resize WebP, PNG, and JPG with **Pillow**. Implemented in `scripts/resize.py` (`Resize`).

Need `--width` and/or `--height`. One dimension keeps aspect ratio. Both: `--fit contain` (default, fit inside), `cover` (crop to fill), or `stretch`. `--output` defaults to `{stem}-{w}x{h}{ext}`. Confirm before `--force` overwrite.

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/design/image-converter`.

| Slash | CLI | Description |
|-------|-----|-------------|
| `/image-converter_resize` | `python scripts/cli.py resize {INPUT} --width {WIDTH} --height {HEIGHT} --output {OUTPUT}` | Resize an image |
| `/image-converter_resize_width` | `python scripts/cli.py resize {INPUT} --width {WIDTH} --output {OUTPUT}` | Resize by width (keep ratio) |
| `/image-converter_resize_height` | `python scripts/cli.py resize {INPUT} --height {HEIGHT} --output {OUTPUT}` | Resize by height (keep ratio) |

Placeholders: `{INPUT}`, `{OUTPUT}`, `{WIDTH}`, `{HEIGHT}`. Optional: `--fit contain|cover|stretch`, `--quality {QUALITY}`, `--force`.
