#!/usr/bin/env python3
"""Build one unhinted Automata Mono style with FontForge.

Run with FontForge's Python: fontforge -lang=py -script scripts/build_font.py.
Applies the glyph customizations to the upstream Roboto Mono TTF, adds Fira
Code ligatures, and writes the font plus a JSON manifest of what changed.
Upstream checkouts are only read.
"""

import argparse
import json
import os
from pathlib import Path
import tempfile

import fontforge

from config import STYLES, fira_font, split_style, upstream_font
from customizations import CUSTOMIZATIONS, Style, apply_customizations
from fira_ligatures import add_ligatures


def build(args):
    source = upstream_font(args.roboto_dir, args.style)
    fira = fira_font(args.ligaturizer_dir, args.style)
    font = fontforge.open(str(source))
    try:
        print("Building " + args.style)
        style = Style.from_font(font, args.style, split_style(args.style)[1])
        customizations = apply_customizations(font, style, CUSTOMIZATIONS)
        ligatures = add_ligatures(font, fira, style, args.ligaturizer_dir)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".automata-", dir=args.output.parent) as staging:
            temporary = Path(staging) / args.output.name
            # Hinting is redone by ttfautohint; finalize.py rewrites names.
            font.generate(str(temporary), flags=("opentype", "omit-instructions", "no-FFTM-table"))
            os.replace(temporary, args.output)
    finally:
        font.close()
    manifest = {
        "style": args.style,
        "source": str(source),
        "fira": str(fira),
        "customizations": customizations,
        "ligatures": ligatures,
    }
    args.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--style", choices=STYLES, required=True)
    parser.add_argument("--roboto-dir", type=Path, default=Path("RobotoMono"))
    parser.add_argument("--ligaturizer-dir", type=Path, default=Path("Ligaturizer"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    build(parse_args())
