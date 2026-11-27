"""i and j: larger dots at a constant gap above the stem, shifted slightly left."""

import psMat

from .base import Customization


class Tittles(Customization):
    name = "tittles"
    summary = "Dots on i and j: larger, at a constant gap above the stem, slightly left of center"
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
    # Relative to their stems, Roboto's dots are the smallest among the
    # monospaced designs compared. Dot width over stem width in Regular is
    # 1.20, against 1.57 to 1.67 in JetBrains Mono, IBM Plex Mono, DM Mono,
    # and Source Code Pro; in Bold, 1.14 against 1.20 to 1.33. Scaling keeps
    # Roboto's own progression across weights.
    SCALE = 1.15
    # JetBrains Mono, DM Mono, and Source Code Pro center their dots about
    # 0.009 em left of the stem center. That compensates for the top serif
    # of i and the hook of j, which both pull the letter's mass to the left.
    # Upstream offsets range from 0 to 0.004 em.
    OFFSET = 0.009

    def redraw(self, font, style):
        gap = round(self.GAP * style.em)
        offset = self.OFFSET * style.em
        upright, slanted = (1, 0, -style.slant, 1, 0, 0), (1, 0, style.slant, 1, 0, 0)
        for name, count in self.DOTS.items():
            glyph = font[name]
            stem_top, dots = self._split(glyph)
            if len(dots) != count:
                raise ValueError("Expected %d dot(s) on %s" % (count, name))
            layer = glyph.foreground
            stems = self._stems([layer[i] for i in range(len(layer)) if i not in dots], stem_top, upright)
            for index in dots:
                dot = layer[index]
                measured = dot.dup()
                measured.transform(upright)
                left, bottom, right, _ = measured.boundingBox()
                center = (left + right) / 2
                stem = min(stems, key=lambda span: abs(sum(span) / 2 - center))
                if not stem[0] < center < stem[1]:
                    raise ValueError("Expected each dot of %s above a stem" % name)
                lift = stem_top + gap - bottom
                if abs(lift) > gap:
                    raise ValueError("Unexpected dot position on " + name)
                # In upright coordinates: grow from the bottom center, so the gap
                # holds, then center the dot OFFSET left of the stem.
                k = self.SCALE
                grow = (k, 0, 0, k, center * (1 - k), bottom * (1 - k))
                move = psMat.translate(sum(stem) / 2 - offset - center, lift)
                transform = upright
                for step in (grow, move, slanted):
                    transform = psMat.compose(transform, step)
                dot.transform(transform)
                layer[index] = dot
            glyph.foreground = layer
            glyph.round()

    @staticmethod
    def _split(glyph):
        """Top of the letter body and indices of the contours above it (dots)."""
        if glyph.references:
            raise ValueError("Expected %s to be drawn without references" % glyph.glyphname)
        layer = glyph.foreground
        body_top = min(contour.boundingBox()[3] for contour in layer)
        dots = [index for index, contour in enumerate(layer) if contour.boundingBox()[1] > body_top]
        return max(layer[i].boundingBox()[3] for i in range(len(layer)) if i not in dots), dots

    @staticmethod
    def _stems(body, stem_top, upright):
        """Left and right edges of the stems, in upright coordinates.

        Measured on the straight part of the stem, between the bottom serif
        and the top serif or crossbar.
        """
        height = 0.6 * stem_top
        crossings = []
        for contour in body:
            contour = contour.dup()
            contour.transform(upright)
            points = [(point.x, point.y) for point in contour if point.on_curve]
            for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1]):
                if (y1 - height) * (y2 - height) < 0:
                    crossings.append(x1 + (height - y1) * (x2 - x1) / (y2 - y1))
        crossings.sort()
        if not crossings or len(crossings) % 2:
            raise ValueError("Could not measure the stems")
        return list(zip(crossings[::2], crossings[1::2]))
