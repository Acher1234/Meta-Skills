# Origin

## Pattern B — first-party / API docs (no upstream skill tree)

Pillow image conversion — WebP, PNG, JPG. SVG is a first-class format: SVG→SVG convert/resize keeps vectors (width/height + viewBox). SVG→raster uses cairosvg (preferred) or svglib+reportlab painted with Pillow when Cairo is missing. Raster→SVG embeds a PNG, not a trace.

- Formats: [Image file formats](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html)
- Save: [Image.save](https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.save)
- SVG: [CairoSVG](https://cairosvg.org/), [svglib](https://pypi.org/project/svglib/)

Auth: none.
