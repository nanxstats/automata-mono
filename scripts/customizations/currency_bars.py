"""$ and ¢: the bar runs through the glyph instead of stopping at its outline."""

import math

import fontforge

from .base import Customization
from .geometry import rounded
from .outline import contour, replace_contours, single_contour


class FullCurrencyBars(Customization):
    name = "full-currency-bars"
    summary = ("$ and ¢: bar runs through the glyph from top to bottom, "
               "as in JetBrains Mono, IBM Plex Mono, and DM Mono")
    # Counters the bar closes: in $, one in each bowl; in ¢, the left of c's.
    COUNTERS = {"dollar": 2, "cent": 1}
    redraws = tuple(COUNTERS)

    # Italic bar ends lean up to 0.7 degrees off the italic angle.
    LEAN = 0.02
    # Where a bar edge crosses the body this close to one of its points, the
    # crossing takes the point's place instead of leaving a sliver of curve
    # between them.
    SLIVER = 8

    def redraw(self, font, style):
        """Run a straight bar between upstream's bar ends.

        Upstream, the ends of the bar stick out above and below the outline
        but do not cross it. In $, they are 0.81 as wide as the stem of n in
        Regular. JetBrains Mono, IBM Plex Mono, and DM Mono draw their bars
        0.50 to 0.83 as wide as their stems, the same in $ and ¢. Roboto's ¢
        ends are as wide as the stroke of c, which would clog the counter the
        bar crosses, so ¢ takes the width of $'s bar.
        """
        bars = {name: self._bar(font[name], style) for name in self.redraws}
        width = round(bars["dollar"][1] - bars["dollar"][0])
        for name, (left, right, bottom, top) in bars.items():
            left = round((left + right - width) / 2)
            self._redraw(font[name], style, (left, left + width, bottom, top), self.COUNTERS[name])

    def _bar(self, glyph, style):
        """Left and right edges of the bar, in upright coordinates, and its ends.

        The two ends of the bar may sit a few units apart; the bar runs
        straight between them, halfway between their positions.
        """
        name = glyph.glyphname
        points = list(single_contour(glyph))
        lefts, rights = [], []
        for _, before, a, b, after in self._ends(points, name):
            sides = sorted(((points[a], points[before]), (points[b], points[after])),
                           key=lambda side: style.upright(side[0].x, side[0].y))
            for (corner, join), edges in zip(sides, (lefts, rights)):
                x0, x1 = style.upright(corner.x, corner.y), style.upright(join.x, join.y)
                if abs(x0 - x1) > self.LEAN * abs(corner.y - join.y):
                    raise ValueError("Expected the bar ends of %s to have straight sides" % name)
                edges += [x0, x1]
        bottom, top = min(p.y for p in points), max(p.y for p in points)
        return sum(lefts) / len(lefts), sum(rights) / len(rights), bottom, top

    @staticmethod
    def _ends(points, name):
        """The bar's two ends: the corner pair at the top or bottom of the
        outline, and the on-curve points where its sides meet the body.

        Yields (y, before, a, b, after) with indices in contour order.
        """
        count = len(points)
        for y in (min(p.y for p in points), max(p.y for p in points)):
            corners = [i for i, point in enumerate(points) if point.y == y]
            if len(corners) != 2 or not all(points[i].on_curve for i in corners):
                raise ValueError("Expected the bar of %s to end flat" % name)
            a, b = corners if (corners[0] + 1) % count == corners[1] else corners[::-1]
            if (a + 1) % count != b:
                raise ValueError("Expected the bar of %s to end flat" % name)
            before, after = (a - 1) % count, (b + 1) % count
            if not (points[before].on_curve and points[after].on_curve):
                raise ValueError("Expected the bar ends of %s to have straight sides" % name)
            yield y, before, a, b, after

    def _redraw(self, glyph, style, bar, counters):
        """Cut the ends off the outline and merge a full-height bar into it.

        Where the bar crosses the body, the body's outline is cut at the bar's
        edges; elsewhere it is unchanged.
        """
        name = glyph.glyphname
        original = single_contour(glyph)
        points = list(original)
        ends = {i for _, _, a, b, _ in self._ends(points, name) for i in (a, b)}
        body = contour([p for i, p in enumerate(points) if i not in ends], like=original)
        left, right, bottom, top = bar
        corners = [rounded(style.slanted(x, y))
                   for x, y in ((left, bottom), (right, bottom), (right, top), (left, top))]
        if original.isClockwise():
            corners.reverse()
        replace_contours(glyph, [body, contour(corners, like=original)])
        glyph.removeOverlap()
        layer = glyph.foreground
        if len(layer) != 1 + counters:
            raise ValueError("Expected the bar of %s to close %d counter(s)" % (name, counters))
        upstream = {(p.x, p.y) for p in points}
        replace_contours(glyph, [self._without_slivers(c, upstream) for c in layer])

        kept = {(p.x, p.y) for c in glyph.foreground for p in c if p.on_curve}
        outside = [p for i, p in enumerate(points) if i not in ends and p.on_curve
                   and not left - self.SLIVER <= style.upright(p.x, p.y) <= right + self.SLIVER]
        if any((p.x, p.y) not in kept for p in outside):
            raise ValueError("Merging the bar into %s changed the outline away from it" % name)

    def _without_slivers(self, outline, upstream):
        """Drop body points next to where a bar edge crosses the body.

        Removes the on-curve point and any off-curve point between it and the
        crossing, so the body's curve runs to the crossing instead.
        """
        points = list(outline)

        def crossing(point):
            return point.on_curve and (point.x, point.y) not in upstream

        while True:
            count = len(points)
            sliver = None
            for index, point in enumerate(points):
                if not crossing(point):
                    continue
                for direction in (1, -1):
                    between = []
                    other = (index + direction) % count
                    if not points[other].on_curve:
                        between.append(other)
                        other = (other + direction) % count
                    neighbor = points[other]
                    if neighbor.on_curve and not crossing(neighbor) and \
                            math.dist((point.x, point.y), (neighbor.x, neighbor.y)) < self.SLIVER:
                        sliver = set(between + [other])
                        break
                if sliver:
                    break
            if not sliver:
                break
            points = [point for index, point in enumerate(points) if index not in sliver]
        result = fontforge.contour()
        result.is_quadratic = outline.is_quadratic
        for point in points:
            result += point
        result.closed = True
        return result
