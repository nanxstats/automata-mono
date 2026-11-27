"""G: a stem cut flat at the baseline, with a spur where the bowl joins it."""

import fontforge

from .base import Customization
from .geometry import Line, rounded
from .outline import contour, replace_contours, single_contour


class SpurG(Customization):
    name = "spur-g"
    summary = (
        "G: stem runs straight down to a flat foot on the baseline, and the bowl "
        "joins it as d's does, as in IBM Plex Mono, DM Mono, and Geist Mono"
    )
    redraws = ("G", "G.smcp")
    inherits = (
        "Gbreve",  # Ğ
        "Gcircumflex",  # Ĝ
        "Gcommaaccent",  # Ģ
        "uni0120",  # Ġ
        "Gbreve.smcp",
        "Gcircumflex.smcp",
        "Gcommaaccent.smcp",
    )

    # Upstream, as in Source Code Pro, the bowl sweeps out to the stem's
    # outer edge and the stem stops above the baseline, so G has no spur.
    # IBM Plex Mono, DM Mono, and Geist Mono run the stem down to the
    # baseline and join the bowl to it as in their d, scaled up: G's crotch
    # sits 0.13 to 0.30 of the cap height up, 0.8 to 1.1 times the fraction
    # of the x-height at which d's sits. G takes Roboto's own d join the
    # same way, with heights scaled by the cap height over the x-height. Its
    # crotch sits 0.105 of the cap height up in Regular through Bold, 0.128
    # in Light, and 0.150 in Thin, as d's does of the x-height.

    def redraw(self, font, style):
        outer, counter = self._join(font["d"], style)
        heights = {"G": style.cap_height, "G.smcp": font["H.smcp"].boundingBox()[3]}
        for name in self.redraws:
            ratio = heights[name] / style.x_height
            self._spur(font[name], style, outer, counter, ratio)

    @staticmethod
    def _join(glyph, style):
        """Where d's bowl meets its stem, in upright coordinates.

        Returns the outer edge from the bottom of the bowl up to the crotch,
        and the counter from its bottom up to where it meets the stem.
        """
        layer = glyph.foreground
        standing = [
            i
            for i in range(len(layer))
            if any(p.on_curve and p.y == 0 for p in layer[i])
        ]
        if glyph.references or len(layer) != 2 or len(standing) != 1:
            raise ValueError("Expected d to be an outline and a counter")
        points = _points(layer[standing[0]], style)
        count = len(points)
        feet = sorted(
            (i for i, p in enumerate(points) if p[2] and p[1] == 0),
            key=lambda i: points[i][0],
        )
        if len(feet) != 2 or (feet[1] - feet[0]) % count not in (1, count - 1):
            raise ValueError("Expected d to stand on a stem cut flat")
        left, right = feet
        # `step` walks up the stem's inner edge from the foot into the bowl.
        step = -1 if (left + 1) % count == right else 1
        crotch = (left + step) % count
        if not points[crotch][2] or not 0 < points[crotch][1] < style.x_height / 3:
            raise ValueError("Expected the bowl of d to meet its stem above the foot")
        bottom = _lowest(points, crotch, step)
        if points[bottom][1] >= 0:
            raise ValueError("Expected the bowl of d to overshoot the baseline")
        outer = _run(points, bottom, crotch, -step)

        # The counter runs straight down the stem's inner edge, then curves
        # away from it into the bowl.
        points = _points(layer[1 - standing[0]], style)
        count = len(points)
        edges = [
            (i, (i + 1) % count)
            for i in range(count)
            if points[i][2] and points[(i + 1) % count][2]
        ]
        if not edges:
            raise ValueError("Expected a straight edge on the counter of d")
        edge = max(edges, key=lambda e: abs(points[e[0]][1] - points[e[1]][1]))
        join, top = sorted(edge, key=lambda i: points[i][1])
        step = 1 if (top + 1) % count == join else -1
        bottom = _lowest(points, join, step)
        if not (
            outer[-1][1] < points[join][1] < style.x_height / 2
            and 0 < points[bottom][1] < points[join][1]
        ):
            raise ValueError(
                "Expected the counter of d to meet its stem above the crotch"
            )
        return outer, _run(points, bottom, join, -step)

    def _spur(self, glyph, style, outer_join, counter_join, ratio):
        """Run the stem down to the baseline and join the bowl to it as d's.

        Upstream, G is one contour: the stem's outer edge, the bar, and the
        stem's inner edge are six corners in a row, and the bowl's outer edge
        and counter both curve into the bottom of the stem. Both stem edges
        now run straight to the baseline. The bowl's outer edge from its
        bottom to the stem, and the counter from its bottom to the stem, are
        replaced by d's, stretched vertically by `ratio` and horizontally to
        fit between the bottom of the bowl and the stem's inner edge.
        """
        original = single_contour(glyph)
        name = glyph.glyphname
        points = _points(original, style)
        count = len(points)
        starts = [
            i
            for i in range(count)
            if all(points[(i + k) % count][2] for k in range(6))
            and not points[(i - 1) % count][2]
            and not points[(i + 6) % count][2]
        ]
        if len(starts) != 1:
            raise ValueError(f"Expected {name} to have one run of stem and bar corners")
        run = [(starts[0] + k) % count for k in range(6)]
        # `step` walks up the stem's outer edge, across the bar, and down the
        # stem's inner edge into the counter.
        step = 1
        if points[run[1]][1] < points[run[3]][1]:
            run.reverse()
            step = -1
        foot, top_right, top_left, bottom_left, bottom_right, stem_bottom = run

        def xy(index):
            return points[index][:2]

        bar, under = points[top_right][1], points[bottom_right][1]
        if not (
            points[top_left][1] == bar > points[bottom_left][1] == under
            and points[top_left][0] < points[bottom_right][0] < points[top_right][0]
            and points[foot][1] < under
            and points[stem_bottom][1] < under
        ):
            raise ValueError(f"Expected {name} to have a bar on top of its stem")
        outer = Line(xy(foot), xy(top_right))
        inner = Line(xy(bottom_right), xy(stem_bottom))
        bowl = _lowest(points, foot, -step)
        counter = _lowest(points, stem_bottom, step)
        if not points[bowl][1] < 0 < points[counter][1]:
            raise ValueError(f"Expected the bowl of {name} to curve into its stem")

        crotch = ratio * outer_join[-1][1]
        join = ratio * counter_join[-1][1]
        if not 0 < crotch < join < under:
            raise ValueError(
                f"Expected the bowl of {name} to join its stem below the bar"
            )
        new_outer = _fit(
            outer_join,
            xy(bowl),
            xy((bowl - step) % count),
            (inner.x_at(crotch), crotch),
            style,
        )
        new_counter = _fit(
            counter_join,
            xy(counter),
            xy((counter + step) % count),
            (inner.x_at(join), join),
            style,
        )

        outline = [
            original[i] for i in (top_right, top_left, bottom_left, bottom_right)
        ]
        outline += reversed(new_counter)
        index = counter
        while index != bowl:
            outline.append(original[index])
            index = (index + step) % count
        outline.append(original[bowl])
        outline += new_outer
        outline += [
            rounded(style.slanted(inner.x_at(0), 0)),
            rounded(style.slanted(outer.x_at(0), 0)),
        ]
        if step < 0:
            outline.reverse()
        replace_contours(glyph, [contour(outline, like=original)])


def _points(outline, style):
    """(x, y, on_curve, implied) in upright coordinates.

    An implied point is an on-curve point midway between two off-curve
    points, which TrueType leaves out.
    """
    points = list(outline)
    count = len(points)
    result = []
    for index, point in enumerate(points):
        before, after = points[index - 1], points[(index + 1) % count]
        implied = (
            point.on_curve
            and not before.on_curve
            and not after.on_curve
            and (point.x, point.y)
            == ((before.x + after.x) / 2, (before.y + after.y) / 2)
        )
        result.append(
            (style.upright(point.x, point.y), point.y, point.on_curve, implied)
        )
    return result


def _lowest(points, start, step):
    """Walking from start, the on-curve point where the outline stops falling."""
    count = len(points)
    lowest = index = start
    for _ in range(count):
        index = (index + step) % count
        if points[index][2]:
            if points[index][1] > points[lowest][1]:
                return lowest
            lowest = index
    raise ValueError("Expected the outline to rise again")


def _run(points, start, end, step):
    run = [points[start]]
    index = start
    while index != end:
        index = (index + step) % len(points)
        run.append(points[index])
    return run


def _fit(run, start, neighbour, end, style):
    """Map a run from d onto G, from start to end, as fontforge points.

    The run is stretched along each axis so its ends land on `start` and
    `end`. Its first handle is turned to line up with `neighbour`, so the
    curve stays smooth where it leaves the upstream outline at `start`.
    Returns the mapped points after the first, slanted back and rounded.
    """
    (x0, y0), (x1, y1) = run[0][:2], run[-1][:2]
    sx = (end[0] - start[0]) / (x1 - x0)
    sy = (end[1] - start[1]) / (y1 - y0)
    if sx <= 0 or sy <= 0:
        raise ValueError("Expected the join of d to fit the bowl of G")
    mapped = [
        [start[0] + (x - x0) * sx, start[1] + (y - y0) * sy, on, implied]
        for x, y, on, implied in run
    ]
    handle = mapped[1]
    if not handle[2]:
        dx, dy = start[0] - neighbour[0], start[1] - neighbour[1]
        t = ((handle[0] - start[0]) * dx + (handle[1] - start[1]) * dy) / (
            dx * dx + dy * dy
        )
        if t <= 0:
            raise ValueError("Expected the join of d to leave the bowl of G smoothly")
        handle[0], handle[1] = start[0] + t * dx, start[1] + t * dy
    result = []
    for x, y, on, _ in mapped[1:]:
        x, y = rounded(style.slanted(x, y))
        result.append(fontforge.point(x, y, on))
    for index in range(1, len(result) - 1):
        if mapped[index + 1][3]:
            before, after = result[index - 1], result[index + 1]
            result[index] = fontforge.point(
                (before.x + after.x) / 2, (before.y + after.y) / 2, True
            )
    return result
