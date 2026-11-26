"""y: a straight descender instead of Roboto's hooked tail."""

from .base import Customization
from .geometry import Line, rounded
from .outline import contour, replace_contours, single_contour


class StraightTailY(Customization):
    name = "straight-y"
    summary = "y: straight tail cut flat at the descender, as in JetBrains Mono and DM Mono"
    redraws = ("y",)
    inherits = (
        "yacute", "ycircumflex", "ydieresis", "ygrave",  # ý ŷ ÿ ỳ
        "uni1EF5", "uni1EF7", "uni1EF9",  # ỵ ỷ ỹ
        "uni0443", "uni045E", "uni04EF", "uni04F1", "uni04F3",  # Cyrillic у ў ӯ ӱ ӳ
    )

    TOLERANCE = 4

    def redraw(self, font, style):
        """Extend the right stroke straight down and keep both arms as drawn.

        The outline is a v whose right stroke runs from the top-right corner
        down to where the hook starts, and whose left arm's outer edge meets
        that stroke at a junction. Everything between the junction and the
        hook start is the tail. It is replaced by a stroke with the
        top's width, parallel to the right edge, cut flat at the descender.
        """
        glyph = font["y"]
        original = single_contour(glyph)
        points = list(original)
        count = len(points)
        top = max(point.y for point in points)

        def at_top(index):
            # Some italics place the right arm's corners a unit or two lower.
            return points[index].y >= top - self.TOLERANCE

        corners = sorted((i for i, point in enumerate(points) if point.on_curve and at_top(i)),
                         key=lambda i: points[i].x)
        if len(corners) != 4:
            raise ValueError("Expected y to have four corners at the x-height")
        top_left, top_right = corners[0], corners[-1]

        def neighbour(index, step):
            index = (index + step) % count
            if not points[index].on_curve:
                raise ValueError("Expected straight edges next to the top corners of y")
            return index

        # Walk from the left arm's outer corner toward its junction with the tail.
        step = 1 if not at_top(neighbour(top_left, 1)) else -1
        junction = neighbour(top_left, step)
        hook_start = neighbour(top_right, -step)
        top_inner = neighbour(top_right, step)
        if not at_top(top_inner) or points[hook_start].y >= points[junction].y:
            raise ValueError("Unexpected y structure")

        def xy(index):
            return points[index].x, points[index].y

        right_edge = Line(xy(top_right), xy(hook_start))
        width = abs(points[top_right].x - points[top_inner].x)
        tail_edge = right_edge.shifted(-width)
        joint = Line(xy(top_left), xy(junction)).intersection(tail_edge)
        if not style.descender < joint[1] < top / 2:
            raise ValueError("Tail joins the left arm at an unexpected height")
        foot = style.descender
        tail = [joint, (tail_edge.x_at(foot), foot), (right_edge.x_at(foot), foot)]

        # Keep the run from the top-right corner around to the left arm's corner.
        kept = []
        index = top_right
        while index != junction:
            kept.append(points[index])
            index = (index + step) % count
        outline = kept + [rounded(point) for point in tail]
        if step < 0:
            outline.reverse()
        replace_contours(glyph, [contour(outline, like=original)])
