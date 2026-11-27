"""6 and 9: a straight stroke from the bowl, instead of Roboto's curved one."""

import math

import fontforge

from .base import Customization
from .geometry import Line, bounds, extent, lerp, quadratic, rounded, segments, turn
from .outline import contour, implied, replace_contours, single_contour


class OpenSixNine(Customization):
    name = "open-six-nine"
    summary = (
        "6 and 9: straight stroke tangent to the counter, cut flat at the "
        "figure height and on the baseline, as in JetBrains Mono"
    )
    redraws = ("six", "nine")

    # Degrees from the horizontal. JetBrains Mono's strokes lean 58 to 61
    # degrees, Google Sans Code's 48 to 53. At 60, the stroke's outer edge
    # reaches the figure height within 0.03 of the cell of the middle of the
    # bowl, and JetBrains Mono's within 0.04.
    ANGLE = 60
    # Degrees. The bowl's outer edge has one straight side, upright or
    # nearly so in italics, below where the stroke leaves it.
    SIDE = 10
    # Degrees. The side is redrawn from the first on-curve point below it
    # where the bowl has turned this far toward its bottom. Upstream, that
    # point has turned 32 to 41 degrees, about halfway around the bowl's
    # corner, and the points above it at most 21.
    BASE = 30
    # Degrees. Upstream, the counter's one corner turns 7 to 27 degrees, and
    # its smooth points turn at most 3.
    CORNER = 5

    def redraw(self, font, style):
        seven = font["seven"]
        thickness = self._leg(seven, style)
        height = seven.boundingBox()[3]
        self._redraw(font["six"], style, thickness, height, turned=False)
        self._redraw(font["nine"], style, thickness, 0, turned=True)

    @staticmethod
    def _leg(glyph, style):
        """Thickness of 7's leg where it is cut flat at the baseline."""
        points = list(single_contour(glyph))
        count = len(points)

        def upright(index):
            return style.upright(points[index].x, points[index].y), points[index].y

        baseline = [i for i, p in enumerate(points) if p.on_curve and p.y == 0]
        if len(baseline) != 2 or (baseline[1] - baseline[0]) % count not in (
            1,
            count - 1,
        ):
            raise ValueError("Expected 7 to stand on a leg cut flat")
        left, right = sorted(baseline, key=lambda i: upright(i)[0])
        top = (left - (1 if (left + 1) % count == right else -1)) % count
        if not points[top].on_curve:
            raise ValueError("Expected the leg of 7 to have straight edges")
        return Line(upright(left), upright(top)).distance(upright(right))

    def _redraw(self, glyph, style, thickness, level, turned):
        """Replace the curved stroke with a straight one cut flat at `level`.

        Upstream, the outer contour runs from the stroke's end down its
        outer edge, onto a straight side of the bowl, around the bowl, and
        over the bowl's top into a corner, where the stroke's inner edge
        leaves it. The new stroke's inner edge is tangent to the counter at
        ANGLE, and its outer edge is `thickness` further out. The bowl's
        side, from halfway down its lower curve, is redrawn as two curves:
        one to a point on upstream's straight side, tangent to it, and one
        from there into the stroke's outer edge. The inner edge stops where
        it meets the top of the bowl.

        Built for 6 in upright coordinates. 9 is built turned half a turn,
        so its tail is 6's stroke and its baseline is 6's figure height.
        """
        name = glyph.glyphname
        layer = glyph.foreground
        if glyph.references or len(layer) != 2:
            raise ValueError(
                f"Expected {name} to be a bowl with a stroke, and a counter"
            )
        outer_index = max(range(2), key=lambda i: _width(layer[i]))
        original, counter = layer[outer_index], layer[1 - outer_index]
        if counter.isClockwise() == original.isClockwise():
            raise ValueError(f"Expected the counter of {name} inside its outline")
        sign = -1 if turned else 1

        def framed(point):
            return (
                sign * style.upright(point.x, point.y),
                sign * point.y,
                point.on_curve,
            )

        def unframed(point):
            return rounded(style.slanted(sign * point[0], sign * point[1]))

        smoothed = self._smooth(counter, framed, unframed, name)
        hole = [framed(point) for point in smoothed]
        left, bottom, right, top = bounds(hole)
        level *= sign

        angle = math.radians(self.ANGLE)
        direction = (math.cos(angle), math.sin(angle))
        normal = (-direction[1], direction[0])  # up and to the left
        reach = extent(hole, normal)

        def line(distance):
            base = (normal[0] * distance, normal[1] * distance)
            return Line(base, (base[0] + direction[0], base[1] + direction[1]))

        def beyond(point):
            return normal[0] * point[0] + normal[1] * point[1] - reach

        inner, outer = line(reach), line(reach + thickness)

        points = list(original)
        count = len(points)
        frame = [framed(point) for point in points]

        def xy(index):
            return frame[index % count][:2]

        sides = [
            i
            for i in range(count)
            if frame[i][2]
            and frame[(i + 1) % count][2]
            and all(left > x and bottom < y < top for x, y in (xy(i), xy(i + 1)))
            and abs(xy(i + 1)[0] - xy(i)[0])
            < abs(xy(i + 1)[1] - xy(i)[1]) * math.tan(math.radians(self.SIDE))
        ]
        if len(sides) != 1:
            raise ValueError(f"Expected the bowl of {name} to have one straight side")
        foot, head = sorted((sides[0], (sides[0] + 1) % count), key=lambda i: xy(i)[1])
        # `step` walks from the straight side down around the bowl, over its
        # top, and up the stroke's inner edge.
        step = 1 if (foot - head) % count == 1 else -1
        side = Line(xy(head), xy(foot))
        base = next(
            (
                index
                for index in ((foot + k * step) % count for k in range(1, count))
                if frame[index][2]
                and turn(
                    xy(head), xy(foot), _shifted(xy(foot), xy(index - step), xy(index))
                )
                >= self.BASE
            ),
            None,
        )
        if base is None:
            raise ValueError(f"Expected the bowl of {name} to curve below its side")
        low = side.intersection(Line(xy(base - step), xy(base)))
        high = side.intersection(outer)
        middle = lerp(low, high, 0.5)
        join = (
            high[0] + math.dist(middle, high) * direction[0],
            high[1] + math.dist(middle, high) * direction[1],
        )
        if not (
            xy(base)[1] < low[1] < high[1] < join[1] < level
            and _dot(xy(base - step), xy(base), low, xy(base)) > 0
        ):
            raise ValueError(f"Expected the stroke of {name} to leave the bowl's side")

        order = [(base + k * step) % count for k in range(count)]
        path = [frame[i] for i in order]
        crossing = next(
            (
                segment
                for segment in segments(path)
                if beyond(path[segment[0]]) < 0 <= beyond(path[segment[2]])
            ),
            None,
        )
        if crossing is None:
            raise ValueError(f"Expected the stroke of {name} to cross the bowl's top")
        start, control, end = crossing
        p0, p2 = path[start][:2], path[end][:2]
        if control is None:
            t = beyond(p0) / (beyond(p0) - beyond(p2))
            crotch, handle = lerp(p0, p2, t), None
        else:
            p1 = path[control][:2]
            t = 1.0 if beyond(p2) == 0 else inner.crossing(p0, p1, p2)
            crotch, handle = quadratic(p0, p1, p2, t), lerp(p0, p1, t)
        if not (left < crotch[0] < right and (bottom + top) / 2 < crotch[1] < level):
            raise ValueError(f"Expected the stroke of {name} to leave the bowl's top")

        kept = [points[i] for i in order[: start + 1]]
        for k in {0, start}:
            # Next to a new handle, an implied point is implied no longer;
            # round it as TrueType will.
            kept[k] = fontforge.point(round(kept[k].x), round(kept[k].y), True)
        high, low = unframed(high), unframed(low)
        outline = [
            *kept,
            *([] if handle is None else [fontforge.point(*unframed(handle), False)]),
            unframed(crotch),
            unframed((inner.x_at(level), level)),
            unframed((outer.x_at(level), level)),
            unframed(join),
            fontforge.point(*high, False),
            # Midway between the handles, so TrueType leaves it implied.
            fontforge.point((high[0] + low[0]) / 2, (high[1] + low[1]) / 2, True),
            fontforge.point(*low, False),
        ]
        if step < 0:
            outline.reverse()
        contours = [contour(outline, like=original), contour(smoothed, like=counter)]
        replace_contours(glyph, contours if outer_index == 0 else contours[::-1])

    def _smooth(self, counter, framed, unframed, name):
        """The counter's points, with its one corner rounded off.

        Upstream, the counter turns a corner where the curved stroke pulls
        away from it: a straight side leads into a curve 7 to 27 degrees
        off. Next to a straight stroke, the corner reads as a dent. From the
        far end of the straight side to the next on-curve point that
        TrueType stores, it is replaced by one curve tangent to both.
        """
        points = list(counter)
        count = len(points)
        frame = [framed(point) for point in points]

        def xy(index):
            return frame[index % count][:2]

        corners = [
            i
            for i in range(count)
            if points[i].on_curve and turn(xy(i - 1), xy(i), xy(i + 1)) > self.CORNER
        ]
        if len(corners) != 1:
            raise ValueError(f"Expected the counter of {name} to turn one corner")
        corner = corners[0]
        before, after = points[corner - 1], points[(corner + 1) % count]
        if before.on_curve == after.on_curve:
            raise ValueError(
                f"Expected the counter of {name} to turn from a straight side"
            )
        # `step` walks from the straight side through the corner.
        step = 1 if before.on_curve else -1
        start = (corner - step) % count
        flags = implied(points)
        end = (corner + step) % count
        while not points[end].on_curve or flags[end]:
            end = (end + step) % count
        handle = Line(xy(start), xy(corner)).intersection(Line(xy(end), xy(end + step)))
        if (
            _dot(xy(start), xy(corner), xy(start), handle) <= 0
            or _dot(handle, xy(end), xy(end), xy(end + step)) <= 0
        ):
            raise ValueError(f"Expected the counter of {name} to curve past its corner")

        outline = []
        index = end
        while index != start:
            outline.append(points[index])
            index = (index + step) % count
        outline += [points[start], fontforge.point(*unframed(handle), False)]
        if step < 0:
            outline.reverse()
        return outline


def _dot(a, b, c, d):
    """Dot product of the vectors from a to b and from c to d."""
    return (b[0] - a[0]) * (d[0] - c[0]) + (b[1] - a[1]) * (d[1] - c[1])


def _shifted(origin, a, b):
    """The point that is to `origin` as b is to a."""
    return origin[0] + b[0] - a[0], origin[1] + b[1] - a[1]


def _width(outline):
    x_min, _, x_max, _ = outline.boundingBox()
    return x_max - x_min
