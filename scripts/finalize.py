#!/usr/bin/env python3
"""Prepare FontForge's output for ttfautohint and release (run with uv).

Removes FontForge artifacts and old hinting tables, writes Automata Mono's
names, and restores upstream metadata that FontForge rewrites.
"""

import argparse
import json
from pathlib import Path

from fontTools.otlLib.maxContextCalc import maxCtxFont
from fontTools.ttLib import TTFont

from config import UPSTREAM_FAMILY, URL, VENDOR_ID, VERSION, output_name, style_names

FIRA_COPYRIGHT = "Programming ligatures from Fira Code. Copyright (c) 2014, The Fira Code Project Authors."
WINDOWS_ENGLISH = (3, 1, 0x409)
# Names that describe Roboto Mono's publisher rather than this font.
DROPPED_NAMES = (7,)  # trademark


def drop_synthesized_layout(font, upstream):
    """Remove the GDEF and GPOS tables FontForge writes for a font without them.

    Upstream has neither. FontForge's GPOS has no lookups, and its GDEF only
    classifies Ligaturizer's spacer glyphs as base glyphs. Such a GDEF would
    stop HarfBuzz from deriving mark classes from Unicode, changing how
    combining marks shape, so anything more than that is an error.
    """
    added = set(font.getGlyphOrder()) - set(upstream.getGlyphOrder())
    if "GPOS" in font and "GPOS" not in upstream:
        lookups = font["GPOS"].table.LookupList
        if lookups is not None and lookups.Lookup:
            raise ValueError("FontForge wrote GPOS lookups")
        del font["GPOS"]
    if "GDEF" in font and "GDEF" not in upstream:
        gdef = font["GDEF"].table
        classes = gdef.GlyphClassDef.classDefs if gdef.GlyphClassDef else {}
        carets = gdef.LigCaretList.LigGlyphCount if gdef.LigCaretList else 0
        extra = any(getattr(gdef, key, None) for key in ("AttachList", "MarkAttachClassDef", "MarkGlyphSetsDef"))
        if set(classes) - added or set(classes.values()) - {1} or carets or extra:
            raise ValueError("FontForge wrote GDEF data beyond spacer glyph classes")
        del font["GDEF"]


def widen_null_glyph(font, upstream):
    """Give FontForge's added .null glyph the cell advance instead of zero.

    Every upstream glyph shares one advance. The glyph is empty and no
    character maps to it; removing it would renumber every glyph ID.
    """
    name = ".null"
    if name not in font.getGlyphOrder() or name in upstream.getGlyphOrder():
        return
    if any(name in table.cmap.values() for table in font["cmap"].tables):
        raise ValueError("FontForge mapped characters to .null")
    font["hmtx"][name] = (upstream["hmtx"]["space"][0], 0)


def sync_side_bearings(font):
    """Set each left side bearing to the outline's xMin.

    FontForge writes stale values for composites whose components changed
    (the semicolon keeps the old comma's bearing) and rounds ligatures
    differently. TrueType rasterizers position outlines by these values.
    """
    glyf, hmtx = font["glyf"], font["hmtx"]
    for name in font.getGlyphOrder():
        glyph = glyf[name]
        if glyph.numberOfContours:
            glyph.recalcBounds(glyf)
            hmtx[name] = (hmtx[name][0], glyph.xMin)


def names(style, upstream, fira):
    existing = {
        record.nameID: record.toUnicode()
        for record in upstream["name"].names
        if (record.platformID, record.platEncID, record.langID) == WINDOWS_ENGLISH
    }
    result = {key: value for key, value in existing.items()
              if key not in DROPPED_NAMES and key not in (1, 2, 4, 6, 16, 17)}
    result.update(style_names(style))
    result[0] = existing[0] + "\n" + FIRA_COPYRIGHT
    result[3] = "%s;%s;%s" % (VERSION, VENDOR_ID, output_name(style))
    result[5] = "Version %s; %s %.3f; Fira Code %.3f" % (
        VERSION, UPSTREAM_FAMILY, upstream["head"].fontRevision, fira["head"].fontRevision)
    result[11] = URL
    return result


def finalize(args):
    manifest = json.loads(args.manifest.read_text())
    style = manifest["style"]
    upstream = TTFont(manifest["source"])
    fira = TTFont(manifest["fira"], lazy=True)
    font = TTFont(args.input)

    drop_synthesized_layout(font, upstream)
    # FontForge also adds a legacy Mac cmap subtable.
    font["cmap"].tables = [table for table in font["cmap"].tables if table.platformID != 1]
    widen_null_glyph(font, upstream)
    sync_side_bearings(font)
    # ttfautohint writes fresh hinting tables; FontForge kept the old ones.
    for tag in ("cvt ", "fpgm", "prep", "gasp"):
        if tag in font:
            del font[tag]

    head, source_head = font["head"], upstream["head"]
    head.fontRevision = float(VERSION)
    head.created = source_head.created
    head.lowestRecPPEM = source_head.lowestRecPPEM
    for field in ("caretSlopeRise", "caretSlopeRun", "caretOffset"):
        # FontForge approximates the italic caret slope with small integers.
        setattr(font["hhea"], field, getattr(upstream["hhea"], field))
    post, source_post = font["post"], upstream["post"]
    # FontForge shifts the underline on export; upstream values are correct.
    post.underlinePosition = source_post.underlinePosition
    post.underlineThickness = source_post.underlineThickness
    post.isFixedPitch = 1  # Upstream leaves this unset although every glyph shares one advance.
    os2 = font["OS/2"]
    os2.achVendID = VENDOR_ID
    os2.usMaxContext = maxCtxFont(font)

    table = font["name"]
    table.names = []
    for name_id, value in sorted(names(style, upstream, fira).items()):
        table.setName(value, name_id, *WINDOWS_ENGLISH)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    font.save(args.output)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True, help="build manifest from build_font.py")
    parser.add_argument("--input", type=Path, required=True, help="FontForge output")
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    finalize(parse_args())
