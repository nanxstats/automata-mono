"""[ and ]: longer arms, the same length in every weight."""

import fontforge

from .base import Customization
from .outline import contour, replace_contours, single_contour


class LongerBrackets(Customization):
    name = "longer-brackets"
    summary = "[ and ]: arms extend a constant 0.30 of the cell past the stem in every weight"
    redraws = ("bracketleft", "bracketright")

    # Arm length past the inner edge of the stem, as a fraction of the cell.
    # Upstream shortens the arms as the stem gets heavier: 0.196 in Thin, 0.180
    # in Regular, 0.138 in Bold. JetBrains Mono keeps them at about 0.26 in
    # every weight; IBM Plex Mono and Source Code Pro at about 0.35. In
    # between, the overall bracket width falls within their range.
    ARM = 0.30

    def redraw(self, font, style):
        cell = font["space"].width
        for name, direction in (("bracketleft", 1), ("bracketright", -1)):
            glyph = font[name]
            original = single_contour(glyph)
            points = list(original)
            levels = {}
            for index, point in enumerate(points):
                if not point.on_curve:
                    raise ValueError("Expected %s to be drawn with straight edges" % name)
                levels.setdefault(point.y, []).append(index)
            if len(points) != 8 or len(levels) != 4 or any(len(pair) != 2 for pair in levels.values()):
                raise ValueError("Expected %s to be a stem with two arms" % name)
            # Each height has one point on the stem side and one at an arm tip.
            # The arms' inner edges are the middle two heights.
            heights = sorted(levels)
            tips = {}
            for y, pair in levels.items():
                stem_side, tip = sorted(pair, key=lambda index: direction * points[index].x)
                tips[y] = (tip, points[tip].x - points[stem_side].x)
            for outer, inner in ((heights[0], heights[1]), (heights[3], heights[2])):
                # Move both tip points of the arm by the same amount, so the
                # tip keeps its slant in italics.
                shift = direction * round(self.ARM * cell) - tips[inner][1]
                if direction * shift <= 0:
                    raise ValueError("Expected %s arms shorter than the target" % name)
                for y in (outer, inner):
                    index = tips[y][0]
                    x = points[index].x + shift
                    if not 0 <= x <= cell:
                        raise ValueError("Bracket arm leaves the cell in " + name)
                    points[index] = fontforge.point(x, y, True)
            replace_contours(glyph, [contour(points, like=original)])
