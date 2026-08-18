# image-converter-thumbnail — Commands

Make a thumbnail with **Pillow** (`Image.thumbnail`). Implemented in `scripts/thumbnail.py` (`Thumbnail`).

`--size` is the max width **and** height; aspect ratio is kept and the image is never enlarged. Default output: `{stem}-thumb{ext}`. Confirm before `--force` overwrite.

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/design/image-converter`.

| Slash | CLI | Description |
|-------|-----|-------------|
| `/image-converter_thumbnail` | `python scripts/cli.py thumbnail {INPUT} --size {SIZE}` | Make a thumbnail |

Placeholders: `{INPUT}`, `{SIZE}`. Optional: `-o {OUTPUT}`, `--quality {QUALITY}`, `--force`.
