# Duration, FPS, loop

```text
duration_ms = 1000 / fps
```

| FPS | `duration` |
|-----|------------|
| 10 | 100 |
| 20 | 50 |
| 24 | ≈ 41 |
| 30 | ≈ 33 |

Per-frame durations:

```python
duration=[40, 40, 40, 200, 40, 40]  # one “pause” frame
```

`loop`:

| Value | Effect |
|-------|--------|
| `0` | Infinite loop |
| `1` | Play once then stop (reader-dependent) |
| omitted / `None` | **Does not loop** (Pillow docs) |
