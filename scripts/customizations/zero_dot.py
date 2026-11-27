"""0: a dot in the middle of the counter, instead of Roboto's slash."""

import math

import fontforge

from .base import Customization
from .geometry import Line, ahead, bounds, rounded
from .outline import contour, replace_contours


class DottedZero(Customization):
    name = "dotted-zero"
    summary = (
        "0: round dot in the middle of the counter instead of the slash, "
        "as in JetBrains Mono, IBM Plex Mono, and Source Code Pro"
    )
    redraws = ("zero",)

    # The dot is the period at 0.85 of its width. In Regular, it is then 0.44
    # as wide as the counter: IBM Plex Mono's is 0.39, Source Code Pro's
    # 0.41, JetBrains Mono's 0.45, and Fira Mono's 0.48. Roboto's period
    # grows faster with weight than the counter of 0 can take, so the dot is
    # at most 0.6 as wide as the counter: JetBrains Mono's Bold dot is 0.58
    # as wide as its counter, IBM Plex Mono's 0.52, and Source Code Pro's
    # 0.66. Medium and Bold reach that limit.
    SCALE = 0.85
    MAX_WIDTH = 0.6
    # Joining the halves may round the counter out past upstream's by this
    # many units at most.
    BULGE = 1
    # Degrees. In Bold, upstream's halves meet the gap along the counter's
    # straight sides, at most 1.4 degrees off.
    STRAIGHT = 2

    def redraw(self, font, style):
        """Close the counter where the slash cut it, and put a dot in it.

        Upstream, the slash cuts the counter in two, each half with a straight
        edge along the slash. Without those edges, the halves are joined on
        each side by a curve tangent to upstream's at both ends. The dot is
        the style's own period, scaled and centered in the counter.
        """
        glyph = font["zero"]
        layer = glyph.foreground
        if glyph.references or len(layer) != 3:
            raise ValueError("Expected 0 to be an outline and a counter cut in two")
        outer = max(range(3), key=lambda i: _width(layer[i]))
        halves = [layer[i] for i in range(3) if i != outer]
        if any(half.isClockwise() == layer[outer].isClockwise() for half in halves):
            raise ValueError("Expected the counter of 0 inside its outline")
        paths = [self._open(half, style) for half in halves]
        upstream = [bounds(path) for path in paths]
        (tail0, head1, handle01), (tail1, head0, handle10) = (
            self._join(paths[0], paths[1]),
            self._join(paths[1], paths[0]),
        )
        counter = []
        for path, head, tail, handle in (
            (paths[0], head0, tail0, handle01),
            (paths[1], head1, tail1, handle10),
        ):
            counter += _trim(path, head, tail)
            if handle is not None:
                counter.append((*handle, False, None))
        left, bottom, right, top = bounds(counter)
        if (
            left < min(b[0] for b in upstream) - self.BULGE
            or right > max(b[2] for b in upstream) + self.BULGE
        ):
            raise ValueError("Joining the halves of the counter of 0 widened it")

        dot = self._dot(
            font["period"],
            style.slanted((left + right) / 2, (bottom + top) / 2),
            right - left,
        )
        points = []
        for index, (x, y, on_curve, source) in enumerate(counter):
            if source is None:
                points.append(fontforge.point(*rounded(style.slanted(x, y)), on_curve))
            elif None in (
                counter[index - 1][3],
                counter[(index + 1) % len(counter)][3],
            ):
                # Next to a new handle, an implied point is implied no longer;
                # round it as TrueType will.
                points.append(fontforge.point(round(source.x), round(source.y), True))
            else:
                points.append(source)
        replace_contours(
            glyph,
            [
                layer[outer],
                contour(points, like=halves[0]),
                contour(dot, like=layer[outer]),
            ],
        )

    @staticmethod
    def _open(half, style):
        """A half of the counter, from one end of its slash edge to the other.

        Returns (x, y, on_curve, point) tuples in upright coordinates, with
        upstream's point.
        """
        points = list(half)
        count = len(points)
        upright = [(style.upright(p.x, p.y), p.y) for p in points]
        xs, ys = [p[0] for p in upright], [p[1] for p in upright]
        width, height = max(xs) - min(xs), max(ys) - min(ys)
        slashes = [
            i
            for i in range(count)
            if points[i].on_curve
            and points[(i + 1) % count].on_curve
            and abs(upright[(i + 1) % count][0] - upright[i][0]) > width / 4
            and abs(upright[(i + 1) % count][1] - upright[i][1]) > height / 4
        ]
        if len(slashes) != 1:
            raise ValueError(
                "Expected each half of the counter of 0 to end at the slash"
            )
        start = (slashes[0] + 1) % count
        return [
            (*upright[i], points[i].on_curve, points[i])
            for i in ((start + k) % count for k in range(count))
        ]

    def _join(self, path, following):
        """How to join the end of `path` to the start of `following`.

        The join is one quadratic, tangent to both halves, or a straight line
        where both ends already lie on a straight side of the counter, as in
        Bold. Where the ends do not lie on one convex curve, as in Light,
        Light Italic, and Thin Italic, one half, whichever leaves the shorter
        gap, is cut back by a segment first. Light, interpolated between
        masters that the slash cuts in different places, narrows the counter
        by up to 9 units next to the slash. Returns the segments dropped from
        the end of `path` and from the start of `following`, and the handle
        in upright coordinates, or None for a straight line.
        """
        if math.dist(path[-1][:2], following[0][:2]) > (
            math.dist(path[0][:2], path[-1][:2]) / 2
        ):
            raise ValueError(
                "Expected the slash of 0 to cut a narrow gap in the counter"
            )
        fits = []
        for tail, head in ((0, 0), (1, 0), (0, 1)):
            a, b = _trim(path, 0, tail), _trim(following, head, 0)
            before, end = a[-2][:2], a[-1][:2]
            start, after = b[0][:2], b[1][:2]
            if not (tail or head) and (
                max(_angle(before, end, start), _angle(end, start, after))
                < self.STRAIGHT
            ):
                return 0, 0, None
            try:
                handle = Line(before, end).intersection(Line(start, after))
            except ValueError:
                continue
            if ahead(before, end, handle) and ahead(handle, start, after):
                if not (tail or head):
                    return 0, 0, handle
                fits.append((math.dist(end, start), tail, head, handle))
        if not fits:
            raise ValueError(
                "Expected the counter of 0 to curve smoothly across the slash"
            )
        _, tail, head, handle = min(fits)
        return tail, head, handle

    def _dot(self, period, center, counter):
        """The period's outline, scaled down to fit a counter `counter` wide
        and centered on `center`.

        Points that TrueType leaves implied, midway between two handles, stay
        midway between the rounded handles.
        """
        if period.references or len(period.foreground) != 1:
            raise ValueError("Expected the period to be one contour")
        points = list(period.foreground[0])
        left, bottom, right, top = bounds([(p.x, p.y, p.on_curve) for p in points])
        middle = ((left + right) / 2, (bottom + top) / 2)
        width = min(self.SCALE * (right - left), self.MAX_WIDTH * counter)
        scale = width / (right - left)
        result = [
            fontforge.point(
                round(center[0] + (point.x - middle[0]) * scale),
                round(center[1] + (point.y - middle[1]) * scale),
                point.on_curve,
            )
            for point in points
        ]
        for index, implied in enumerate(_implied(points)):
            if implied:
                before, after = result[index - 1], result[(index + 1) % len(result)]
                result[index] = fontforge.point(
                    (before.x + after.x) / 2, (before.y + after.y) / 2, True
                )
        return result


def _trim(path, head, tail):
    """An open path without its first `head` and last `tail` segments."""
    start, end = 0, len(path) - 1
    for _ in range(head):
        start += 2 if not path[start + 1][2] else 1
    for _ in range(tail):
        end -= 2 if not path[end - 1][2] else 1
    if start >= end:
        raise ValueError("Expected a half of the counter of 0 to be longer")
    return path[start : end + 1]


def _angle(a, b, c):
    """Degrees between the direction from a to b and from b to c."""
    turn = math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(b[1] - a[1], b[0] - a[0])
    return abs(math.degrees((turn + math.pi) % (2 * math.pi) - math.pi))


def _width(outline):
    x_min, _, x_max, _ = outline.boundingBox()
    return x_max - x_min


def _implied(points):
    """Flags for on-curve points midway between two handles.

    TrueType leaves such points out, and FontForge reads them back.
    """
    count = len(points)
    flags = []
    for index, point in enumerate(points):
        before, after = points[index - 1], points[(index + 1) % count]
        flags.append(
            point.on_curve
            and not before.on_curve
            and not after.on_curve
            and (point.x, point.y)
            == ((before.x + after.x) / 2, (before.y + after.y) / 2)
        )
    return flags
