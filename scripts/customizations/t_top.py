"""t: a taller stem above the crossbar."""

import fontforge

from .base import Customization
from .outline import contour, replace_contours, single_contour


class TallerT(Customization):
    name = "taller-t"
    summary = "t: stem raised to 86% of the way from x-height to cap height, as in JetBrains Mono"
    redraws = ("t", "tbar")  # ŧ draws its own copy of the t outline
    inherits = ("tcaron", "uni0163", "uni021B")  # ť ţ ț

    # How far the stem rises from the x-height toward the cap height.
    # Upstream: 0.70 in Regular through Bold, up to 0.78 in Thin, which makes
    # t read close to + and f at small sizes. Fira Code is about 0.80, and
    # JetBrains Mono 0.86 in every weight. The cap height is the reference
    # because Roboto's ascenders rise above it; t stays shorter than capitals.
    HEIGHT = 0.86

    def redraw(self, font, style):
        target = round(style.x_height + self.HEIGHT * (style.cap_height - style.x_height))
        for name in self.redraws:
            glyph = font[name]
            original = single_contour(glyph)
            points = list(original)
            count = len(points)
            top = max(point.y for point in points)
            corners = [i for i, point in enumerate(points) if point.on_curve and point.y == top]
            if len(corners) != 2 or (corners[1] - corners[0]) % count not in (1, count - 1):
                raise ValueError("Expected a flat stem top on " + name)
            lift = target - top
            if not 0 < lift < style.cap_height - style.x_height:
                raise ValueError("Unexpected stem height on " + name)
            for corner in corners:
                # The stem must run straight down from each corner to the crossbar.
                below = [points[(corner + step) % count] for step in (-1, 1)]
                below = [point for point in below if point.y != top]
                if len(below) != 1 or not below[0].on_curve or abs(below[0].y - style.x_height) > 4:
                    raise ValueError("Expected straight stem edges on " + name)
            for corner in corners:
                # Move along the italic angle so the stem edges stay straight.
                point = points[corner]
                points[corner] = fontforge.point(point.x + round(lift * style.slant), target, True)
            replace_contours(glyph, [contour(points, like=original)])
