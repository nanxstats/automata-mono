"""The customization contract and the driver that enforces it."""

import math
from dataclasses import dataclass

from .outline import referencing, snapshot


@dataclass(frozen=True)
class Style:
    """Per-style facts that customizations need, measured from the source font."""

    name: str
    italic: bool
    em: int
    slant: float  # horizontal shift per unit of height; 0 for upright styles
    x_height: float  # top of x
    cap_height: float  # top of H
    ascender: float  # flat top of l, the height of straight ascenders
    descender: float  # flat bottom of p, the depth of straight descenders

    @classmethod
    def from_font(cls, font, name, italic):
        if bool(font.italicangle) != italic:
            raise ValueError("Italic angle does not match style " + name)
        return cls(
            name=name,
            italic=italic,
            em=font.em,
            slant=math.tan(math.radians(-font.italicangle)),
            x_height=font["x"].boundingBox()[3],
            cap_height=font["H"].boundingBox()[3],
            ascender=font["l"].boundingBox()[3],
            descender=font["p"].boundingBox()[1],
        )

    def upright(self, x, y):
        """Remove the italic slant from a point's x coordinate."""
        return x - y * self.slant

    def slanted(self, x, y):
        """Apply the italic slant to a point drawn in upright coordinates."""
        return x + y * self.slant, y


class Customization:
    """One self-contained change to the design of Roboto Mono glyphs.

    Subclasses declare which glyphs they touch and implement `redraw`. The
    driver checks the declaration against the font before and after:

    - `redraws`: glyphs whose own outlines `redraw` replaces. Each must change.
    - `inherits`: composites that reference a redrawn glyph and should show the
      new design. Each must change.
    - `preserves`: composites that reference a redrawn glyph but keep the
      upstream design. Their references to redrawn glyphs are decomposed first.

    Every composite that references a redrawn glyph must appear in `inherits`
    or `preserves`, so new upstream composites cannot change silently. Glyphs
    that reach a redrawn glyph only through an inherited composite change
    with it and are reported. Nothing else may change, advances included.
    """

    name = ""
    summary = ""
    redraws = ()
    inherits = ()
    preserves = ()

    def redraw(self, font, style):
        raise NotImplementedError


class CustomizationError(ValueError):
    pass


def apply_customizations(font, style, customizations):
    """Apply customizations in order; return a manifest entry for each."""
    return [_apply(font, style, customization) for customization in customizations]


def _apply(font, style, customization):
    name = customization.name

    def fail(message, glyphs):
        raise CustomizationError(
            f"{name} ({style.name}): {message}: {', '.join(sorted(glyphs))}"
        )

    redraws, inherits, preserves = (
        set(getattr(customization, key)) for key in ("redraws", "inherits", "preserves")
    )
    missing = {glyph for glyph in redraws | inherits | preserves if glyph not in font}
    if missing:
        fail("glyphs not in font", missing)
    dependents = referencing(font, redraws) - redraws
    if dependents - inherits - preserves:
        fail(
            "unclassified composites reference redrawn glyphs",
            dependents - inherits - preserves,
        )
    if (inherits | preserves) - dependents:
        fail(
            "declared composites do not reference redrawn glyphs",
            (inherits | preserves) - dependents,
        )

    before = snapshot(font)
    for glyph_name in preserves:
        for ref_name in {ref[0] for ref in font[glyph_name].references} & redraws:
            font[glyph_name].unlinkRef(ref_name)
    customization.redraw(font, style)
    after = snapshot(font)

    if before.keys() != after.keys():
        fail("glyph set changed", before.keys() ^ after.keys())
    changed = {glyph for glyph in before if before[glyph][0] != after[glyph][0]}
    resized = {glyph for glyph in before if before[glyph][1] != after[glyph][1]}
    if resized:
        fail("advance widths changed", resized)
    if (redraws | inherits) - changed:
        fail("declared changes did not happen", (redraws | inherits) - changed)
    if changed & preserves:
        fail("preserved composites changed", changed & preserves)
    reachable = set(redraws | inherits)
    while True:
        more = referencing(font, reachable) - reachable
        if not more:
            break
        reachable |= more
    if changed - reachable:
        fail("undeclared glyphs changed", changed - reachable)

    print(f"  {name}: {', '.join(sorted(changed))}")
    return {
        "name": name,
        "summary": customization.summary,
        "changed": sorted(changed),
        "preserved": sorted(preserves),
    }
