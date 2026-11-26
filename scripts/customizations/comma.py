"""Comma: a straight, slightly tapered stroke instead of Roboto's hooked tail."""

from .base import Customization
from .geometry import rounded
from .outline import contour, replace_contours, single_contour


class StraightComma(Customization):
    name = "straight-comma"
    summary = "Comma and semicolon: straight tapered tail in the style of JetBrains Mono"
    redraws = ("comma",)
    inherits = ("semicolon",)
    # Cyrillic letters with a tail (Ҋ Ӆ Ӊ Ӎ and lowercase) reuse the comma as
    # their descender. That is a different design element, so keep it.
    preserves = (
        "uni048A", "uni048B", "uni04C5", "uni04C6",
        "uni04C9", "uni04CA", "uni04CD", "uni04CE",
    )

    # Proportions measured from JetBrains Mono, which keeps them across weights:
    # the left edge leans about 10 degrees from vertical (dx/dy = 0.18), and
    # the foot is about 85% as wide as the head.
    LEAN = 0.18
    TAPER = 0.85

    def redraw(self, font, style):
        """Keep Roboto's head (position, width, top) and depth; straighten the tail.

        Roboto scales the head width with the stem weight, and the semicolon
        places its comma by the same head, so both stay aligned.
        """
        glyph = font["comma"]
        original = single_contour(glyph)
        top = max(point.y for point in original)
        bottom = min(point.y for point in original)
        head = [point for point in original if point.on_curve and point.y == top]
        if len(head) != 2:
            raise ValueError("Expected a flat comma head with two corners")
        left, right = sorted(style.upright(point.x, point.y) for point in head)
        foot_left = left - self.LEAN * (top - bottom)
        foot_right = foot_left + self.TAPER * (right - left)
        corners = [(left, top), (right, top), (foot_right, bottom), (foot_left, bottom)]
        corners = [rounded(style.slanted(x, y)) for x, y in corners]
        if not original.isClockwise():
            corners.reverse()
        replace_contours(glyph, [contour(corners, like=original)])
