# image-converter

Convert still images between WebP, PNG, JPG, and SVG. SVG → SVG stays vector. Rasterize only for PNG/JPG/WebP (or trim). No credentials.

```bash
cd ~/.meta-skills/skills/design/image-converter
~/.meta-skills/install.sh pip init .
python scripts/cli.py svg-check
python scripts/cli.py convert {INPUT} --to webp --output {OUTPUT}
python scripts/cli.py convert {INPUT} --to png --output {OUTPUT}
python scripts/cli.py convert {INPUT} --to jpg --output {OUTPUT}
python scripts/cli.py convert {INPUT} --to svg --output {OUTPUT}
python scripts/cli.py convert logo.svg --to svg
python scripts/cli.py convert logo.svg --to png
python scripts/cli.py resize logo.svg --width {WIDTH}
python scripts/cli.py resize {INPUT} --width {WIDTH} --height {HEIGHT} --output {OUTPUT}
python scripts/cli.py trim logo-raw.jpg -o logo-clean.png --padding 10
python scripts/cli.py thumbnail photo.jpg --size 200
```
