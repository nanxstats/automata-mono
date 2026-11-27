"""Comma: a straight, slightly tapered stroke instead of Roboto's hooked tail."""

from .base import Customization
from .geometry import rounded
from .outline import contour, replace_contours, single_contour
from .punctuation_dots import LargerDots


class StraightComma(Customization):
    name = "straight-comma"
    summary = (
        "Comma and semicolon: straight tapered tail in the style of JetBrains Mono"
    )
    redraws = ("comma",)
    inherits = ("semicolon",)
    # Cyrillic letters with a tail (Ҋ Ӆ Ӊ Ӎ and lowercase) reuse the comma as
    # their descender. That is a different design element, so keep it.
    preserves = (
        "uni048A",
        "uni048B",
        "uni04C5",
        "uni04C6",
        "uni04C9",
        "uni04CA",
        "uni04CD",
        "uni04CE",
    )

    # The left edge leans about 10 degrees from vertical (dx/dy = 0.18), as
    # in JetBrains Mono, which keeps it across weights.
    LEAN = 0.18
    # The head grows with the period (see punctuation_dots.py): it widens as
    # much, keeping Roboto's 0.69 of the period's width in Regular, between
    # JetBrains Mono's 0.66 and DM Mono's 0.74. The foot keeps its width, so
    # it is 0.74 as wide as the head, as in DM Mono (0.72 to 0.76); JetBrains
    # Mono's is 0.85 as wide.
    HEAD = LargerDots.SCALE
    TAPER = 0.74

    def redraw(self, font, style):
        """Keep Roboto's head center and depth; grow the head, straighten the tail.

        Roboto scales the head width with the stem weight, and the semicolon
        places its comma by the center of the same head, so both stay
        aligned. The head grows with the period: it widens about its center,
        and its top rises as far as the period's. So it keeps its height
        relative to the period, from 23 units per 1000 em above it (Thin) to
        50 below (Bold). The fonts compared end their commas level with their
        periods.
        """
        glyph = font["comma"]
        original = single_contour(glyph)
        top = max(point.y for point in original)
        bottom = min(point.y for point in original)
        head = [point for point in original if point.on_curve and point.y == top]
        if len(head) != 2:
            raise ValueError("Expected a flat comma head with two corners")
        left, right = sorted(style.upright(point.x, point.y) for point in head)
        center, half = (left + right) / 2, self.HEAD * (right - left) / 2
        left, right = center - half, center + half
        top += LargerDots.period(font["period"], style)[1]
        foot_left = left - self.LEAN * (top - bottom)
        foot_right = foot_left + self.TAPER * (right - left)
        corners = [(left, top), (right, top), (foot_right, bottom), (foot_left, bottom)]
        corners = [rounded(style.slanted(x, y)) for x, y in corners]
        if not original.isClockwise():
            corners.reverse()
        replace_contours(glyph, [contour(corners, like=original)])
