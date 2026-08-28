"""Rasterize SVG/SVGZ to a Pillow RGBA image.

Backend order: cairosvg (Cairo) → svglib+reportlab (pip-only) → rsvg-convert → magick.
Cairo is optional. svglib is the required fallback after `install.sh pip init .`.
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
import shutil
import subprocess
import sys
from io import BytesIO
from pathlib import Path
from typing import Any, Callable, NoReturn
from xml.etree import ElementTree as ET

from PIL import Image

SVG_SUFFIXES = {".svg", ".svgz"}
DEFAULT_SVG_WIDTH = 1024
PIP_INIT = (
    "cd ~/.meta-skills/skills/design/image-converter && "
    "~/.meta-skills/install.sh pip init ."
)

_LEN = re.compile(
    r"^\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*(px|pt|pc|mm|cm|in|%)?\s*$",
    re.I,
)


def is_svg_path(path: Path) -> bool:
    return path.suffix.lower() in SVG_SUFFIXES


def add_svg_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--svg-dpi",
        type=float,
        default=96,
        help="SVG raster DPI (default: 96)",
    )
    parser.add_argument(
        "--svg-width",
        type=int,
        default=None,
        help="SVG raster width in pixels; height follows aspect/viewBox",
    )
    parser.add_argument(
        "--svg-scale",
        type=float,
        default=1.0,
        help="SVG raster scale (default: 1)",
    )


def svg_kwargs(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "svg_dpi": args.svg_dpi,
        "svg_width": args.svg_width,
        "svg_scale": args.svg_scale,
    }


def rasterize_svg(
    src: Path,
    *,
    dpi: float = 96,
    width: int | None = None,
    scale: float = 1.0,
    backends: tuple[str, ...] | None = None,
) -> Image.Image:
    if dpi <= 0:
        raise SystemExit("--svg-dpi must be > 0")
    if scale <= 0:
        raise SystemExit("--svg-scale must be > 0")
    if width is not None and width <= 0:
        raise SystemExit("--svg-width must be > 0")

    svg_bytes = _read_svg_bytes(src)
    px_w, px_h = _target_px(svg_bytes, dpi=dpi, width=width, scale=scale)
    chain = ("cairosvg", "svglib", "rsvg-convert", "magick") if backends is None else backends
    tried: list[str] = []
    errors: dict[str, str] = {}

    runners: dict[str, Callable[[], Image.Image]] = {
        "cairosvg": lambda: _raster_cairosvg(svg_bytes, px_w, px_h, dpi),
        "svglib": lambda: _raster_svglib(svg_bytes, px_w, px_h),
        "rsvg-convert": lambda: _raster_rsvg(src, px_w, px_h, dpi),
        "magick": lambda: _raster_magick(src, px_w, px_h, dpi),
    }

    for name in chain:
        run = runners.get(name)
        if run is None:
            continue
        if name == "rsvg-convert" and not shutil.which("rsvg-convert"):
            continue
        if name == "magick" and not shutil.which("magick"):
            continue
        tried.append(name)
        try:
            img = run()
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception as exc:
            errors[name] = _exc_msg(exc)
            continue
        img = img.convert("RGBA")
        img.info["_input_kind"] = "svg"
        img.info["_svg_backend"] = name
        img.info["_svg_px"] = [img.size[0], img.size[1]]
        img.info["_frames_read"] = 1
        return img

    _abort_no_backend(tried, errors)


def probe() -> dict[str, Any]:
    from PIL import __version__ as pillow_version

    cairosvg_importable, cairosvg_error = _try_import("cairosvg")
    cairo_ok, cairo_error = _cairo_loadable()
    svglib_ok, svglib_error = _svglib_usable()
    rsvg = bool(shutil.which("rsvg-convert"))
    magick = bool(shutil.which("magick"))

    cairosvg_ok = cairosvg_importable and cairo_ok
    python_ok = cairosvg_ok or svglib_ok
    if cairosvg_ok:
        recommended = "cairosvg"
    elif svglib_ok:
        recommended = "svglib"
    elif rsvg:
        recommended = "rsvg-convert"
    elif magick:
        recommended = "magick"
    else:
        recommended = None

    out: dict[str, Any] = {
        "ok": python_ok,
        "python": sys.version.split()[0],
        "executable": sys.executable,
        "pillow": pillow_version,
        "cairosvg_importable": cairosvg_importable,
        "cairo_loadable": cairo_ok,
        "svglib_importable": svglib_ok,
        "rsvg_convert": rsvg,
        "magick": magick,
        "recommended_backend": recommended,
    }
    if not cairo_ok and cairo_error:
        out["cairo_error"] = cairo_error
    if not cairosvg_importable and cairosvg_error:
        out["cairosvg_error"] = cairosvg_error
    if not svglib_ok and svglib_error:
        out["svglib_error"] = svglib_error
    if not python_ok:
        out["install"] = {
            "pip": PIP_INIT,
            "cairo_macos": "brew install cairo",
            "cairo_linux": "apt install libcairo2",
        }
    return out


def cmd_svg_check(_args: argparse.Namespace) -> int:
    data = probe()
    print(json.dumps(data, indent=2))
    return 0 if data["ok"] else 1


def register_svg_check(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser(
        "svg-check",
        help="Report SVG raster backends as JSON",
    )
    p.set_defaults(func=cmd_svg_check)


def _read_svg_bytes(src: Path) -> bytes:
    data = src.read_bytes()
    if src.suffix.lower() == ".svgz" or data[:2] == b"\x1f\x8b":
        data = gzip.decompress(data)
    return data


def _target_px(
    svg_bytes: bytes,
    *,
    dpi: float,
    width: int | None,
    scale: float,
) -> tuple[int, int]:
    intrinsic_w, intrinsic_h, aspect = _intrinsic_px(svg_bytes, dpi)
    if width is not None:
        w = width
        h = max(1, round(w / aspect)) if aspect else w
        return w, h
    if intrinsic_w and intrinsic_h:
        return max(1, round(intrinsic_w * scale)), max(1, round(intrinsic_h * scale))
    w = max(1, round(DEFAULT_SVG_WIDTH * scale))
    h = max(1, round(w / aspect)) if aspect else w
    return w, h


def _intrinsic_px(svg_bytes: bytes, dpi: float) -> tuple[float | None, float | None, float | None]:
    try:
        root = ET.fromstring(svg_bytes)
    except ET.ParseError:
        return None, None, None
    return _intrinsic_from_root(root, dpi)


def _intrinsic_from_root(root: ET.Element, dpi: float) -> tuple[float | None, float | None, float | None]:
    vb_w, vb_h = _viewbox_size(root)
    w = _length_px(root.get("width"), dpi)
    h = _length_px(root.get("height"), dpi)
    aspect = None
    if w and h:
        aspect = w / h
    elif vb_w and vb_h:
        aspect = vb_w / vb_h
        if w and not h:
            h = w / aspect
        elif h and not w:
            w = h * aspect
        elif not w and not h:
            w, h = vb_w * (dpi / 96.0), vb_h * (dpi / 96.0)
    return w, h, aspect


def planned_svg_size(
    src: Path,
    *,
    width: int | None = None,
    height: int | None = None,
    fit: str = "contain",
    scale: float = 1.0,
    dpi: float = 96,
    no_upscale: bool = False,
) -> tuple[int, int]:
    root = ET.fromstring(_read_svg_bytes(src))
    orig_w, orig_h, aspect = _intrinsic_from_root(root, dpi)
    if not orig_w or not orig_h:
        orig_w = float(DEFAULT_SVG_WIDTH)
        orig_h = orig_w / aspect if aspect else orig_w
    ow, oh = orig_w, orig_h
    if scale != 1.0 and width is None and height is None:
        ow, oh = ow * scale, oh * scale
    return _fitted_size(ow, oh, width, height, fit, no_upscale=no_upscale)


def copy_svg(src: Path, dest: Path) -> None:
    data = _read_svg_bytes(src)
    _write_svg_bytes(dest, data)


def resize_svg(
    src: Path,
    dest: Path,
    *,
    width: int | None = None,
    height: int | None = None,
    fit: str = "contain",
    scale: float = 1.0,
    dpi: float = 96,
    no_upscale: bool = False,
) -> tuple[int, int]:
    root = ET.fromstring(_read_svg_bytes(src))
    orig_w, orig_h, aspect = _intrinsic_from_root(root, dpi)
    if not orig_w or not orig_h:
        orig_w = float(DEFAULT_SVG_WIDTH)
        orig_h = orig_w / aspect if aspect else orig_w
    ow, oh = orig_w, orig_h
    if scale != 1.0 and width is None and height is None:
        ow, oh = ow * scale, oh * scale
    tw, th = _fitted_size(ow, oh, width, height, fit, no_upscale=no_upscale)
    _ensure_viewbox(root, orig_w, orig_h)
    root.set("width", str(tw))
    root.set("height", str(th))
    if width and height:
        if fit == "stretch":
            root.set("preserveAspectRatio", "none")
        elif fit == "cover":
            root.set("preserveAspectRatio", "xMidYMid slice")
        else:
            root.set("preserveAspectRatio", "xMidYMid meet")
    _write_svg_root(root, dest)
    return tw, th


def raster_image_to_svg(img: Image.Image, dest: Path) -> None:
    import base64

    prepared = img.convert("RGBA") if img.mode not in {"RGB", "RGBA", "L"} else img
    buf = BytesIO()
    prepared.save(buf, format="PNG", optimize=True)
    b64 = base64.standard_b64encode(buf.getvalue()).decode("ascii")
    w, h = prepared.size
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n'
        f'  <image href="data:image/png;base64,{b64}" width="{w}" height="{h}"/>\n'
        "</svg>\n"
    )
    dest.write_text(xml, encoding="utf-8")


def _fitted_size(
    ow: float,
    oh: float,
    width: int | None,
    height: int | None,
    fit: str,
    *,
    no_upscale: bool = False,
) -> tuple[int, int]:
    if width and not height:
        h = max(1, round(oh * width / ow))
        if no_upscale and width > ow:
            return max(1, round(ow)), max(1, round(oh))
        return width, h
    if height and not width:
        w = max(1, round(ow * height / oh))
        if no_upscale and height > oh:
            return max(1, round(ow)), max(1, round(oh))
        return w, height
    if not width and not height:
        return max(1, round(ow)), max(1, round(oh))
    assert width is not None and height is not None
    if fit == "stretch" or fit == "cover":
        return width, height
    scale = min(width / ow, height / oh)
    if no_upscale:
        scale = min(scale, 1.0)
    return max(1, round(ow * scale)), max(1, round(oh * scale))


def _ensure_viewbox(root: ET.Element, ow: float, oh: float) -> None:
    if root.get("viewBox") or root.get("viewbox"):
        return
    root.set("viewBox", f"0 0 {ow:g} {oh:g}")


def _write_svg_root(root: ET.Element, dest: Path) -> None:
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
    _write_svg_bytes(dest, ET.tostring(root, encoding="utf-8", xml_declaration=True))


def _write_svg_bytes(dest: Path, data: bytes) -> None:
    if dest.suffix.lower() == ".svgz":
        dest.write_bytes(gzip.compress(data))
        return
    dest.write_bytes(data)


def _viewbox_size(root: ET.Element) -> tuple[float | None, float | None]:
    raw = root.get("viewBox") or root.get("viewbox")
    if not raw:
        return None, None
    parts = raw.replace(",", " ").split()
    if len(parts) != 4:
        return None, None
    try:
        vb_w, vb_h = float(parts[2]), float(parts[3])
    except ValueError:
        return None, None
    if vb_w <= 0 or vb_h <= 0:
        return None, None
    return vb_w, vb_h


def _length_px(value: str | None, dpi: float) -> float | None:
    if not value:
        return None
    match = _LEN.match(value)
    if not match:
        return None
    amount = float(match.group(1))
    unit = (match.group(2) or "").lower()
    if unit == "%":
        return None
    inches = {
        "": amount / 96.0,
        "px": amount / 96.0,
        "pt": amount / 72.0,
        "pc": amount / 6.0,
        "in": amount,
        "mm": amount / 25.4,
        "cm": amount / 2.54,
    }.get(unit)
    if inches is None:
        return None
    px = inches * dpi
    return px if px > 0 else None


def _raster_cairosvg(svg_bytes: bytes, width: int, height: int, dpi: float) -> Image.Image:
    import cairosvg

    png = cairosvg.svg2png(
        bytestring=svg_bytes,
        dpi=dpi,
        output_width=width,
        output_height=height,
    )
    return _png_to_image(png)


def _raster_svglib(svg_bytes: bytes, width: int, height: int) -> Image.Image:
    from rlg_pil import drawing_to_pil
    from svglib.svglib import svg2rlg

    drawing = svg2rlg(BytesIO(svg_bytes))
    if drawing is None:
        raise RuntimeError("svglib could not parse SVG")
    dw, dh = float(drawing.width or 0), float(drawing.height or 0)
    if dw <= 0 or dh <= 0:
        drawing.width = width
        drawing.height = height
    else:
        drawing.scale(width / dw, height / dh)
        drawing.width = width
        drawing.height = height
    return drawing_to_pil(drawing, width, height)


def _raster_rsvg(src: Path, width: int, height: int, dpi: float) -> Image.Image:
    proc = subprocess.run(
        [
            "rsvg-convert",
            "--format",
            "png",
            f"--dpi-x={dpi}",
            f"--dpi-y={dpi}",
            "--width",
            str(width),
            "--height",
            str(height),
            str(src),
        ],
        capture_output=True,
        timeout=60,
        check=False,
    )
    if proc.returncode != 0:
        err = proc.stderr.decode("utf-8", errors="replace").strip() or f"exit {proc.returncode}"
        raise RuntimeError(err)
    return _png_to_image(proc.stdout)


def _raster_magick(src: Path, width: int, height: int, dpi: float) -> Image.Image:
    proc = subprocess.run(
        [
            "magick",
            "-density",
            str(dpi),
            "-background",
            "none",
            str(src),
            "-resize",
            f"{width}x{height}",
            "PNG:-",
        ],
        capture_output=True,
        timeout=60,
        check=False,
    )
    if proc.returncode != 0:
        err = proc.stderr.decode("utf-8", errors="replace").strip() or f"exit {proc.returncode}"
        raise RuntimeError(err)
    return _png_to_image(proc.stdout)


def _png_to_image(png: bytes) -> Image.Image:
    if not png:
        raise RuntimeError("raster backend returned empty PNG")
    img = Image.open(BytesIO(png))
    img.load()
    return img


def _try_import(name: str) -> tuple[bool, str | None]:
    try:
        __import__(name)
    except Exception as exc:
        return False, _exc_msg(exc)
    return True, None


def _cairo_loadable() -> tuple[bool, str | None]:
    try:
        import cairocffi

        _ = cairocffi.cairo
    except Exception as exc:
        return False, _exc_msg(exc)
    return True, None


def _svglib_usable() -> tuple[bool, str | None]:
    try:
        from rlg_pil import drawing_to_pil
        from svglib.svglib import svg2rlg

        drawing = svg2rlg(
            BytesIO(
                b'<svg xmlns="http://www.w3.org/2000/svg" width="8" height="8">'
                b'<rect width="8" height="8" fill="#ff0000"/></svg>'
            )
        )
        if drawing is None:
            return False, "svg2rlg returned None"
        img = drawing_to_pil(drawing, 8, 8)
        if img.mode != "RGBA" or img.size != (8, 8):
            return False, f"unexpected image {img.mode} {img.size}"
    except Exception as exc:
        return False, _exc_msg(exc)
    return True, None


def _exc_msg(exc: BaseException) -> str:
    msg = str(exc).strip() or type(exc).__name__
    if len(msg) > 400:
        return msg[:400] + "..."
    return msg


def _abort_no_backend(tried: list[str], errors: dict[str, str]) -> NoReturn:
    print(
        json.dumps(
            {
                "ok": False,
                "error": "no SVG raster backend available",
                "tried": tried,
                "errors": errors,
                "install": {
                    "pip": PIP_INIT,
                    "cairo_macos": "brew install cairo",
                    "cairo_linux": "apt install libcairo2",
                },
            },
            indent=2,
        )
    )
    raise SystemExit(1)
