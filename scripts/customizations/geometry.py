"""Plane geometry on (x, y) tuples, independent of FontForge."""

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

    def intersection(self, other):
        (x1, y1), (x2, y2) = self.a, self.b
        (x3, y3), (x4, y4) = other.a, other.b
        denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(denominator) < 1e-9:
            raise ValueError("Parallel lines do not intersect")
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
        return x1 + t * (x2 - x1), y1 + t * (y2 - y1)


def rounded(point):
    return round(point[0]), round(point[1])
