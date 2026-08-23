"""Paint ReportLab drawings to Pillow images (cairo-free svglib fallback)."""

from __future__ import annotations

from typing import Any

from PIL import Image, ImageDraw, ImageFont
from reportlab.graphics.shapes import (
    Circle,
    Drawing,
    Ellipse,
    Group,
    Line,
    Path,
    Polygon,
    PolyLine,
    Rect,
    String,
    _CLOSEPATH,
    _CURVETO,
    _LINETO,
    _MOVETO,
)
from reportlab.graphics.transform import mmult, transformPoint
from reportlab.lib.colors import toColor

_IDENTITY = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def drawing_to_pil(drawing: Drawing, width: int, height: int) -> Image.Image:
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")
    flip = (1.0, 0.0, 0.0, -1.0, 0.0, float(height))
    ctm = mmult(flip, tuple(drawing.transform or _IDENTITY))
    bg = getattr(drawing, "background", None)
    if bg is not None:
        _paint(bg, draw, ctm)
    for child in drawing.contents:
        _paint(child, draw, ctm)
    return img


def _paint(node: Any, draw: ImageDraw.ImageDraw, ctm: tuple) -> None:
    if isinstance(node, Group):
        child_ctm = mmult(ctm, tuple(node.transform or _IDENTITY))
        for child in node.contents:
            _paint(child, draw, child_ctm)
        return
    if isinstance(node, Rect):
        x, y, w, h = node.x, node.y, node.width, node.height
        pts = [
            transformPoint(ctm, (x, y)),
            transformPoint(ctm, (x + w, y)),
            transformPoint(ctm, (x + w, y + h)),
            transformPoint(ctm, (x, y + h)),
        ]
        _fill_stroke(node, draw, pts, closed=True, scale=_scale(ctm))
        return
    if isinstance(node, Circle):
        pts = _ellipse_pts(node.cx, node.cy, node.r, node.r, ctm)
        _fill_stroke(node, draw, pts, closed=True, scale=_scale(ctm))
        return
    if isinstance(node, Ellipse):
        pts = _ellipse_pts(node.cx, node.cy, node.rx, node.ry, ctm)
        _fill_stroke(node, draw, pts, closed=True, scale=_scale(ctm))
        return
    if isinstance(node, Line):
        pts = [transformPoint(ctm, (node.x1, node.y1)), transformPoint(ctm, (node.x2, node.y2))]
        _stroke(node, draw, pts, closed=False, scale=_scale(ctm))
        return
    if isinstance(node, Polygon):
        _fill_stroke(node, draw, _pairs(node.points, ctm), closed=True, scale=_scale(ctm))
        return
    if isinstance(node, PolyLine):
        _stroke(node, draw, _pairs(node.points, ctm), closed=False, scale=_scale(ctm))
        return
    if isinstance(node, Path):
        _paint_path(node, draw, ctm)
        return
    if isinstance(node, String):
        _paint_string(node, draw, ctm)


def _paint_path(node: Path, draw: ImageDraw.ImageDraw, ctm: tuple) -> None:
    subpaths: list[list[tuple[float, float]]] = []
    closed_flags: list[bool] = []
    current: list[tuple[float, float]] = []
    start: tuple[float, float] | None = None
    last: tuple[float, float] | None = None
    points = node.points
    i = 0
    for op in node.operators:
        if op == _MOVETO:
            if current:
                subpaths.append(current)
                closed_flags.append(False)
            last = start = transformPoint(ctm, (points[i], points[i + 1]))
            i += 2
            current = [last]
        elif op == _LINETO:
            last = transformPoint(ctm, (points[i], points[i + 1]))
            i += 2
            current.append(last)
        elif op == _CURVETO:
            p1 = transformPoint(ctm, (points[i], points[i + 1]))
            p2 = transformPoint(ctm, (points[i + 2], points[i + 3]))
            p3 = transformPoint(ctm, (points[i + 4], points[i + 5]))
            i += 6
            current.extend(_cubic(last or p1, p1, p2, p3)[1:])
            last = p3
        elif op == _CLOSEPATH:
            if current and start is not None:
                current.append(start)
                subpaths.append(current)
                closed_flags.append(True)
                current = []
                last = start
    if current:
        subpaths.append(current)
        closed_flags.append(False)

    scale = _scale(ctm)
    fill = _rgba(getattr(node, "fillColor", None), getattr(node, "fillOpacity", None))
    if fill:
        for sp in subpaths:
            if len(sp) >= 3:
                draw.polygon(_int_pts(sp), fill=fill)
    for sp, closed in zip(subpaths, closed_flags):
        _stroke(node, draw, sp, closed=closed, scale=scale)


def _paint_string(node: String, draw: ImageDraw.ImageDraw, ctm: tuple) -> None:
    fill = _rgba(getattr(node, "fillColor", None))
    if not fill or not node.text:
        return
    x, y = transformPoint(ctm, (node.x, node.y))
    size = max(8, int(round(float(node.fontSize or 12) * _scale(ctm))))
    font = _font(size)
    anchor = {"start": "ls", "middle": "ms", "end": "rs"}.get(getattr(node, "textAnchor", None), "ls")
    try:
        draw.text((x, y), node.text, fill=fill, font=font, anchor=anchor)
    except (TypeError, ValueError):
        draw.text((x, y), node.text, fill=fill, font=font)


def _fill_stroke(
    node: Any,
    draw: ImageDraw.ImageDraw,
    pts: list[tuple[float, float]],
    *,
    closed: bool,
    scale: float,
) -> None:
    fill = _rgba(getattr(node, "fillColor", None), getattr(node, "fillOpacity", None))
    if fill and len(pts) >= 3:
        draw.polygon(_int_pts(pts), fill=fill)
    _stroke(node, draw, pts, closed=closed, scale=scale)


def _stroke(
    node: Any,
    draw: ImageDraw.ImageDraw,
    pts: list[tuple[float, float]],
    *,
    closed: bool,
    scale: float,
) -> None:
    stroke = _rgba(getattr(node, "strokeColor", None), getattr(node, "strokeOpacity", None))
    sw = float(getattr(node, "strokeWidth", 0) or 0)
    if not stroke or sw <= 0 or len(pts) < 2:
        return
    seq = list(pts)
    if closed and seq[0] != seq[-1]:
        seq.append(seq[0])
    draw.line(_int_pts(seq), fill=stroke, width=max(1, int(round(sw * scale))), joint="curve")


def _ellipse_pts(cx: float, cy: float, rx: float, ry: float, ctm: tuple) -> list[tuple[float, float]]:
    from math import cos, pi, sin

    pts = []
    for i in range(48):
        t = 2 * pi * i / 48
        pts.append(transformPoint(ctm, (cx + rx * cos(t), cy + ry * sin(t))))
    return pts


def _pairs(values: list[float], ctm: tuple) -> list[tuple[float, float]]:
    return [transformPoint(ctm, (values[i], values[i + 1])) for i in range(0, len(values) - 1, 2)]


def _cubic(
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    p3: tuple[float, float],
    steps: int = 16,
) -> list[tuple[float, float]]:
    pts = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        x = u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1]
        pts.append((x, y))
    return pts


def _int_pts(pts: list[tuple[float, float]]) -> list[tuple[int, int]]:
    return [(int(round(x)), int(round(y))) for x, y in pts]


def _scale(ctm: tuple) -> float:
    sx = (ctm[0] ** 2 + ctm[1] ** 2) ** 0.5
    sy = (ctm[2] ** 2 + ctm[3] ** 2) ** 0.5
    return max(0.01, (sx + sy) / 2)


def _rgba(color: Any, opacity: float | None = None) -> tuple[int, int, int, int] | None:
    if color is None:
        return None
    try:
        c = toColor(color)
    except Exception:
        return None
    alpha = float(getattr(c, "alpha", 1.0) or 0)
    if opacity is not None:
        alpha *= float(opacity)
    if alpha <= 0:
        return None
    return (
        int(round(float(c.red) * 255)),
        int(round(float(c.green) * 255)),
        int(round(float(c.blue) * 255)),
        int(round(min(1.0, alpha) * 255)),
    )


def _font(size: int) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
    for path in (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "Arial.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()
