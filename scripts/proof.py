#!/usr/bin/env python3
"""Render proof sheets comparing Roboto Mono with Automata Mono (run with uv).

Writes PNGs to the output directory:
- glyphs.png: the redrawn glyphs in every style, upstream above, ours below.
- small-sizes.png: code at small pixel sizes, unhinted (as on macOS) and with
  TrueType hinting (as on Windows and Linux), magnified without smoothing.
- ligatures.png: Fira Code ligatures in every style, with calt on and off.

Text is shaped with HarfBuzz and rasterized with FreeType.
"""

import argparse
from pathlib import Path

import freetype
import uharfbuzz as hb
from PIL import Image, ImageDraw, ImageFont

from config import STYLES, output_name, upstream_font

GLYPHS_TEXT = (
    "ij; a\u0105, b  y \u1ef5 \u0443 \u0133  tf\u0165 [0] %/ r\u0159\u0157 $\u00a2"
    " CG\u0122 6 OQ 0\u00d8"
)
CODE_TEXT = (
    "for (int i = 0; i < j; i++) { a[i] = fix(t, y) % 8; } return Get($err, Q, 0xC6);"
)
LIGATURES_TEXT = "-> => != === <= >= |> <| || :: ... /* */ <!-- --> www && ?? ;;"
SMALL_SIZES = (11, 12, 13, 14, 16)
SMALL_STYLES = ("Regular", "Bold")
MAGNIFY = 3
LABEL = 14
PAD = 8


def render(path, text, size, hinted=False, features=None):
    """Shape and rasterize one line of text as a grayscale image (black on white)."""
    hb_font = hb.Font(hb.Face(hb.Blob.from_file_path(str(path))))
    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    hb.shape(hb_font, buffer, features or {})
    face = freetype.Face(str(path))
    face.set_pixel_sizes(0, size)
    scale = size / face.units_per_EM
    ascent, descent = round(face.ascender * scale), round(-face.descender * scale)
    flags = freetype.FT_LOAD_RENDER | (
        freetype.FT_LOAD_DEFAULT if hinted else freetype.FT_LOAD_NO_HINTING
    )
    cell = round(buffer.glyph_positions[0].x_advance * scale) if hinted else None
    width = (
        len(buffer.glyph_infos) * cell
        if hinted
        else sum(p.x_advance for p in buffer.glyph_positions) * scale
    )
    image = Image.new("L", (round(width) + 2 * PAD, ascent + descent + 2 * PAD), 0)
    pen = 0.0
    for index, (info, position) in enumerate(
        zip(buffer.glyph_infos, buffer.glyph_positions, strict=True)
    ):
        face.load_glyph(info.codepoint, flags)
        bitmap = face.glyph.bitmap
        if bitmap.width and bitmap.rows:
            glyph = Image.frombytes(
                "L",
                (bitmap.width, bitmap.rows),
                bytes(bitmap.buffer),
                "raw",
                "L",
                bitmap.pitch,
            )
            x = PAD + (index * cell if hinted else round(pen)) + face.glyph.bitmap_left
            y = PAD + ascent - face.glyph.bitmap_top
            image.paste(255, (x, y), glyph)
        pen += position.x_advance * scale
    return Image.eval(image, lambda value: 255 - value)


def stack(rows, gap=PAD):
    """Stack (label, image) rows vertically with labels on the left."""
    font = ImageFont.load_default(size=LABEL)
    label_width = max(font.getbbox(label)[2] for label, _ in rows) + 2 * PAD
    width = label_width + max(image.width for _, image in rows)
    height = sum(image.height + gap for _, image in rows)
    sheet = Image.new("L", (width, height), 255)
    draw = ImageDraw.Draw(sheet)
    y = 0
    for label, image in rows:
        draw.text((PAD, y + (image.height - LABEL) // 2), label, fill=96, font=font)
        sheet.paste(image, (label_width, y))
        y += image.height + gap
    return sheet


def pair(style, args):
    return upstream_font(args.roboto_dir, style), args.fonts_dir / (
        output_name(style) + ".ttf"
    )


def glyphs_sheet(args, styles):
    rows = []
    for style in styles:
        before, after = pair(style, args)
        rows.append(("Roboto Mono " + style, render(before, GLYPHS_TEXT, 72)))
        rows.append(("Automata Mono " + style, render(after, GLYPHS_TEXT, 72)))
    return stack(rows)


def small_sizes_sheet(args, styles):
    rows = []
    for style in styles:
        before, after = pair(style, args)
        for hinted in (False, True):
            for size in SMALL_SIZES:
                mode = "hinted" if hinted else "unhinted"
                for family, path in (("Roboto", before), ("Automata", after)):
                    image = render(path, CODE_TEXT, size, hinted)
                    image = image.resize(
                        (image.width * MAGNIFY, image.height * MAGNIFY), Image.NEAREST
                    )
                    rows.append((f"{family} {style} {size}px {mode}", image))
    return stack(rows)


def ligatures_sheet(args, styles):
    rows = []
    for style in styles:
        path = pair(style, args)[1]
        rows.append((style + " calt", render(path, LIGATURES_TEXT, 40)))
        rows.append(
            (
                style + " no calt",
                render(path, LIGATURES_TEXT, 40, features={"calt": False}),
            )
        )
    return stack(rows)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--roboto-dir", type=Path, default=Path("RobotoMono"))
    parser.add_argument("--fonts-dir", type=Path, default=Path("fonts"))
    parser.add_argument("--output-dir", type=Path, default=Path("build/proof"))
    parser.add_argument(
        "--style", choices=STYLES, action="append", help="default: all styles"
    )
    args = parser.parse_args()
    styles = args.style or STYLES
    args.output_dir.mkdir(parents=True, exist_ok=True)
    sheets = {
        "glyphs.png": glyphs_sheet(args, styles),
        "small-sizes.png": small_sizes_sheet(
            args, [s for s in styles if s in SMALL_STYLES] or styles[:1]
        ),
        "ligatures.png": ligatures_sheet(args, styles),
    }
    for name, sheet in sheets.items():
        sheet.save(args.output_dir / name)
        print("Wrote " + str(args.output_dir / name))


if __name__ == "__main__":
    main()
