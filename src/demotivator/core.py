from __future__ import annotations

import io
from dataclasses import dataclass
from os import PathLike
from typing import BinaryIO, Union

from PIL import Image, ImageDraw, ImageOps

from .fonts import load_font

ImageSource = Union[str, PathLike, bytes, BinaryIO, Image.Image]


@dataclass(slots=True)
class DemotivatorStyle:
    """Visual parameters. Sizes are relative to the final canvas width."""

    background: tuple[int, int, int] = (0, 0, 0)
    frame_color: tuple[int, int, int] = (255, 255, 255)
    title_color: tuple[int, int, int] = (255, 255, 255)
    subtitle_color: tuple[int, int, int] = (255, 255, 255)
    title_font: str | None = None
    subtitle_font: str | None = None
    image_width: int = 640          # photo is scaled to this width
    max_image_height: int = 900     # cap for very tall photos
    margin: float = 0.12            # outer margin / canvas width
    gap: float = 0.012              # gap between photo and white frame
    frame_width: int = 3            # white line thickness in px
    title_size: float = 0.085       # title font size / canvas width
    subtitle_size: float = 0.045
    min_font_size: int = 14
    max_title_lines: int = 3
    max_subtitle_lines: int = 3
    line_spacing: float = 0.15
    upper: bool = False             # uppercase the title


def _open(src: ImageSource) -> Image.Image:
    if isinstance(src, Image.Image):
        img = src
    elif isinstance(src, (bytes, bytearray)):
        img = Image.open(io.BytesIO(src))
    else:
        img = Image.open(src)
    img = ImageOps.exif_transpose(img)
    if img.mode in ("RGBA", "LA", "P"):
        rgba = img.convert("RGBA")
        bg = Image.new("RGB", rgba.size, (0, 0, 0))
        bg.paste(rgba, mask=rgba.getchannel("A"))
        return bg
    return img.convert("RGB")


def _text_w(draw: ImageDraw.ImageDraw, text: str, font) -> int:
    return int(draw.textlength(text, font=font))


def _wrap(draw, text: str, font, max_w: int) -> list[str]:
    lines: list[str] = []
    for para in text.splitlines() or [""]:
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = ""
        for w in words:
            # break overly long single words by characters
            while _text_w(draw, w, font) > max_w and len(w) > 1:
                k = len(w)
                while k > 1 and _text_w(draw, w[:k], font) > max_w:
                    k -= 1
                if cur:
                    lines.append(cur)
                    cur = ""
                lines.append(w[:k])
                w = w[k:]
            trial = f"{cur} {w}".strip()
            if _text_w(draw, trial, font) <= max_w:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return [l for l in lines] or [""]


def _fit(draw, text, font_path, start_size, max_w, max_lines, min_size):
    """Shrink the font until text fits into max_lines; truncate as last resort."""
    size = start_size
    while True:
        font = load_font(font_path, size)
        lines = _wrap(draw, text, font, max_w)
        if len(lines) <= max_lines or size <= min_size:
            break
        size = int(size * 0.92)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        while last and _text_w(draw, last + "\u2026", font) > max_w:
            last = last[:-1]
        lines[-1] = last.rstrip() + "\u2026"
    return font, lines


def _block_height(font, lines, spacing) -> int:
    asc, desc = font.getmetrics()
    lh = asc + desc
    return int(lh * len(lines) + lh * spacing * (len(lines) - 1))


def _draw_block(draw, font, lines, color, cx, y, spacing) -> int:
    asc, desc = font.getmetrics()
    lh = asc + desc
    for line in lines:
        w = _text_w(draw, line, font)
        draw.text((cx - w / 2, y), line, font=font, fill=color)
        y += int(lh * (1 + spacing))
    return y


def create_demotivator(
    image: ImageSource,
    title: str = "",
    subtitle: str = "",
    style: DemotivatorStyle | None = None,
) -> Image.Image:
    """Build a demotivator poster and return it as a PIL RGB image."""
    st = style or DemotivatorStyle()
    photo = _open(image)

    w = st.image_width
    h = round(photo.height * w / photo.width)
    if h > st.max_image_height:
        h = st.max_image_height
        photo = ImageOps.fit(photo, (w, h), Image.Resampling.LANCZOS)
    else:
        photo = photo.resize((w, h), Image.Resampling.LANCZOS)

    margin = round(w * st.margin / (1 - 2 * st.margin) )
    canvas_w = w + 2 * margin
    gap = max(round(canvas_w * st.gap), 4) + st.frame_width
    frame_outer_w = w + 2 * gap
    frame_x = (canvas_w - frame_outer_w) // 2

    title = (title or "").strip()
    subtitle = (subtitle or "").strip()
    if st.upper:
        title = title.upper()

    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    text_w = int(canvas_w * 0.92)
    t_font, t_lines = (None, [])
    s_font, s_lines = (None, [])
    if title:
        t_font, t_lines = _fit(probe, title, st.title_font,
                               round(canvas_w * st.title_size), text_w,
                               st.max_title_lines, st.min_font_size)
    if subtitle:
        s_font, s_lines = _fit(probe, subtitle, st.subtitle_font,
                               round(canvas_w * st.subtitle_size), text_w,
                               st.max_subtitle_lines, st.min_font_size)

    top = margin
    frame_h = h + 2 * gap
    y_text = top + frame_h + round(canvas_w * 0.03)
    text_h = 0
    if t_lines:
        text_h += _block_height(t_font, t_lines, st.line_spacing)
    if s_lines:
        text_h += round(canvas_w * 0.015) * bool(t_lines)
        text_h += _block_height(s_font, s_lines, st.line_spacing)
    bottom = margin if not text_h else round(margin * 0.8)
    canvas_h = y_text + text_h + bottom if text_h else top + frame_h + margin

    out = Image.new("RGB", (canvas_w, canvas_h), st.background)
    draw = ImageDraw.Draw(out)
    draw.rectangle(
        [frame_x, top, frame_x + frame_outer_w - 1, top + frame_h - 1],
        outline=st.frame_color, width=st.frame_width,
    )
    out.paste(photo, (frame_x + gap, top + gap))

    cx = canvas_w / 2
    y = y_text
    if t_lines:
        y = _draw_block(draw, t_font, t_lines, st.title_color, cx, y, st.line_spacing)
    if s_lines:
        if t_lines:
            y += round(canvas_w * 0.015)
        _draw_block(draw, s_font, s_lines, st.subtitle_color, cx, y, st.line_spacing)
    return out


def demotivator_bytes(
    image: ImageSource,
    title: str = "",
    subtitle: str = "",
    style: DemotivatorStyle | None = None,
    fmt: str = "JPEG",
    quality: int = 92,
) -> bytes:
    """Same as create_demotivator, but returns encoded bytes (handy for Telegram)."""
    img = create_demotivator(image, title, subtitle, style)
    buf = io.BytesIO()
    if fmt.upper() in ("JPEG", "JPG"):
        img.save(buf, "JPEG", quality=quality, optimize=True)
    else:
        img.save(buf, fmt.upper())
    return buf.getvalue()
