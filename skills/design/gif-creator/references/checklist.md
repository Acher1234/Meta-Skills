# Anti-bug checklist

- [ ] `save_all=True` + `append_images=frames[1:]`
- [ ] `loop=0` for an infinite loop
- [ ] `duration` in **ms**, not seconds
- [ ] `disposal=2` for a transparent background
- [ ] `optimize=False` if transparency looks wrong
- [ ] Frames in mode `P` with `transparency=<index>`
- [ ] Same size for every frame
- [ ] Shadow = **black**, not gray (otherwise a “white shadow”)
- [ ] Do not expect partial alpha in a GIF
