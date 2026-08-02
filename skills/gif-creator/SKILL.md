---
name: gif-creator
description: >-
  Generate animated GIFs with Pillow (palette, binary transparency, toss/lift
  animations, frame folders). Use when the user asks to create a GIF, animate a
  logo, convert frames to GIF, inspect a GIF, or invokes /gif-creator_*.
disable-model-invocation: true
---

# gif-creator

Generate animated GIFs with **Pillow** (GIF87a/GIF89a, LZW, max 256 colors, one transparent palette index). Full Pillow 12.3.0 guide: [`references/pillow-gif-guide.md`](references/pillow-gif-guide.md).

## When to use

Trigger phrases: "create a GIF", "animate this logo", "make a toss GIF", "frames to GIF", "GIF transparency", `/gif-creator_toss`, `/gif-creator_from-frames`, `/gif-creator_info`.

## Working directory

Placeholders changed by `/meta-skills` at copy time (NAME => {PLACEHOLDER}):

IS_GLOBAL => {IS_GLOBAL}
TYPE_OF_AI_TOOLS => {TYPE_OF_AI_TOOLS}
SKILL_PATH => {SKILL_PATH}

Before `cd`, export the local skill directory and source `.env` files (shared library, then this skill dir):

```bash
export CURRENT_SKILL_DIRECTORY="{SKILL_PATH}"
export IS_GLOBAL="{IS_GLOBAL}"
export TYPE_OF_AI_TOOLS="{TYPE_OF_AI_TOOLS}"
[ -f "$HOME/.meta-skills/.env" ] && set -a && . "$HOME/.meta-skills/.env" && set +a
[ -f "{SKILL_PATH}/.env" ] && set -a && . "{SKILL_PATH}/.env" && set +a
cd "{SKILL_PATH}"
```

Always `cd` into `{SKILL_PATH}` before running scripts. Prefer the shared interpreter: `~/.meta-skills/.venv/bin/python` (run from the library skill tree when scripts live under `~/.meta-skills/skills/gif-creator/`).

## Slash commands

| Slash | CLI | Description |
|-------|-----|-------------|
| `/gif-creator_toss` | `python scripts/create_gif.py toss SRC DEST [--max-width N] [--lift N] [--fps N] [--duration S]` | Logo rises → spins → falls (transparent GIF) |
| `/gif-creator_from-frames` | `python scripts/create_gif.py from-frames DIR DEST [--fps N] [--duration-ms MS] [--loop N]` | Build GIF from images in a directory (sorted by name) |
| `/gif-creator_info` | `python scripts/create_gif.py info PATH` | Print GIF metadata / frame durations as JSON |
| `/gif-creator_install-deps` | `~/.meta-skills/install.sh pip init .` | Install Pillow into the shared venv |

## How to run

1. `cd` to the [working directory](#working-directory) that exists on this machine (after exports). Prefer library path: `~/.meta-skills/skills/gif-creator`.
2. First Python run: `cd ~/.meta-skills/skills/gif-creator && ~/.meta-skills/install.sh pip init .`
3. Run the CLI; parse JSON stdout when available.

```bash
cd ~/.meta-skills/skills/gif-creator
~/.meta-skills/.venv/bin/python scripts/create_gif.py toss ./logo.png ./out.gif
```

## Critical GIF rules (Pillow)

- GIF has **no partial alpha** — one palette index is fully transparent.
- Save with `save_all=True`, `append_images=frames[1:]`, `loop=0`, `disposal=2`, `optimize=False` for transparent anims.
- Prefer a **solid black** shadow (size varies), not gray (looks white on dark UIs).
- Compose in `RGBA`, convert to mode `P` via `gif_utils.rgba_to_gif_frame` before save.
- Details + official option tables: [`references/pillow-gif-guide.md`](references/pillow-gif-guide.md).

## Notes

- Confirm output path with the user before overwriting an existing file.
- No credentials required for this skill.
- Prefer WebP/APNG only when the user needs true partial transparency (see guide §11).
