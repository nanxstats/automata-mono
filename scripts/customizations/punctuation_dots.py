"""Period, !, ?, ¡, and ¿: larger dots. The colon and semicolon follow."""

import fontforge

from .base import Customization
from .geometry import Line, bounds, lerp, quadratic
from .outline import contour, implied, mapped, replace_contours, single_contour


class LargerDots(Customization):
    name = "larger-dots"
    summary = (
        "Period, colon, semicolon, !, ?, ¡, ¿: larger dots, as in JetBrains Mono, "
        "IBM Plex Mono, Source Code Pro, DM Mono, and Google Sans Code"
    )
    # Glyphs with a stroke over a dot, and whether the dot is on top.
    MARKS = {
        "exclam": False,
        "question": False,
        "exclamdown": True,
        "questiondown": True,
    }
    redraws = ("period", *MARKS)
    inherits = ("colon", "semicolon", "exclamdbl")  # ‼ is two !
    # Upstream spaces the periods of … and ‥ 82 to 150 units apart in
    # Regular, so larger ones would nearly touch. The fonts compared draw
    # them smaller than their periods.
    preserves = ("ellipsis", "uni2025")

    # Relative to its stems, Roboto's period is the smallest among the
    # monospaced designs compared. Period width over the stem of n in
    # Regular is 1.58, against 1.79 to 1.98 in JetBrains Mono, IBM Plex Mono,
    # Source Code Pro, DM Mono, and Google Sans Code; in Bold, 1.38 against
    # 1.36 to 1.58. Scaling by as much as the dots of i and j keeps Roboto's
    # progression across weights and the relation between the two.
    SCALE = 1.15
    # Roboto draws the dots of ! and ? 0.79 (Regular) to 0.84 (Light and
    # Bold) as wide as its period, and 0.97 in Thin. From Regular to Bold,
    # JetBrains Mono and Source Code Pro draw them 0.86 to 0.91 as wide, and
    # IBM Plex Mono, DM Mono, and Google Sans Code 0.93 to 1.00.
    MARK = 0.9

    def redraw(self, font, style):
        period = font["period"]
        dot, rise = self.period(period, style)
        replace_contours(period, [dot])
        self._follow(font, style, rise)
        box = _box(dot, style)
        width = self.MARK * (box[2] - box[0])
        for name, top in self.MARKS.items():
            self._mark(font[name], style, width, top)

    @classmethod
    def period(cls, glyph, style):
        """The larger period and how far its top rises, from upstream's.

        It grows from the middle of its bottom, so it keeps its place on the
        baseline.
        """
        original = single_contour(glyph)
        dot = _grown(original, style, cls.SCALE, top=False)
        return dot, round(_box(dot, style)[3] - _box(original, style)[3])

    @staticmethod
    def _follow(font, style, rise):
        """Keep the tops of the upper dots of : and ;, so they grow downward.

        The lower dot of : stands on the baseline and grows upward with the
        period. The upper dots move down by as much, along the italic angle.
        """
        for name, count in (("colon", 2), ("semicolon", 1)):
            glyph = font[name]
            references = glyph.references
            heights = sorted(ref[1][5] for ref in references if ref[0] == "period")
            if (
                glyph.foreground
                or len(heights) != count
                or heights[-1] <= 0
                or heights[:-1] != [0] * (count - 1)
                or any(tuple(ref[1][:4]) != (1, 0, 0, 1) for ref in references)
            ):
                raise ValueError(f"Expected {name} to be built from unscaled periods")
            moved = []
            for ref_name, (xx, xy, yx, yy, dx, dy), *_ in references:
                if ref_name == "period" and dy > 0:
                    dx, dy = dx - round(rise * style.slant), dy - rise
                moved.append((ref_name, (xx, xy, yx, yy, dx, dy)))
            glyph.references = tuple(moved)

    @staticmethod
    def _mark(glyph, style, width, top):
        """Grow the dot of ! ? ¡ ¿ to `width` and cut the stroke back.

        The dot keeps its place on the baseline (on top for ¡ and ¿) and its
        center. The stroke is cut back by as much as the dot grows, so
        upstream's gap between them is kept.
        """
        name = glyph.glyphname
        layer = glyph.foreground
        if glyph.references or len(layer) != 2:
            raise ValueError(f"Expected {name} to be a stroke and a dot")
        boxes = [_box(outline, style) for outline in layer]
        if top:
            dot = max((0, 1), key=lambda i: boxes[i][1])
            apart = boxes[dot][1] > boxes[1 - dot][3]
        else:
            dot = min((0, 1), key=lambda i: boxes[i][3])
            apart = boxes[dot][3] < boxes[1 - dot][1]
        if not apart:
            raise ValueError(f"Expected the dot of {name} apart from its stroke")
        box = boxes[dot]
        grown = _grown(layer[dot], style, width / (box[2] - box[0]), top)
        after = _box(grown, style)
        rise = round(box[1] - after[1]) if top else round(after[3] - box[3])
        stroke = _shortened(layer[1 - dot], -1 if top else 1, rise, name)
        replace_contours(glyph, [grown if i == dot else stroke for i in range(2)])


def _box(outline, style):
    """Exact bounds of a contour in upright coordinates."""
    return bounds([(style.upright(p.x, p.y), p.y, p.on_curve) for p in outline])


def _grown(outline, style, scale, top):
    """A dot scaled about the middle of its bottom edge, or its top edge."""
    left, bottom, right, upper = _box(outline, style)
    y = upper if top else bottom
    x = style.slanted((left + right) / 2, y)[0]
    points = mapped(
        list(outline), lambda px, py: (x + (px - x) * scale, y + (py - y) * scale)
    )
    return contour(points, like=outline)


# Units. Upstream's strokes end level within a unit, in italics too.
FLAT = 2
# Units. A cut closer than this below an on-curve point moves the point
# to the cut instead, rather than leave a sliver of the stroke's side.
SLIVER = 8
# Units. What is left of a cut curve becomes a line if it is this straight,
# rather than a short curve with a shorter handle.
STRAIGHT = 0.5


def _shortened(outline, sy, rise, name):
    """A stroke cut back by `rise` at its end next to the dot.

    In the frame (x, sy * y), the dot lies below the stroke, which ends in
    an edge between two on-curve points, level within FLAT. Both sides of
    the stroke are cut level, `rise` above the lower end of that edge, and
    the cut becomes the stroke's new end.
    """
    points = list(outline)
    count = len(points)
    frame = [(p.x, sy * p.y, p.on_curve) for p in points]
    low = min(v for _, v, on in frame if on)
    ends = [
        i
        for i in range(count)
        if frame[i][2]
        and frame[(i + 1) % count][2]
        and max(frame[i][1], frame[(i + 1) % count][1]) - low <= FLAT
    ]
    if len(ends) != 1:
        raise ValueError(f"Expected the stroke of {name} to end level above its dot")
    # From one corner of the end, round the stroke to the other.
    first = (ends[0] + 1) % count
    order = [(first + k) % count for k in range(count)]
    path = [(*frame[i], i) for i in order]
    level = low + rise
    start, head = _split(path, level, name)
    stop, tail = _split(path[::-1], level, name)
    stop = count - 1 - stop
    if start > stop:
        raise ValueError(f"Expected the stroke of {name} to be longer")
    kept = head + path[start : stop + 1] + tail[::-1]

    flags = implied(points)
    result = []
    for k, (x, v, on, index) in enumerate(kept):
        if index is None:
            result.append(fontforge.point(round(x), round(sy * v), on))
        elif flags[index] and None in (kept[k - 1][3], kept[(k + 1) % len(kept)][3]):
            # Next to a new handle, an implied point is implied no longer;
            # round it as TrueType will.
            point = points[index]
            result.append(fontforge.point(round(point.x), round(point.y), True))
        else:
            result.append(points[index])
    return contour(result, like=outline)


def _split(path, level, name):
    """Cut an open path where it first rises to `level`.

    `path` holds (x, v, on_curve, index) tuples and starts on-curve below
    `level`, rising steadily until it gets there. Returns the position of
    the first point kept, and the new points before it: an on-curve point
    at `level`, and the rest of the cut curve's handle unless it is straight.
    """
    start = 0
    while True:
        if start + 1 >= len(path):
            raise ValueError(f"Expected the stroke of {name} to rise past the cut")
        control = None if path[start + 1][2] else start + 1
        end = start + 1 if control is None else start + 2
        heights = [path[i][1] for i in (start, control, end) if i is not None]
        if heights != sorted(heights) or heights[0] == heights[-1]:
            raise ValueError(f"Expected the stroke of {name} to rise from its end")
        if path[end][1] > level:
            break
        start = end
    p0, p2 = path[start][:2], path[end][:2]
    if p2[1] - level < SLIVER:
        return end + 1, [(p2[0], level, True, None)]
    if control is None:
        t = (level - p0[1]) / (p2[1] - p0[1])
        return end, [(lerp(p0, p2, t)[0], level, True, None)]
    p1 = path[control][:2]
    low, high = 0.0, 1.0
    for _ in range(50):
        middle = (low + high) / 2
        if quadratic(p0, p1, p2, middle)[1] < level:
            low = middle
        else:
            high = middle
    t = (low + high) / 2
    cut = (quadratic(p0, p1, p2, t)[0], level)
    handle = lerp(p1, p2, t)
    if Line(cut, p2).distance(handle) < STRAIGHT:
        return end, [(*cut, True, None)]
    return end, [(*cut, True, None), (*handle, False, None)]
