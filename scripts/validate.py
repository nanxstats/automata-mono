#!/usr/bin/env python3
"""Validate the built fonts against upstream Roboto Mono and Fira Code (run with uv).

Checks tables and metadata, that only declared glyphs differ from upstream,
ligature outlines, and real HarfBuzz shaping with and without ligatures.
"""

import argparse
import json
import sys
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

from config import (
    EXCLUDED_LIGATURES,
    MISSING_FIRA_LIGATURES,
    STYLES,
    UPSTREAM_FAMILY,
    UPSTREAM_POSTSCRIPT_FAMILY,
    URL,
    VENDOR_ID,
    VERSION,
    load_ligature_specs,
    output_name,
    style_names,
    upstream_font,
)

# Script/language systems to shape in; None lets HarfBuzz guess from the text.
SYSTEMS = (
    (None, None),
    ("Latn", None),
    ("Cyrl", None),
    ("Grek", None),
    ("Latn", "ca"),
    ("Latn", "ro"),
    ("Latn", "tr"),
    ("Cyrl", "sr"),
)
SAMPLES = (
    "if (x, y; z) { return a[i] + b[j]; }",
    "yield: y_axis, fix(ij);",
    "**`example.json`**",
    "x`x",
    "```",
    "$HOME ${value} $100.00",
    # Combining sequences (e.g. y + dot below), Vietnamese, and Cyrillic letters
    # built from redrawn glyphs, including the tailed letters that keep the comma.
    "e\u0301 a\u0308 n\u0303 o\u0308 y\u0323 \u0456\u0308",
    "\u1ef5 \u0443 \u045e \u048a \u04c5",
)
OS2_FIELDS = (
    "version",
    "xAvgCharWidth",
    "usWeightClass",
    "usWidthClass",
    "fsType",
    "fsSelection",
    "ySubscriptXSize",
    "ySubscriptYSize",
    "ySubscriptXOffset",
    "ySubscriptYOffset",
    "ySuperscriptXSize",
    "ySuperscriptYSize",
    "ySuperscriptXOffset",
    "ySuperscriptYOffset",
    "yStrikeoutSize",
    "yStrikeoutPosition",
    "sFamilyClass",
    "ulUnicodeRange1",
    "ulUnicodeRange2",
    "ulUnicodeRange3",
    "ulUnicodeRange4",
    "sTypoAscender",
    "sTypoDescender",
    "sTypoLineGap",
    "usWinAscent",
    "usWinDescent",
    "ulCodePageRange1",
    "ulCodePageRange2",
    "sxHeight",
    "sCapHeight",
    "usDefaultChar",
    "usBreakChar",
)


class ValidationError(AssertionError):
    pass


def require(condition, message):
    if not condition:
        raise ValidationError(message)


class Shaper:
    def __init__(self, path, shaper="ot"):
        self.font = hb.Font(hb.Face(hb.Blob.from_file_path(str(path))))
        self.name = shaper

    def shape(self, text, features=None, script=None, language=None):
        buffer = hb.Buffer()
        buffer.add_str(text)
        buffer.guess_segment_properties()
        if script:
            buffer.script = script
        if language:
            buffer.language = language
        hb.shape(self.font, buffer, features or {}, shapers=[self.name])
        names = [
            self.font.glyph_to_string(info.codepoint) for info in buffer.glyph_infos
        ]
        positions = [
            (p.x_advance, p.y_advance, p.x_offset, p.y_offset)
            for p in buffer.glyph_positions
        ]
        return names, positions


def outline(glyphs, name):
    """Decomposed contours, sorted: flattening a composite may reorder them."""
    pen = DecomposingRecordingPen(glyphs)
    glyphs[name].draw(pen)
    contours, current = [], []
    for operator, points in pen.value:
        current.append((operator, tuple(points)))
        if operator in ("closePath", "endPath"):
            contours.append(tuple(current))
            current = []
    return sorted(contours + ([tuple(current)] if current else []))


def bounds(glyphs, name, transform=None):
    pen = BoundsPen(glyphs)
    glyphs[name].draw(TransformPen(pen, transform) if transform else pen)
    return pen.bounds


def validate_tables(font, upstream):
    difference = set(font.reader.keys()) ^ set(upstream.reader.keys())
    require(not difference, f"Table set differs from upstream: {sorted(difference)}")
    require(
        "ttfautohint" in font["name"].getDebugName(5),
        "Font is not hinted by ttfautohint",
    )
    head, source = font["head"], upstream["head"]
    for field in ("unitsPerEm", "flags", "macStyle", "lowestRecPPEM", "created"):
        require(
            getattr(head, field) == getattr(source, field),
            f"head.{field} differs from upstream",
        )
    require(
        abs(head.fontRevision - float(VERSION)) < 1e-4, "Incorrect head.fontRevision"
    )
    for field in OS2_FIELDS:
        require(
            getattr(font["OS/2"], field) == getattr(upstream["OS/2"], field),
            f"OS/2.{field} differs from upstream",
        )
    require(
        font["OS/2"].panose.__dict__ == upstream["OS/2"].panose.__dict__,
        "OS/2 PANOSE differs",
    )
    require(font["OS/2"].achVendID == VENDOR_ID, "Incorrect vendor ID")
    for field in (
        "ascent",
        "descent",
        "lineGap",
        "caretSlopeRise",
        "caretSlopeRun",
        "caretOffset",
        "advanceWidthMax",
    ):
        require(
            getattr(font["hhea"], field) == getattr(upstream["hhea"], field),
            f"hhea.{field} differs from upstream",
        )
    for field in ("italicAngle", "underlinePosition", "underlineThickness"):
        require(
            getattr(font["post"], field) == getattr(upstream["post"], field),
            f"post.{field} differs from upstream",
        )
    require(font["post"].isFixedPitch == 1, "Not marked fixed pitch")
    glyf, hmtx = font["glyf"], font["hmtx"]
    ascent, descent = font["OS/2"].usWinAscent, font["OS/2"].usWinDescent
    for name in font.getGlyphOrder():
        glyph = glyf[name]
        if glyph.numberOfContours:
            glyph.recalcBounds(glyf)
            require(
                hmtx[name][1] == glyph.xMin, "Left side bearing is not xMin: " + name
            )
            require(
                glyph.yMax <= ascent and glyph.yMin >= -descent,
                "Clipped by win metrics: " + name,
            )


def validate_names(font, style, upstream):
    records = {}
    for record in font["name"].names:
        require(
            (record.platformID, record.platEncID, record.langID) == (3, 1, 0x409),
            "Unexpected name record platform/language",
        )
        records[record.nameID] = record.toUnicode()
    upstream_records = {
        r.nameID: r.toUnicode() for r in upstream["name"].names if r.platformID == 3
    }
    # The naming scheme reproduces upstream's own names when given its family.
    styled = {
        key: value
        for key, value in upstream_records.items()
        if key in (1, 2, 4, 6, 16, 17)
    }
    require(
        style_names(style, UPSTREAM_FAMILY, UPSTREAM_POSTSCRIPT_FAMILY) == styled,
        "Naming scheme no longer matches upstream",
    )
    expected = style_names(style)
    for key in (1, 2, 4, 6, 16, 17):
        require(
            records.get(key) == expected.get(key),
            f"Incorrect name ID {key}: {records.get(key)!r}",
        )
    require(
        records[0].startswith(upstream_records[0]) and "Fira Code" in records[0],
        "Incorrect copyright",
    )
    require(
        records[3] == f"{VERSION};{VENDOR_ID};{output_name(style)}",
        "Incorrect unique ID",
    )
    require(
        records[5].startswith(f"Version {VERSION}; {UPSTREAM_FAMILY} "),
        "Incorrect version string",
    )
    require(7 not in records, "Upstream trademark notice retained")
    require(records[11] == URL, "Incorrect vendor URL")


def validate_glyphs(font, upstream, manifest, cell):
    glyphs, source = font.getGlyphSet(), upstream.getGlyphSet()
    added = set(font.getGlyphOrder()) - set(upstream.getGlyphOrder())
    require(
        set(upstream.getGlyphOrder()) <= set(font.getGlyphOrder()),
        "Lost upstream glyphs",
    )
    require(
        all(name == ".null" or name.startswith(("lig.", "CR.")) for name in added),
        f"Unexpected new glyphs: {sorted(added)[:5]}",
    )
    require(
        font.getBestCmap() == upstream.getBestCmap(),
        "Character map differs from upstream",
    )
    require(
        all(glyphs[name].width == cell for name in font.getGlyphOrder()),
        "Non-monospace advance",
    )
    require(
        all(source[name].width == cell for name in upstream.getGlyphOrder()),
        "Upstream cell changed",
    )
    declared = {
        name for entry in manifest["customizations"] for name in entry["changed"]
    }
    preserved = {
        name for entry in manifest["customizations"] for name in entry["preserved"]
    }
    changed = {
        name
        for name in upstream.getGlyphOrder()
        if outline(glyphs, name) != outline(source, name)
    }
    require(
        changed == declared,
        "Changed glyphs differ from the manifest: "
        f"unexpected {sorted(changed - declared)}, "
        f"unchanged {sorted(declared - changed)}",
    )
    require(not changed & preserved, "Preserved glyphs changed")
    return changed


def validate_ligature_outlines(font, fira, shaper, specs, transforms):
    glyphs, donor = font.getGlyphSet(), fira.getGlyphSet()
    em_scale = font["head"].unitsPerEm / fira["head"].unitsPerEm
    cell = font["hmtx"]["space"][0]
    for text, (a, b, c, d, e, f) in transforms.items():
        name = specs[text]["firacode_ligature_name"]
        ligature = shaper.shape(text)[0][-1]
        # Ligaturizer changes Fira's em first, rounding the advance, then fits the cell.
        x_scale = em_scale * cell / round(em_scale * donor[name].width)
        expected = bounds(
            donor, name, (a * x_scale, b * x_scale, c * em_scale, d * em_scale, e, f)
        )
        actual = bounds(glyphs, ligature)
        require(
            all(abs(p - q) <= 3 for p, q in zip(actual, expected, strict=True)),
            f"Ligature outline does not match Fira Code: {text!r} ({ligature})",
        )


def coretext_shaper(path):
    """A CoreText shaper on macOS, where apps may shape with it instead of HarfBuzz."""
    shaper = Shaper(path, "coretext")
    try:
        shaper.shape("a")
    except RuntimeError:
        return None
    return shaper


def validate_ligatures(shaper, texts, names, cell, script=None, language=None):
    where = f"{shaper.name} {script}/{language}"
    for text in texts:
        glyphs, positions = shaper.shape(text, script=script, language=language)
        require(
            len(glyphs) == len(text)
            and glyphs[-1].startswith("lig.")
            and all(name.startswith("CR.") for name in glyphs[:-1]),
            f"Ligature failed for {text!r} ({where}): {glyphs}",
        )
        require(
            all(p == (cell, 0, 0, 0) for p in positions),
            f"Ligature changed spacing: {text!r}",
        )
        glyphs, _ = shaper.shape(text, {"calt": False}, script, language)
        require(
            glyphs == [names[char] for char in text],
            f"calt=0 did not disable {text!r} ({where})",
        )
    for text in sorted(EXCLUDED_LIGATURES):
        require(
            shaper.shape(text, script=script, language=language)[0]
            == [names[char] for char in text],
            f"Excluded ligature is active: {text!r} ({where})",
        )


def validate_shaping(shaper, reference, coretext, texts, cell, cmap):
    names = {chr(code): name for code, name in cmap.items()}
    plain = {"calt": False}
    for script, language in SYSTEMS:
        validate_ligatures(shaper, texts, names, cell, script, language)
        smcp = shaper.shape("ai", {"smcp": True}, script, language)[0]
        require(
            smcp == ["A.smcp", "I.smcp"],
            f"smcp unavailable in {script}/{language}: {smcp}",
        )
    if coretext:
        validate_ligatures(coretext, texts, names, cell)
    # Without ligatures, every character and sample shapes exactly like Roboto Mono.
    corpus = [chr(code) for code in cmap if code >= 0x20] + list(SAMPLES)
    for text in corpus:
        for features in (plain, {"calt": False, "smcp": True}):
            require(
                shaper.shape(text, features) == reference.shape(text, features),
                f"Shaping differs from upstream with calt=0: {text!r}",
            )
    printable = "".join(chr(code) for code in range(0x20, 0x7F))
    for features in ({}, plain):
        glyphs, positions = shaper.shape(printable, features)
        require(
            ".notdef" not in glyphs and all(p == (cell, 0, 0, 0) for p in positions),
            "ASCII spacing changed",
        )


def validate_style(args, style, specs):
    name = output_name(style)
    path = args.output_dir / (name + ".ttf")
    manifest = json.loads((args.build_dir / (name + ".json")).read_text())
    source_path = upstream_font(args.roboto_dir, style)
    font, upstream, fira = TTFont(path), TTFont(source_path), TTFont(manifest["fira"])
    cell = upstream["hmtx"]["space"][0]
    texts = sorted(specs.keys() - MISSING_FIRA_LIGATURES)
    require(
        sorted(manifest["ligatures"]) == texts,
        "Manifest ligatures differ from the expected set",
    )
    validate_tables(font, upstream)
    validate_names(font, style, upstream)
    changed = validate_glyphs(font, upstream, manifest, cell)
    shaper = Shaper(path)
    validate_ligature_outlines(font, fira, shaper, specs, manifest["ligatures"])
    coretext = coretext_shaper(path)
    validate_shaping(
        shaper, Shaper(source_path), coretext, texts, cell, upstream.getBestCmap()
    )
    customizations = ", ".join(entry["name"] for entry in manifest["customizations"])
    shapers = "HarfBuzz and CoreText" if coretext else "HarfBuzz"
    print(
        f"PASS {path.name}: {len(texts)} ligatures, "
        f"{len(EXCLUDED_LIGATURES)} exclusions, "
        f"{len(changed)} glyphs changed by {customizations}; shaped with {shapers}"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--roboto-dir", type=Path, default=Path("RobotoMono"))
    parser.add_argument("--ligaturizer-dir", type=Path, default=Path("Ligaturizer"))
    parser.add_argument("--build-dir", type=Path, default=Path("build"))
    parser.add_argument("--output-dir", type=Path, default=Path("fonts"))
    parser.add_argument(
        "--style", choices=STYLES, action="append", help="default: all styles"
    )
    args = parser.parse_args()
    specs = load_ligature_specs(args.ligaturizer_dir)
    failures = 0
    for style in args.style or STYLES:
        try:
            validate_style(args, style, specs)
        except ValidationError as error:
            failures += 1
            print(f"FAIL {style}: {error}", file=sys.stderr)
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
