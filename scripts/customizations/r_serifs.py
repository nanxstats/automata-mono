"""r: a flag at the x-height and a foot bar, drawn like Roboto's own i."""

from dataclasses import dataclass

import fontforge

from .base import Customization
from .geometry import Line, rounded
from .outline import contour, replace_contours, single_contour


@dataclass(frozen=True)
class _Serifs:
    """i's slab serifs, in upright coordinates."""

    top: float  # top of the stem and flag
    flag: float  # length past the stem's left edge
    flag_thickness: float
    foot_thickness: float
    center: float  # stem center at half the x-height


class SlabR(Customization):
    name = "slab-r"
    summary = ("r: flag at the x-height and foot bar on the baseline, drawn like i's, "
               "as in IBM Plex Mono, DM Mono, and Geist Mono")
    redraws = ("r",)
    inherits = ("racute", "rcaron", "rcommaaccent")  # ŕ ř ŗ

    # Roboto Mono gives i, j, and l slab serifs but leaves r bare, so r has a
    # wide gap on its left and reads close to the bare stem of a sans r. The
    # proportions below are measured from the Regular of IBM Plex Mono, DM
    # Mono, and Geist Mono, which give r a flag and a foot.
    #
    # Their r stem sits 0.107, 0.078, and 0.108 of the cell left of i's stem;
    # Roboto's sits 0.20 left of it, which leaves no room for a flag.
    STEM = 0.10
    # The flag is 0.81, 0.81, and 0.68 as long as i's. The foot starts below
    # the end of the flag.
    FLAG = 0.75
    # The foot reaches 1.32, 1.23, and 1.22 times as far right of the stem as
    # left of it, under the arm.
    FOOT = 1.25
    # Upstream, r's arm stops 0.047 of the cell short of f's hook. In
    # JetBrains Mono, the two end together; in IBM Plex Mono, DM Mono, and
    # Geist Mono, r's arm reaches 0.01 to 0.07 of the cell further. The arm
    # now reaches as far as f's hook. With the stem moved right, that
    # narrows the shoulder to 0.85 to 0.89 of its width. Much narrower would
    # cramp it and shorten the arm.
    MIN_SHOULDER = 0.8

    def redraw(self, font, style):
        serifs = self._serifs(font["i"], style)
        hook = self._reach(font["f"], style)
        shift = self._redraw_r(font["r"], style, serifs, hook, font["space"].width)
        for name in self.inherits:
            # The accents keep their place relative to the stem. Upstream's
            # sit where IBM Plex Mono, DM Mono, and Geist Mono put theirs.
            glyph = font[name]
            if sorted(ref[0] == "r" for ref in glyph.references) != [False, True] or glyph.foreground:
                raise ValueError("Expected %s to be r with one accent" % name)
            references = []
            for ref_name, (xx, xy, yx, yy, dx, dy), *_ in glyph.references:
                if ref_name != "r":
                    dx += shift
                references.append((ref_name, (xx, xy, yx, yy, dx, dy)))
            glyph.references = tuple(references)

    @staticmethod
    def _reach(glyph, style):
        """How far right a glyph reaches, in upright coordinates."""
        if glyph.references:
            raise ValueError("Expected %s to be drawn without references" % glyph.glyphname)
        layer = glyph.foreground.dup()
        layer.transform((1, 0, -style.slant, 1, 0, 0))
        return layer.boundingBox()[2]

    @staticmethod
    def _serifs(glyph, style):
        """Measure the flag and foot of i: ten straight edges at four heights."""
        if glyph.references:
            raise ValueError("Expected i to be drawn without references")
        standing = [c for c in glyph.foreground if c.boundingBox()[1] == 0]
        if len(standing) != 1 or len(standing[0]) != 10 or not all(p.on_curve for p in standing[0]):
            raise ValueError("Expected i to be a stem with a flag and a foot")
        levels = {}
        for point in standing[0]:
            levels.setdefault(point.y, []).append(style.upright(point.x, point.y))
        heights = sorted(levels)
        if len(heights) != 4 or heights[0] != 0 or [len(levels[y]) for y in heights] != [2, 4, 2, 2]:
            raise ValueError("Expected i to be a stem with a flag and a foot")
        _, foot_top, flag_bottom, top = heights
        flag_left, stem_left_high = sorted(levels[flag_bottom])
        _, stem_left_low, stem_right_low, _ = sorted(levels[foot_top])
        stem_right_high = max(levels[top])
        left = Line((stem_left_low, foot_top), (stem_left_high, flag_bottom))
        right = Line((stem_right_low, foot_top), (stem_right_high, top))
        middle = style.x_height / 2
        return _Serifs(
            top=top,
            flag=stem_left_high - flag_left,
            flag_thickness=top - flag_bottom,
            foot_thickness=foot_top,
            center=(left.x_at(middle) + right.x_at(middle)) / 2,
        )

    def _redraw_r(self, glyph, style, serifs, hook, cell):
        """Move the stem right, give it i's serifs, and fit the shoulder.

        Upstream, r is a bare stem with a shoulder that leaves it at its
        right edge and ends in a terminal near the right of the cell. The
        stem and the points where the shoulder joins it move right. The
        shoulder is narrowed and moved so the terminal ends at `hook`.
        Returns the horizontal shift of the stem.
        """
        original = single_contour(glyph)
        points = list(original)
        count = len(points)

        def upright(index):
            return style.upright(points[index].x, points[index].y), points[index].y

        baseline = [i for i, p in enumerate(points) if p.on_curve and p.y == 0]
        if len(baseline) != 2 or (baseline[1] - baseline[0]) % count not in (1, count - 1):
            raise ValueError("Expected r to stand on a stem cut flat")
        bottom_left, bottom_right = sorted(baseline, key=lambda i: upright(i)[0])
        # `step` walks from the stem's bottom left to its bottom right, then
        # up the stem's right edge into the shoulder.
        step = 1 if (bottom_left + 1) % count == bottom_right else -1

        def at(index, steps):
            return (index + steps * step) % count

        top_left, top_right, inner = at(bottom_left, -1), at(bottom_left, -2), at(bottom_right, 1)
        if any(not points[i].on_curve or points[i].y != serifs.top for i in (top_left, top_right)):
            raise ValueError("Expected the stem of r to be cut flat at the top of i")
        if not points[inner].on_curve or not style.x_height / 3 < points[inner].y < style.x_height:
            raise ValueError("Expected the shoulder of r to leave the stem's right edge")
        # Above the shoulder, the stem's right edge runs from the stem top
        # down to where the shoulder's outer curve meets it.
        stem = [top_right]
        while points[at(stem[-1], -1)].on_curve:
            stem.append(at(stem[-1], -1))
        stem += [top_left, bottom_left, bottom_right, inner]
        left = Line(upright(top_left), upright(bottom_left))
        right = Line(upright(bottom_right), upright(inner))
        middle = style.x_height / 2
        if len(stem) < 6 or any(not left.x_at(points[i].y) <= upright(i)[0] <= right.x_at(points[i].y) + 2
                                for i in stem[1:-4]):
            raise ValueError("Expected the shoulder of r to join the stem below its top")

        shift = round(serifs.center - self.STEM * cell - (left.x_at(middle) + right.x_at(middle)) / 2)
        shoulder = [i for i in range(count) if i not in stem]
        end = self._reach(glyph, style)
        join = upright(inner)[0]
        scale = (hook - join - shift) / (end - join)
        if shift <= 0 or hook < end or not self.MIN_SHOULDER <= scale < 1:
            raise ValueError("Unexpected stem or arm position on r")

        def narrowed(index):
            x, y = upright(index)
            return style.slanted(hook - (end - x) * scale, y)

        moved = {}
        for index in shoulder:
            point = points[index]
            neighbors = points[(index - 1) % count], points[(index + 1) % count]
            # Keep on-curve points that sit midway between two off-curve
            # points implied, as upstream has them.
            if point.on_curve and not any(p.on_curve for p in neighbors) and \
                    (point.x, point.y) == ((neighbors[0].x + neighbors[1].x) / 2,
                                           (neighbors[0].y + neighbors[1].y) / 2):
                continue
            x, y = rounded(narrowed(index))
            moved[index] = fontforge.point(x, y, point.on_curve)
        for index in shoulder:
            if index not in moved:
                before, after = moved[(index - 1) % count], moved[(index + 1) % count]
                moved[index] = fontforge.point((before.x + after.x) / 2, (before.y + after.y) / 2, True)
        for index in stem:
            point = points[index]
            if index not in (top_left, bottom_left, bottom_right):
                moved[index] = fontforge.point(point.x + shift, point.y, True)

        left, right = left.shifted(shift), right.shifted(shift)
        flag_bottom = serifs.top - serifs.flag_thickness
        foot_top = serifs.foot_thickness
        end_left = left.x_at(flag_bottom) - self.FLAG * serifs.flag
        foot_right = right.x_at(foot_top) + self.FOOT * (left.x_at(foot_top) - end_left)
        corners = [
            (end_left, serifs.top), (end_left, flag_bottom), (left.x_at(flag_bottom), flag_bottom),
            (left.x_at(foot_top), foot_top), (end_left, foot_top), (end_left, 0),
            (foot_right, 0), (foot_right, foot_top), (right.x_at(foot_top), foot_top),
        ]
        outline = [moved[inner]]
        index = at(inner, 1)
        while index != top_left:
            outline.append(moved[index])
            index = at(index, 1)
        outline += [rounded(style.slanted(x, y)) for x, y in corners]
        if step < 0:
            outline.reverse()
        replace_contours(glyph, [contour(outline, like=original)])
        return shift
