"""%: a full-height slash cut flat, instead of Roboto's short stroke."""

import math

from .base import Customization
from .geometry import Line, rounded
from .outline import contour, replace_contours


class FullPercentSlash(Customization):
    name = "full-percent-slash"
    summary = ("%: slash runs from the baseline to the cap height between the rings' "
               "outer corners, cut flat, as in JetBrains Mono")
    redraws = ("percent",)

    def redraw(self, font, style):
        """Draw the slash corner to corner across the rings, keeping its thickness.

        Upstream, the slash covers only the middle of the glyph, and its ends
        are cut square to the stroke. JetBrains Mono runs it from the
        baseline at the left of the rings to the cap height at their right,
        cut flat like /. Measured in upright coordinates, so italics are the
        upright design slanted, as in JetBrains Mono; their slash reaches a
        little past the cell, as several upstream italic glyphs do.
        """
        glyph = font["percent"]
        if glyph.references:
            raise ValueError("Expected % to be drawn without references")
        layer = glyph.foreground
        slashes = [i for i in range(len(layer))
                   if len(layer[i]) == 4 and all(point.on_curve for point in layer[i])]
        if len(layer) != 5 or len(slashes) != 1:
            raise ValueError("Expected % to be two rings, each with a counter, and a slash")
        original = layer[slashes[0]]
        upright = (1, 0, -style.slant, 1, 0, 0)
        rings, left, right = [], math.inf, -math.inf
        for index in range(len(layer)):
            if index != slashes[0]:
                ring = layer[index].dup()
                ring.transform(upright)
                x_min, _, x_max, _ = ring.boundingBox()
                left, right = min(left, x_min), max(right, x_max)
                rings.append([(point.x, point.y) for point in ring])

        old = self._corners([(style.upright(p.x, p.y), p.y) for p in original])
        thickness = self._thickness(old)
        height = style.cap_height
        run = right - left
        # The horizontal width w that keeps the thickness at the new angle:
        # thickness = w * height / hypot(height, run - w).
        a = height ** 2 - thickness ** 2
        b = 2 * thickness ** 2 * run
        c = -thickness ** 2 * (height ** 2 + run ** 2)
        width = (-b + math.sqrt(b * b - 4 * a * c)) / (2 * a)
        new = [(left, 0), (left + width, 0), (right, height), (right - width, height)]
        # Less steep than upstream's, the slash ends up 5% to 35% farther from
        # the rings; it must never come closer.
        if self._clearance(rings, new) < self._clearance(rings, old):
            raise ValueError("The slash of % would crowd its rings")

        corners = [rounded(style.slanted(x, y)) for x, y in new]
        if original.isClockwise():
            corners.reverse()
        slash = contour(corners, like=original)
        replace_contours(glyph, [slash if i == slashes[0] else layer[i] for i in range(len(layer))])

    @staticmethod
    def _corners(points):
        """Bottom left, bottom right, top right, and top left of a slash."""
        points = sorted(points, key=lambda point: point[1])
        (bottom_left, bottom_right), (top_left, top_right) = sorted(points[:2]), sorted(points[2:])
        if top_left[0] <= bottom_left[0]:
            raise ValueError("Expected the slash of % to rise to the right")
        return [bottom_left, bottom_right, top_right, top_left]

    @staticmethod
    def _sine(bottom, top):
        """Converts horizontal distances from the line through bottom and top to perpendicular ones."""
        return (top[1] - bottom[1]) / math.dist(bottom, top)

    def _thickness(self, corners):
        bottom_left, bottom_right, top_right, top_left = corners
        left_side = Line(bottom_left, top_left)
        bottom, top = left_side.offset(bottom_right), left_side.offset(top_right)
        if bottom <= 0 or abs(bottom - top) > 0.01 * bottom:
            raise ValueError("Expected the slash of % to be a parallelogram")
        return bottom * self._sine(bottom_left, top_left)

    def _clearance(self, rings, corners):
        """Smallest gap between the slash's sides and the rings on either side.

        Measured to the control points, whose hull contains each contour.
        """
        bottom_left, bottom_right, top_right, top_left = corners
        left_side, right_side = Line(bottom_left, top_left), Line(bottom_right, top_right)
        gaps = {}
        for points in rings:
            above = -max(left_side.offset(point) for point in points)
            below = min(right_side.offset(point) for point in points)
            if max(above, below) <= 0:
                raise ValueError("Expected the rings of % on either side of the slash")
            side = "above" if above > 0 else "below"
            gaps[side] = min(gaps.get(side, math.inf), max(above, below))
        if len(gaps) != 2:
            raise ValueError("Expected one ring of % on each side of the slash")
        return min(gaps.values()) * self._sine(bottom_left, top_left)
