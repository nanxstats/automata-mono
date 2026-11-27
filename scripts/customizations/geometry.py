"""Plane geometry on (x, y) tuples, independent of FontForge."""

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Line:
    """The infinite line through points a and b."""

    a: tuple
    b: tuple

    def x_at(self, y):
        (x1, y1), (x2, y2) = self.a, self.b
        if y1 == y2:
            raise ValueError("Horizontal line has no unique x at a given y")
        return x1 + (y - y1) * (x2 - x1) / (y2 - y1)

    def shifted(self, dx):
        """The parallel line moved horizontally by dx."""
        return Line((self.a[0] + dx, self.a[1]), (self.b[0] + dx, self.b[1]))

    def offset(self, point):
        """Horizontal distance from the line to a point, positive to the right."""
        return point[0] - self.x_at(point[1])

    def distance(self, point):
        """Perpendicular distance from the line to a point."""
        (x1, y1), (x2, y2) = self.a, self.b
        cross = (x2 - x1) * (point[1] - y1) - (y2 - y1) * (point[0] - x1)
        return abs(cross) / math.dist(self.a, self.b)

    def crossing(self, p0, p1, p2):
        """Parameter t where the quadratic curve p0, p1, p2 crosses the line.

        The curve's ends must lie on opposite sides of the line.
        """
        side = self.offset(p0)
        if side * self.offset(p2) >= 0:
            raise ValueError("Curve does not cross the line")
        low, high = 0.0, 1.0
        for _ in range(50):
            middle = (low + high) / 2
            if self.offset(quadratic(p0, p1, p2, middle)) * side > 0:
                low = middle
            else:
                high = middle
        return (low + high) / 2

    def intersection(self, other):
        (x1, y1), (x2, y2) = self.a, self.b
        (x3, y3), (x4, y4) = other.a, other.b
        denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(denominator) < 1e-9:
            raise ValueError("Parallel lines do not intersect")
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
        return x1 + t * (x2 - x1), y1 + t * (y2 - y1)


def lerp(a, b, t):
    return tuple(u + (v - u) * t for u, v in zip(a, b, strict=True))


def quadratic(p0, p1, p2, t):
    """The point at t on the quadratic Bézier curve p0, p1, p2."""
    return lerp(lerp(p0, p1, t), lerp(p1, p2, t), t)


def rounded(point):
    return round(point[0]), round(point[1])


def turn(a, b, c):
    """Degrees between the direction from a to b and from b to c."""
    angle = math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(b[1] - a[1], b[0] - a[0])
    return abs(math.degrees((angle + math.pi) % (2 * math.pi) - math.pi))


def ahead(a, b, c):
    """Whether c lies ahead of b on the way from a to b."""
    return (b[0] - a[0]) * (c[0] - b[0]) + (b[1] - a[1]) * (c[1] - b[1]) > 0


def segments(points):
    """Split a closed quadratic outline into (start, control, end) indices.

    `points` are (x, y, on_curve) tuples with at most one off-curve point
    between on-curve ones, as FontForge reads TrueType outlines. `control`
    is None for straight segments. The first segment starts at the first
    on-curve point.
    """
    count = len(points)
    first = next(i for i, point in enumerate(points) if point[2])
    result = []
    start = first
    while True:
        end, control = (start + 1) % count, None
        if not points[end][2]:
            control, end = end, (end + 1) % count
            if not points[end][2]:
                raise ValueError("Expected an on-curve point between handles")
        result.append((start, control, end))
        start = end
        if start == first:
            return result


def extent(points, direction):
    """How far a closed quadratic outline (see `segments`) reaches along a
    unit vector: the largest dot product of `direction` with its points.
    """

    def along(index):
        return direction[0] * points[index][0] + direction[1] * points[index][1]

    best = -math.inf
    for start, control, end in segments(points):
        a0, a2 = along(start), along(end)
        best = max(best, a0, a2)
        if control is not None:
            a1 = along(control)
            denominator = a0 - 2 * a1 + a2
            if denominator and 0 < (a0 - a1) / denominator < 1:
                t = (a0 - a1) / denominator
                best = max(best, (1 - t) ** 2 * a0 + 2 * t * (1 - t) * a1 + t**2 * a2)
    return best


def bounds(points):
    """Exact bounding box of a closed quadratic outline (see `segments`)."""
    extremes = []
    for start, control, end in segments(points):
        p0, p2 = points[start][:2], points[end][:2]
        extremes.append(p0)
        if control is not None:
            p1 = points[control][:2]
            for axis in (0, 1):
                denominator = p0[axis] - 2 * p1[axis] + p2[axis]
                if denominator and 0 < (p0[axis] - p1[axis]) / denominator < 1:
                    t = (p0[axis] - p1[axis]) / denominator
                    extremes.append(quadratic(p0, p1, p2, t))
    xs, ys = [p[0] for p in extremes], [p[1] for p in extremes]
    return min(xs), min(ys), max(xs), max(ys)
