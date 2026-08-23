# image-converter-svg-check — Commands

Probe SVG raster backends (JSON). Exit 0 if at least one **Python** backend works (cairosvg+Cairo, or svglib+reportlab). Implemented in `scripts/svg.py`.

Reports: Python / Pillow versions, cairosvg importable, Cairo loadable, svglib usable, `rsvg-convert` / `magick` on PATH, `recommended_backend`. Does not brew-install anything.

If nothing can rasterize an SVG at convert time, the CLI exits non-zero with JSON: backends tried, `install.sh pip init .`, `brew install cairo` / `apt install libcairo2`.

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/design/image-converter`.

| Slash | CLI | Description |
|-------|-----|-------------|
| `/image-converter_svg-check` | `python scripts/cli.py svg-check` | JSON backend probe |
