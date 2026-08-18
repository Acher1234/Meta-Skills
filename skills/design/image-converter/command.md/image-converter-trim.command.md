# image-converter-trim — Commands

Trim extra background around a logo with **Pillow**. Implemented in `scripts/trim.py` (`Trim`).

Flood-fills the border color (with `--tolerance` for JPEG artifacts), crops to the logo, then adds `--padding`. PNG/WebP keep a transparent pad; JPG flattens onto white. Confirm before `--force` overwrite.

All commands: `~/.meta-skills/.venv/bin/python scripts/cli.py …` from `~/.meta-skills/skills/design/image-converter`.

| Slash | CLI | Description |
|-------|-----|-------------|
| `/image-converter_trim` | `python scripts/cli.py trim {INPUT} -o {OUTPUT} --padding {PADDING}` | Trim background and pad |

Placeholders: `{INPUT}`, `{OUTPUT}`, `{PADDING}`. Optional: `--tolerance {TOLERANCE}` (default 24), `--force`. Default output: `{stem}-trim.png`.
