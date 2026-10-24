"""Font lookup: user font -> common system serif fonts -> Pillow default."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PIL import ImageFont

_CANDIDATES = (
    "times.ttf", "Times New Roman.ttf", "timesbd.ttf",
    "LiberationSerif-Regular.ttf", "DejaVuSerif.ttf", "FreeSerif.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
    "C:/Windows/Fonts/times.ttf",
)


@lru_cache(maxsize=128)
def load_font(path: str | None, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    size = max(int(size), 6)
    if path:
        if not Path(path).exists():
            raise FileNotFoundError(f"Font not found: {path}")
        return ImageFont.truetype(path, size)
    for name in _CANDIDATES:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=size)  # Pillow >= 10.1
    except TypeError:  # pragma: no cover
        return ImageFont.load_default()
