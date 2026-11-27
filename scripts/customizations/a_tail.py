"""a: a straight stem cut flat at the baseline instead of Roboto's spur."""

import fontforge

from .base import Customization
from .geometry import Line, lerp, quadratic, rounded
from .outline import contour, replace_contours


class StraightTailA(Customization):
    name = "straight-a"
    summary = ("a: stem runs straight to a flat foot on the baseline, "
               "as in JetBrains Mono, DM Mono, and Source Code Pro")
    redraws = ("a", "aogonek")  # ą draws its own copy of the a outline
    inherits = (
        "aacute", "abreve", "acircumflex", "adieresis", "agrave",  # á ă â ä à
        "amacron", "aring", "aringacute", "atilde",  # ā å ǻ ã
        "uni1E01", "uni1EA1", "uni1EA3", "uni1EA5", "uni1EA7", "uni1EA9",  # ḁ ạ ả ấ ầ ẩ
        "uni1EAB", "uni1EAD", "uni1EAF", "uni1EB1", "uni1EB3", "uni1EB5", "uni1EB7",  # ẫ ậ ắ ằ ẳ ẵ ặ
        "uni0430", "uni04D1", "uni04D3",  # Cyrillic а ӑ ӓ
    )

    # The foot starts where the bowl meets the stem. Upstream, that is up to
    # 4% of the stem width right of the stem's inner edge in upright styles
    # and up to 10% in italics, so the foot is that much narrower than the
    # stem. Much narrower would no longer read as the same stem.
    MIN_FOOT = 0.85

    def redraw(self, font, style):
        for name in self.redraws:
            self._straighten(font[name], style)

    def _straighten(self, glyph, style):
        """Extend the stem's outer edge to the baseline and cut it flat.

        Upstream, the stem bends right below its straight outer edge into a
        spur, and the foot's inner edge leans right from where the bowl meets
        the stem. That foot is replaced by a parallelogram that continues the
        outer edge, with its inner edge parallel to it through the bowl
        junction, so the bowl stays as drawn. In ą, the ogonek hangs from the
        foot: it moves to the new outer corner, and the foot's inner edge
        meets its inner curve.
        """
        name = glyph.glyphname
        if glyph.references:
            raise ValueError("Expected %s to be drawn without references" % name)
        layer = glyph.foreground
        standing = [i for i in range(len(layer)) if any(p.on_curve and p.y == 0 for p in layer[i])]
        if len(standing) != 1 or len(layer) != 2:
            raise ValueError("Expected %s to be an outline and a counter" % name)
        original, counter = layer[standing[0]], layer[1 - standing[0]]
        points = list(original)
        count = len(points)

        def xy(index):
            return points[index].x, points[index].y

        def step(index, direction):
            return (index + direction) % count

        # The outer edge of the stem is the longest straight edge. `up` walks
        # from the bowl through the foot to the stem: bottom, then top.
        top, bottom = sorted(self._longest_edge(original), key=lambda i: -points[i].y)
        if points[top].y - points[bottom].y < style.x_height / 3:
            raise ValueError("Expected a straight stem on " + name)
        up = 1 if step(bottom, 1) == top else -1
        outer = Line(xy(bottom), xy(top))

        # Below the straight edge, the spur runs down to a corner on the
        # baseline, right of the edge.
        corner = bottom
        while not (points[corner].on_curve and points[corner].y == 0):
            corner = step(corner, -up)
            if not 0 <= points[corner].y < points[bottom].y:
                raise ValueError("Unexpected spur on " + name)
        if outer.offset(xy(corner)) <= 0:
            raise ValueError("Expected the spur of %s to stick out past the stem" % name)
        # Next comes the foot's left corner, or the end of the ogonek.
        left = step(corner, -up)
        if not (points[left].on_curve and points[left].y == 0):
            raise ValueError("Expected a flat foot on " + name)
        ogonek = points[step(left, -up)].y < 0

        # The bowl meets the foot at the first peak above the baseline.
        junction = left
        for _ in range(count):
            following = step(junction, -up)
            if points[junction].y > 0 and points[following].y < points[junction].y:
                break
            junction = following
        if not points[junction].on_curve or not 0 < points[junction].y < points[bottom].y:
            raise ValueError("Expected the bowl of %s to meet the stem above the foot" % name)
        foot = -outer.offset(xy(junction))
        stem = -outer.offset(self._midpoint(counter, self._longest_edge(counter)))
        if not self.MIN_FOOT * stem <= foot <= stem + 1:
            raise ValueError("Expected the bowl of %s to meet the stem at its inner edge" % name)
        inner = outer.shifted(-foot)
        outer_corner = rounded((outer.x_at(0), 0))

        if not ogonek:
            foot_points = [rounded((inner.x_at(0), 0)), outer_corner]
        else:
            foot_points = self._ogonek(points, junction, left, up, inner, outer_corner, name)

        kept = []
        index = top
        while index != junction:
            kept.append(points[index])
            index = step(index, up)
        outline = kept + [points[junction]] + foot_points
        if up < 0:
            outline.reverse()
        new = contour(outline, like=original)
        replace_contours(glyph, [new if i == standing[0] else layer[i] for i in range(len(layer))])

    @staticmethod
    def _ogonek(points, junction, end, up, inner, outer_corner, name):
        """The ogonek's points, from the foot's inner edge to the outer corner.

        The ogonek leaves the foot's inner edge just above the baseline and
        ends on the baseline near the outer corner. It moves sideways so that
        it ends at the corner, and its first curve is cut where it crosses
        the foot's inner edge.
        """
        count = len(points)
        # The last on-curve point above the baseline; in italics, the first
        # control point of the ogonek is still slightly above it.
        attach = index = junction
        while points[index].y > 0:
            if points[index].on_curve:
                attach = index
            index = (index + up) % count
        shift = outer_corner[0] - points[end].x
        ogonek = []
        index = attach
        while True:
            point = points[index]
            ogonek.append(fontforge.point(point.x + shift, point.y, point.on_curve))
            if index == end:
                break
            index = (index + up) % count
        first, control, second = ((point.x, point.y) for point in ogonek[:3])
        if not (ogonek[0].on_curve and not ogonek[1].on_curve and ogonek[2].on_curve):
            raise ValueError("Expected the ogonek of %s to start with a curve" % name)
        if inner.offset(first) <= 0 or inner.offset(second) >= 0:
            raise ValueError("Expected the ogonek of %s to cross the stem's inner edge" % name)
        t = inner.crossing(first, control, second)
        cut = rounded(quadratic(first, control, second, t))
        control = rounded(lerp(control, second, t))
        return [cut, fontforge.point(control[0], control[1], False)] + ogonek[2:]

    @staticmethod
    def _longest_edge(outline):
        """Indices of the ends of the straight edge that spans the most height."""
        points = list(outline)
        count = len(points)
        edges = [(i, (i + 1) % count) for i in range(count)
                 if points[i].on_curve and points[(i + 1) % count].on_curve]
        if not edges:
            raise ValueError("Expected straight edges")
        return max(edges, key=lambda edge: abs(points[edge[1]].y - points[edge[0]].y))

    @staticmethod
    def _midpoint(outline, edge):
        a, b = (outline[i] for i in edge)
        return (a.x + b.x) / 2, (a.y + b.y) / 2
