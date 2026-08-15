# Alternatives when GIF is the limit

| Need | Format |
|------|--------|
| True partial transparency + animation | **APNG** (`save_all=True` on PNG) or animated **WebP** |
| Better quality / size | WebP / MP4 + `ffmpeg` |
| Simple sharing | GIF is still the most compatible |

Animated WebP (if compiled in):

```python
frames[0].save(
    "out.webp",
    save_all=True,
    append_images=frames[1:],
    duration=40,
    loop=0,
    lossless=True,
)
```

## Official docs

1. GIF format: https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#gif
2. `Image.save`: https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.save
3. `ImageSequence`: https://pillow.readthedocs.io/en/stable/reference/ImageSequence.html
4. Concepts (modes `P`, `RGBA`, …): https://pillow.readthedocs.io/en/stable/handbook/concepts.html
5. `ImageDraw`: https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html
6. `ImageFilter`: https://pillow.readthedocs.io/en/stable/reference/ImageFilter.html
7. `ImagePalette`: https://pillow.readthedocs.io/en/stable/reference/ImagePalette.html
