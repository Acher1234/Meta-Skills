# Transparency pitfalls

1. **No partial alpha** — only one fully transparent index.
2. **`disposal=2`** — otherwise frames stack (ghosting).
3. **`optimize=False`** — the optimizer can mark “unchanged” pixels as transparent and break the anim.
4. **Do not use light gray for a “transparent” shadow** on a dark background: it becomes a white shadow. Prefer a **solid black** block with variable size, or black dither.
5. All frames should share the **same size** (logical screen).

## Faking more / less transparent shadows

GIF cannot store partial alpha. Options:

| Technique | Look | When |
|-----------|------|------|
| **Solid black** ellipse, variable size | Clean | Ground shadow (recommended) |
| Gray | Looks white on dark UIs | Avoid for shadows |
| Dither (Bayer, etc.) | Black dots | If grain is acceptable |
