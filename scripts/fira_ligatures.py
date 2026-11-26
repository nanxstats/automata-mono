"""Add Fira Code programming ligatures through Ligaturizer's LigatureCreator."""

from contextlib import closing

import fontforge
import psMat

from config import MISSING_FIRA_LIGATURES, load_ligature_specs

FALLBACK_SCRIPTS = (("DFLT", ("dflt",)), ("latn", ("dflt",)))
# Fira Code draws `||` with its full-height bar: taller than Roboto's `|` and
# below Roboto's Windows clipping descent. Fit it to Roboto's own glyph so
# `a || b` matches `a | b`. The bars are vertical, so their width is kept.
FIT_TO_GLYPH = {"||": "bar"}


def script_languages(font):
    """Script and language systems already used by the font's GSUB features."""
    systems = {}
    for lookup in font.gsub_lookups:
        for _, scripts in font.getLookupInfo(lookup)[2]:
            for script, languages in scripts:
                systems.setdefault(script, set()).update(languages)
    if not systems:
        return FALLBACK_SCRIPTS
    return tuple((script, tuple(sorted(languages))) for script, languages in sorted(systems.items()))


def add_ligatures(font, fira_path, style, ligaturizer_dir):
    """Add every retained ligature to `font`.

    Return a map from ligature text to the transform applied to its outline
    after Ligaturizer's scaling (fitting and slanting), for validation.
    """
    specs = load_ligature_specs(ligaturizer_dir)
    from ligaturize import LigatureCreator

    systems = script_languages(font)
    existing = set(font.gsub_lookups)
    added = []
    with closing(fontforge.open(str(fira_path))) as fira:
        creator = LigatureCreator(font, fira, 0.1, False)
        # Same order as Ligaturizer's own driver: shorter sequences first.
        for text, spec in sorted(specs.items(), key=lambda item: len(item[0])):
            if spec["firacode_ligature_name"] not in fira:
                if text in MISSING_FIRA_LIGATURES:
                    continue
                raise ValueError("Fira Code lacks the %r ligature" % text)
            creator.add_ligature(spec["chars"], spec["firacode_ligature_name"])
            added.append(text)
        if creator._lig_counter != len(added):
            raise ValueError("Ligaturizer silently skipped ligatures")

    # Ligaturizer registers calt under a fixed list of scripts and languages.
    # A language system does not inherit features from its script's default,
    # so those extra systems would hide Roboto's smcp. Use the font's own.
    for lookup in set(font.gsub_lookups) - existing:
        features = font.getLookupInfo(lookup)[2]
        if features:
            font.lookupSetFeatureList(lookup, tuple((tag, systems) for tag, _ in features))

    slant = psMat.identity()
    if style.slant:
        # Slant about the math axis, as Roboto's italic operators are, so the
        # ligatures stay centered on the operators they replace.
        bottom, top = font["equal"].boundingBox()[1::2]
        axis = (bottom + top) / 2
        slant = (1, 0, style.slant, 1, -style.slant * axis, 0)
    transforms = {}
    # Ligaturizer names ligature glyphs lig.1, lig.2, ... in the order added.
    for number, text in enumerate(added, 1):
        glyph = font["lig.%d" % number]
        transform = slant
        if text in FIT_TO_GLYPH:
            _, bottom, _, top = glyph.boundingBox()
            _, target_bottom, _, target_top = font[FIT_TO_GLYPH[text]].boundingBox()
            scale = (target_top - target_bottom) / (top - bottom)
            fit = (1, 0, 0, scale, 0, target_bottom - bottom * scale)
            transform = psMat.compose(fit, slant)
        if transform != psMat.identity():
            glyph.transform(transform)
        transforms[text] = tuple(transform)
    print("  Added %d Fira Code ligatures from %s" % (len(added), fira_path.name))
    return transforms
