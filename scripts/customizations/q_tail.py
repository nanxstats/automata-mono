"""Q: a straight tail cut flat, instead of Roboto's tail cut square to the stroke."""

import math

import fontforge

from .base import Customization
from .geometry import Line, ahead, bounds, lerp, quadratic, rounded, segments
from .outline import contour, replace_contours


class FlatTailQ(Customization):
    name = "flat-tail-q"
    summary = (
        "Q: straight tail cut flat, ending under the right edge of the bowl, "
        "as in JetBrains Mono and DM Mono"
    )
    redraws = ("Q", "Q.smcp")

    # Degrees from the horizontal. JetBrains Mono's tail leans 59 degrees and
    # DM Mono's 46 to 48; both cut it flat, 1.0 to 1.3 times as wide as the
    # bowl's stroke. Upstream's leans 40 to 46 degrees, at which a flat cut
    # would be up to 1.5 strokes wide and end in a sharp point.
    ANGLE = 50
    # Upstream, the tail's edges lean up to 1 degree apart.
    PARALLEL = 2

    def redraw(self, font, style):
        for name in self.redraws:
            self._redraw(font[name], style)

    def _redraw(self, glyph, style):
        """Replace the tail with a straight one cut flat at the same depth.

        Upstream, the bowl's outer edge stops where the tail leaves it, and
        the tail is four corners in a row: its two edges, nearly parallel,
        and an end cut square to them. The bowl's outer edge is closed under
        the tail with one curve, tangent to upstream's on both sides. The
        new tail keeps upstream's thickness and depth, leans at ANGLE, and
        is cut flat, its right corner under the bowl's right edge. Built in
        upright coordinates, so italics get the upright design slanted.
        """
        name = glyph.glyphname
        layer = glyph.foreground
        if glyph.references or len(layer) != 2:
            raise ValueError(f"Expected {name} to be a bowl with a tail, and a counter")
        index = min(range(2), key=lambda i: layer[i].boundingBox()[1])
        original = layer[index]
        points = [(style.upright(p.x, p.y), p.y, p.on_curve) for p in original]
        count = len(points)

        def xy(i):
            return points[i][:2]

        starts = [
            i
            for i in range(count)
            if all(points[(i + k) % count][2] for k in range(4))
            and not points[(i - 1) % count][2]
            and not points[(i + 4) % count][2]
        ]
        if len(starts) != 1:
            raise ValueError(f"Expected the tail of {name} to be four corners in a row")
        run = [(starts[0] + k) % count for k in range(4)]
        # `step` walks along the bottom of the bowl, down the tail's left
        # edge, and up its right edge into the bowl again.
        step = 1
        if Line(xy(run[0]), xy(run[1])).x_at(0) > Line(xy(run[3]), xy(run[2])).x_at(0):
            run.reverse()
            step = -1
        join_left, end_left, end_right, join_right = run
        left, right = (
            Line(xy(join_left), xy(end_left)),
            Line(xy(join_right), xy(end_right)),
        )
        lean = [
            math.degrees(math.atan2(a[1] - b[1], b[0] - a[0]))
            for a, b in ((left.a, left.b), (right.a, right.b))
        ]
        if not (
            max(points[end_left][1], points[end_right][1]) < 0
            and min(points[join_left][1], points[join_right][1])
            > max(points[end_left][1], points[end_right][1])
            and all(0 < angle < 90 for angle in lean)
            and abs(lean[0] - lean[1]) < self.PARALLEL
        ):
            raise ValueError(
                f"Expected {name} to have a straight tail down to the right"
            )
        thickness = (
            sum(right.distance(xy(i)) for i in (join_left, end_left))
            + sum(left.distance(xy(i)) for i in (join_right, end_right))
        ) / 4
        depth = min(points[end_left][1], points[end_right][1])

        before, after = (join_left - step) % count, (join_right + step) % count
        handle = Line(xy(before), xy(join_left)).intersection(
            Line(xy(join_right), xy(after))
        )
        if not (
            ahead(xy(before), xy(join_left), handle)
            and ahead(handle, xy(join_right), xy(after))
        ):
            raise ValueError(f"Expected the bowl of {name} to curve under its tail")
        # The bowl, closed under the tail, from the tail's right edge around
        # to its left edge. `sources` maps it back to upstream's points.
        sources = [join_right]
        while sources[-1] != join_left:
            sources.append((sources[-1] + step) % count)
        sources.append(None)
        bowl = [points[i] for i in sources[:-1]] + [(*handle, False)]
        reach = bounds(bowl)[2]
        if depth >= bounds(bowl)[1]:
            raise ValueError(f"Expected the tail of {name} to hang below the bowl")

        angle = math.radians(self.ANGLE)
        new_right = Line(
            (reach, depth), (reach - style.em / math.tan(angle), depth + style.em)
        )
        new_left = new_right.shifted(-thickness / math.sin(angle))
        pieces = segments(bowl)
        cut_left, cut_right = (
            self._crossing(bowl, pieces, line, name) for line in (new_left, new_right)
        )
        # Both edges may leave the curve that closes the bowl under the tail.
        if (cut_right[0] - cut_left[0]) % len(pieces) > len(pieces) // 4 or (
            cut_left[0] == cut_right[0] and cut_left[1] >= cut_right[1]
        ):
            raise ValueError(
                f"Expected the new tail of {name} to leave the bottom of the bowl"
            )

        def new(point, on_curve=True):
            x, y = rounded(style.slanted(*point))
            return fontforge.point(x, y, on_curve)

        def kept(position, boundary=False):
            if sources[position] is None:
                return new(bowl[position][:2], bowl[position][2])
            point = original[sources[position]]
            if boundary:
                # A neighboring handle moves, so an implied point is implied
                # no longer; round it as TrueType will.
                return fontforge.point(round(point.x), round(point.y), point.on_curve)
            return point

        def curve(segment):
            start, control, end = pieces[segment]
            p0, p2 = bowl[start][:2], bowl[end][:2]
            return p0, (bowl[control][:2] if control is not None else None), p2

        outline = []
        segment, t = cut_right
        p0, p1, p2 = curve(segment)
        outline.append(new(quadratic(p0, p1 or lerp(p0, p2, 0.5), p2, t)))
        if p1 is not None:
            outline.append(new(lerp(p1, p2, t), False))
        outline.append(kept(pieces[segment][2], boundary=True))
        segment = (segment + 1) % len(pieces)
        while segment != cut_left[0]:
            start, control, end = pieces[segment]
            if control is not None:
                outline.append(kept(control))
            outline.append(
                kept(end, boundary=(segment + 1) % len(pieces) == cut_left[0])
            )
            segment = (segment + 1) % len(pieces)
        t = cut_left[1]
        p0, p1, p2 = curve(segment)
        if p1 is not None:
            outline.append(new(lerp(p0, p1, t), False))
        outline.append(new(quadratic(p0, p1 or lerp(p0, p2, 0.5), p2, t)))
        outline += [new((new_left.x_at(depth), depth)), new((reach, depth))]
        if step < 0:
            outline.reverse()
        replace_contours(
            glyph,
            [
                contour(outline, like=original) if i == index else layer[i]
                for i in range(2)
            ],
        )

    @staticmethod
    def _crossing(bowl, pieces, line, name):
        """Where a tail edge leaves the bottom of the bowl: (segment, t).

        The bowl is convex, so the line crosses it twice; the tail hangs
        from the lower crossing.
        """
        found = []
        for segment, (start, control, end) in enumerate(pieces):
            p0, p2 = bowl[start][:2], bowl[end][:2]
            if line.offset(p0) * line.offset(p2) < 0:
                p1 = bowl[control][:2] if control is not None else lerp(p0, p2, 0.5)
                t = line.crossing(p0, p1, p2)
                found.append((quadratic(p0, p1, p2, t)[1], segment, t))
        if len(found) != 2:
            raise ValueError(f"Expected the tail of {name} to cross the bowl twice")
        _, segment, t = min(found)
        return segment, t
