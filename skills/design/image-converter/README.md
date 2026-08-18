# image-converter

Convert still images between WebP, PNG, and JPG with Pillow. No credentials.

```bash
cd ~/.meta-skills/skills/design/image-converter
~/.meta-skills/install.sh pip init .
python scripts/cli.py convert {INPUT} --to webp --output {OUTPUT}
python scripts/cli.py convert {INPUT} --to png --output {OUTPUT}
python scripts/cli.py convert {INPUT} --to jpg --output {OUTPUT}
python scripts/cli.py resize {INPUT} --width {WIDTH} --height {HEIGHT} --output {OUTPUT}
python scripts/cli.py trim logo-raw.jpg -o logo-clean.png --padding 10
python scripts/cli.py thumbnail photo.jpg --size 200
```
