"""i and j: a constant, wider gap between the dot and the stem."""

from .base import Customization


class RaisedTittles(Customization):
    name = "raised-tittles"
    summary = "Dots on i and j raised to a constant gap above the stem"
    # Glyphs that draw their own i/j dots, with dot counts. Accented forms
    # (í, ï, ĵ, ...) use the dotless letters with an accent and are unaffected.
    DOTS = {"i": 1, "j": 1, "iogonek": 1, "ij": 2}
    redraws = tuple(DOTS)
    inherits = ("uni0456", "uni0458", "uni1ECB")  # Cyrillic і ј, Vietnamese ị

    # Gap between the stem top and the dot, in em. Upstream ranges from 0.116
    # (Thin) down to 0.063 (Bold), so dots crowd the stem at small sizes in
    # the heavier weights. JetBrains Mono (about 0.10) and Fira Code (about
    # 0.13) hold the gap nearly constant and let heavier dots grow upward.
    # Every weight and every dotted glyph gets the same gap here.
    GAP = 0.11

    def redraw(self, font, style):
        gap = round(self.GAP * style.em)
        for name, count in self.DOTS.items():
            glyph = font[name]
            stem_top, dots = self._split(glyph)
            if len(dots) != count:
                raise ValueError("Expected %d dot(s) on %s" % (count, name))
            layer = glyph.foreground
            for index in dots:
                dot = layer[index]
                lift = stem_top + gap - dot.boundingBox()[1]
                if abs(lift) > gap:
                    raise ValueError("Unexpected dot position on " + name)
                # Move along the italic angle so the dot stays over the stem.
                dot.transform((1, 0, 0, 1, round(lift * style.slant), round(lift)))
                layer[index] = dot
            glyph.foreground = layer

    @staticmethod
    def _split(glyph):
        """Top of the letter body and indices of the contours above it (dots)."""
        if glyph.references:
            raise ValueError("Expected %s to be drawn without references" % glyph.glyphname)
        layer = glyph.foreground
        body_top = min(contour.boundingBox()[3] for contour in layer)
        dots = [index for index, contour in enumerate(layer) if contour.boundingBox()[1] > body_top]
        return max(layer[i].boundingBox()[3] for i in range(len(layer)) if i not in dots), dots
