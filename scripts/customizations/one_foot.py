"""1: l's foot bar under Roboto's flagged stem."""

from dataclasses import dataclass

from .base import Customization
from .geometry import Line, rounded
from .outline import contour, replace_contours, single_contour


@dataclass(frozen=True)
class _Foot:
    """l's foot bar, in upright coordinates."""

    top: float
    corners: tuple  # top left, bottom left, bottom right, top right

    @property
    def left(self):
        return min(self.corners[0][0], self.corners[1][0])

    @property
    def right(self):
        return max(self.corners[2][0], self.corners[3][0])


class FootedOne(Customization):
    name = "footed-one"
    summary = (
        "1: l's foot bar on the baseline, under Roboto's flag, "
        "as in JetBrains Mono and IBM Plex Mono"
    )
    redraws = ("one",)

    # Roboto's flag already reaches as far left as l's foot, from 5 units
    # short of it (Regular) to 28 past (Bold Italic), as JetBrains Mono's
    # reaches its own foot. The long, sloping flag keeps 1 apart from l,
    # whose flag is level.
    REACH = 40

    def redraw(self, font, style):
        """Run the stem down to the top of l's foot and add the foot.

        Upstream, 1 is one contour standing on a stem cut flat at the
        baseline. The foot is l's, at the same place in the cell, so 1 and l
        line up in a column of code.
        """
        foot = self._foot(font["l"], style)
        glyph = font["one"]
        original = single_contour(glyph)
        points = list(original)
        count = len(points)

        def upright(index):
            return style.upright(points[index].x, points[index].y), points[index].y

        baseline = [i for i, p in enumerate(points) if p.on_curve and p.y == 0]
        if len(baseline) != 2 or (baseline[1] - baseline[0]) % count not in (
            1,
            count - 1,
        ):
            raise ValueError("Expected 1 to stand on a stem cut flat")
        bottom_left, bottom_right = sorted(baseline, key=lambda i: upright(i)[0])
        # `step` walks from the stem's bottom left to its bottom right, then
        # up the stem's right edge.
        step = 1 if (bottom_left + 1) % count == bottom_right else -1
        top_left, top_right = (
            (bottom_left - step) % count,
            (bottom_right + step) % count,
        )
        if not all(points[i].on_curve for i in (top_left, top_right)):
            raise ValueError("Expected straight stem edges on 1")
        left = Line(upright(bottom_left), upright(top_left))
        right = Line(upright(bottom_right), upright(top_right))
        flag = min(style.upright(p.x, p.y) for p in points)
        if not (
            foot.left < left.x_at(foot.top)
            and right.x_at(foot.top) < foot.right
            and abs(flag - foot.left) < self.REACH
        ):
            raise ValueError("Expected the stem and flag of 1 to fit l's foot")

        corners = [
            (left.x_at(foot.top), foot.top),
            *foot.corners,
            (right.x_at(foot.top), foot.top),
        ]
        outline = []
        index = (bottom_right + step) % count
        while index != bottom_left:
            outline.append(points[index])
            index = (index + step) % count
        outline += [rounded(style.slanted(x, y)) for x, y in corners]
        if step < 0:
            outline.reverse()
        replace_contours(glyph, [contour(outline, like=original)])

    @staticmethod
    def _foot(glyph, style):
        """Measure l's foot bar: a stem with a flag and a foot, all straight."""
        outline = single_contour(glyph)
        points = [(style.upright(p.x, p.y), p.y) for p in outline if p.on_curve]
        if len(points) != len(outline):
            raise ValueError("Expected l to be drawn with straight edges")
        heights = sorted({y for _, y in points})
        if len(heights) != 4 or heights[0] != 0:
            raise ValueError("Expected l to be a stem with a flag and a foot")
        top = heights[1]
        bottom = sorted(p for p in points if p[1] == 0)
        upper = sorted(p for p in points if p[1] == top)
        if len(bottom) != 2 or len(upper) != 4:
            raise ValueError("Expected l to be a stem with a flag and a foot")
        return _Foot(top=top, corners=(upper[0], bottom[0], bottom[1], upper[-1]))
