"""Project settings shared by the FontForge build and the uv tools.

Standard library only: FontForge's embedded Python and the uv environment
both import this module.
"""

import sys
from pathlib import Path

FAMILY = "Automata Mono"
POSTSCRIPT_FAMILY = "AutomataMono"
VERSION = "1.000"
VENDOR_ID = "UKWN"
URL = "https://github.com/nanxstats/automata-mono"

UPSTREAM_FAMILY = "Roboto Mono"
UPSTREAM_POSTSCRIPT_FAMILY = "RobotoMono"

WEIGHTS = {"Thin": 100, "Light": 300, "Regular": 400, "Medium": 500, "Bold": 700}
# Upstream style names; the regular italic is plain "Italic".
STYLES = tuple(
    ("Italic" if weight == "Regular" else weight + "Italic") if italic else weight
    for weight in WEIGHTS
    for italic in (False, True)
)

# Fira Code weight that supplies each style's ligatures. Roboto Mono draws its
# operators lighter than its letters, so match operator strokes (hyphen
# thickness at 2048 UPM): Roboto Light 103 / Regular 152 / Medium 194 /
# Bold 225 against Fira Light 122 / Regular 153 / Medium 193 / SemiBold 221.
# Fira Code has nothing near Roboto Thin (54), so Thin uses Light unchanged.
FIRA_WEIGHTS = {
    "Thin": "Light",
    "Light": "Light",
    "Regular": "Regular",
    "Medium": "Medium",
    "Bold": "SemiBold",
}

# Fira Code ligatures that are deliberately left out: Ergonomic Mono's set,
# plus www, whose condensed letters do not match Roboto Mono's lowercase.
EXCLUDED_LIGATURES = frozenset(
    ("&&", "~@", "\\/", ".?", "?:", "?=", "?.", "??", ";;", "/\\", "www")
)
# Listed by Ligaturizer but absent from the Fira Code revision it pins.
MISSING_FIRA_LIGATURES = frozenset(("~=",))


def split_style(style):
    """Return (weight, italic) for an upstream style name."""
    if style not in STYLES:
        raise ValueError("Unknown style: " + style)
    if style == "Italic":
        return "Regular", True
    return style.removesuffix("Italic"), style.endswith("Italic")


def upstream_font(roboto_dir, style):
    return (
        Path(roboto_dir)
        / "fonts"
        / "ttf"
        / (UPSTREAM_POSTSCRIPT_FAMILY + "-" + style + ".ttf")
    )


def fira_font(ligaturizer_dir, style):
    weight = FIRA_WEIGHTS[split_style(style)[0]]
    return (
        Path(ligaturizer_dir)
        / "fonts"
        / "fira"
        / "distr"
        / "otf"
        / ("FiraCode-" + weight + ".otf")
    )


def output_name(style):
    return POSTSCRIPT_FAMILY + "-" + style


def style_names(style, family=FAMILY, postscript_family=POSTSCRIPT_FAMILY):
    """Name IDs 1, 2, 4, 6, 16, 17 following upstream's Google Fonts scheme.

    Regular, Italic, Bold, and Bold Italic form the legacy four-style family.
    Other weights get their own legacy family plus typographic names.
    """
    weight, italic = split_style(style)
    names = {6: postscript_family + "-" + style}
    if weight in ("Regular", "Bold"):
        subfamily = {
            (False, False): "Regular",
            (False, True): "Italic",
            (True, False): "Bold",
            (True, True): "Bold Italic",
        }[weight == "Bold", italic]
        names.update({1: family, 2: subfamily, 4: family + " " + subfamily})
    else:
        typographic = weight + (" Italic" if italic else "")
        names.update(
            {
                1: family + " " + weight,
                2: "Italic" if italic else "Regular",
                4: family + " " + typographic,
                16: family,
                17: typographic,
            }
        )
    return names


def load_ligature_specs(ligaturizer_dir):
    """Map ligature text (e.g. "->") to Ligaturizer's spec, minus exclusions.

    Ligaturizer's ligatures.py and char_dict.py are plain data modules.
    Append (not prepend) their directory: Ligaturizer also ships a stat.py
    that would shadow the standard library module.
    """
    directory = str(Path(ligaturizer_dir).resolve())
    if directory not in sys.path:
        sys.path.append(directory)
    from char_dict import char_dict
    from ligatures import ligatures

    specs = {
        "".join(char_dict[name] for name in spec["chars"]): spec
        for spec in ligatures
        if spec["firacode_ligature_name"] is not None
    }
    stale = EXCLUDED_LIGATURES - specs.keys()
    if stale:
        raise ValueError(
            f"Ligaturizer no longer offers excluded ligatures: {sorted(stale)}"
        )
    return {
        text: spec for text, spec in specs.items() if text not in EXCLUDED_LIGATURES
    }
