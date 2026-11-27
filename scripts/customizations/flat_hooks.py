"""f, g, j, and t: hooks that run flat into an upright cut."""

from dataclasses import dataclass

import fontforge

from .base import Customization
from .geometry import rounded
from .outline import contour, implied, replace_contours


@dataclass(frozen=True)
class _Edge:
    """One edge of a hook, cut where it runs level.

    `point` is the on-curve point where it runs level, and `handle` the
    handle next to it toward the stem, both (u, v) in the hook's frame.
    `kept` are the indices of the points beyond the handle, toward the stem,
    in walking order.
    """

    point: tuple
    handle: tuple
    kept: list


class FlatHooks(Customization):
    name = "flat-hooks"
    summary = (
        "f, g, j, t: hooks run flat along the ascender, baseline, or descender "
        "into an upright cut, as in JetBrains Mono"
    )
    # Glyphs that draw their own hook: the line it runs along, and whether
    # it runs right of the stem (else left).
    HOOKS = {
        "f": ("ascender", True),
        "t": ("baseline", True),
        "tbar": ("baseline", True),  # ŧ draws its own copy of the t outline
        "g": ("descender", False),
        "j": ("descender", False),
        "uni0237": ("descender", False),  # dotless j, under ĵ and ǰ
        "ij": ("descender", False),  # ĳ draws its own, narrower j
    }
    redraws = tuple(HOOKS)
    inherits = (
        "tcaron",  # ť
        "uni0163",  # ţ
        "uni021B",  # ț
        "gbreve",  # ğ
        "gcircumflex",  # ĝ
        "gcommaaccent",  # ģ
        "uni0121",  # ġ
        "uni0458",  # Cyrillic ј
        "jcircumflex",  # ĵ
        "uni01F0",  # ǰ
    )

    # Of the em. Upstream, the hooks overshoot their line by 10 to 46 units.
    MAX_OVERSHOOT = 0.03
    # Run over rise of the stem edges the hooks leave, in upright
    # coordinates. Italic stems lean about 0.01 less than the italic angle,
    # and the short edges above f's bar and below g's crotch up to 0.045.
    STEM = 0.05

    def redraw(self, font, style):
        lines = {
            "ascender": style.ascender,
            "baseline": 0,
            "descender": style.descender,
        }
        for name, (line, right) in self.HOOKS.items():
            self._flatten(font[name], style, lines[line], line == "ascender", right)

    def _flatten(self, glyph, style, line, top, right):
        """Run the hook flat along `line` into an upright cut.

        Upstream, the hook leaves the stem, curves until it runs level just
        past `line`, and curls on into a cut square to the stroke. Both
        edges are cut where they run level, and the curves up to there move
        along the stem so that the outer edge lies on `line`. From there,
        both edges run straight to an upright cut where upstream's hook
        reaches furthest. The stroke keeps its thickness where it runs level.

        Built for t, in upright coordinates: the hook hangs below the stem
        and runs right. f is built upside down, and g and j mirrored.
        """
        name = glyph.glyphname
        if glyph.references:
            raise ValueError(f"Expected {name} to be drawn without references")
        sx, sy = (1 if right else -1), (-1 if top else 1)

        def framed(point):
            return sx * style.upright(point.x, point.y), sy * point.y, point.on_curve

        def placed(u, v, on_curve):
            return fontforge.point(*rounded(style.slanted(sx * u, sy * v)), on_curve)

        layer = glyph.foreground
        frames = [[framed(point) for point in outline] for outline in layer]
        hooked = min(
            range(len(layer)),
            key=lambda i: min(point[1] for point in frames[i] if point[2]),
        )
        original, frame = layer[hooked], frames[hooked]
        points = list(original)
        count = len(points)
        level = sy * line

        def xy(index):
            return frame[index % count][:2]

        def on(index):
            return frame[index % count][2]

        def straight(index, step):
            return on(index) and on(index + step)

        def walk(index, step, stop):
            """The first index after `index`, stepping by `step`, where stop holds."""
            for _ in range(count):
                index = (index + step) % count
                if stop(index):
                    return index
            raise ValueError(f"Unexpected hook on {name}")

        def run(first, last, step):
            indices = [first % count]
            while indices[-1] != last % count:
                indices.append((indices[-1] + step) % count)
            return indices

        bottom = min((i for i in range(count) if on(i)), key=lambda i: xy(i)[1])
        # `step` walks from the bottom of the hook toward its end.
        step = 1 if xy(walk(bottom, 1, on))[0] > xy(walk(bottom, -1, on))[0] else -1
        # The hook leaves the stem at `start` and comes back to it at `stop`.
        # In between, it is cut from `end` to `corner`.
        start = walk(bottom, -step, lambda i: straight(i, -step))
        end = walk(bottom - step, step, lambda i: straight(i, step))
        corner = (end + step) % count
        stop = walk(corner, step, lambda i: straight(i, step))
        for junction, direction in ((start, -step), (stop, step)):
            (u0, v0), (u1, v1) = xy(junction), xy(junction + direction)
            if not (v1 > v0 and abs(u1 - u0) <= self.STEM * (v1 - v0)):
                raise ValueError(f"Expected the hook of {name} to leave a stem")

        outer = _cut(frame, run(start, end, step), toward_stem=False, name=name)
        inner = _cut(frame, run(corner, stop, step), toward_stem=True, name=name)
        overshoot = level - outer.point[1]
        thickness = round(inner.point[1] - outer.point[1])
        reach = max(xy(end)[0], xy(corner)[0])
        if not (
            0 <= overshoot <= self.MAX_OVERSHOOT * style.em
            and xy(start)[1] + overshoot < xy(start - step)[1]
            and xy(stop)[1] + overshoot < xy(stop + step)[1]
            and thickness > 0
            and max(outer.point[0], inner.point[0]) < reach
        ):
            raise ValueError(f"Expected the hook of {name} to run level past {line}")

        # Move along the italic angle so the stem edges stay straight.
        dy = round(sy * overshoot)
        dx = round(dy * style.slant)
        flags = implied(points)

        def moved(index, smooth=True):
            point = points[index]
            x, y = point.x + dx, point.y + dy
            if flags[index] and not smooth:
                # Next to a new handle, an implied point is implied no
                # longer; round it as TrueType will.
                x, y = round(x), round(y)
            return fontforge.point(x, y, point.on_curve)

        inner_level = level + thickness
        outline = [points[i] for i in run(stop + step, start - step, step)]
        outline += [moved(i) for i in outer.kept[:-1]]
        outline += [
            moved(outer.kept[-1], smooth=False),
            placed(outer.handle[0], level, False),
            placed(outer.point[0], level, True),
            placed(reach, level, True),
            placed(reach, inner_level, True),
            placed(inner.point[0], inner_level, True),
            placed(inner.handle[0], inner_level, False),
            moved(inner.kept[0], smooth=False),
        ]
        outline += [moved(i) for i in inner.kept[1:]]
        if step < 0:
            outline.reverse()
        replace_contours(
            glyph,
            [
                contour(outline, like=original) if i == hooked else layer[i]
                for i in range(len(layer))
            ],
        )


# Units. Upstream, each edge's lowest on-curve point lies within half a unit
# of the curve's lowest, and its handle toward the stem is level with it
# within 3 units; the italics are not drawn with points at the extremes.
LEVEL = 4


def _cut(frame, run, toward_stem, name):
    """Cut an edge at its lowest on-curve point, where it must run level.

    `run` lists the indices in `frame` of the edge's points, from one
    on-curve point to another. If `toward_stem`, the run ends at the stem,
    else it starts there.
    """
    position = min(
        (k for k, index in enumerate(run) if frame[index][2]),
        key=lambda k: frame[run[k]][1],
    )
    handle = position + 1 if toward_stem else position - 1
    if not (
        0 < handle < len(run) - 1
        and not frame[run[handle]][2]
        and abs(frame[run[handle]][1] - frame[run[position]][1]) <= LEVEL
    ):
        raise ValueError(f"Expected the hook of {name} to curve until it runs level")
    kept = run[handle + 1 :] if toward_stem else run[:handle]
    return _Edge(frame[run[position]][:2], frame[run[handle]][:2], kept)
