"""FontForge outline helpers shared by the glyph customizations."""

import fontforge


def flat_outline(font, name, cache=None):
    """Contours of a glyph with references resolved, as hashable tuples.

    Contours are sorted so that decomposing a reference compares equal.
    """
    if cache is not None and name in cache:
        return cache[name]
    glyph = font[name]
    contours = [
        tuple((round(p.x, 3), round(p.y, 3), bool(p.on_curve)) for p in contour)
        for contour in glyph.foreground
    ]
    for ref_name, (xx, xy, yx, yy, dx, dy), *_ in glyph.references:
        for contour in flat_outline(font, ref_name, cache):
            contours.append(
                tuple(
                    (round(xx * x + yx * y + dx, 3), round(xy * x + yy * y + dy, 3), on)
                    for x, y, on in contour
                )
            )
    result = tuple(sorted(contours))
    if cache is not None:
        cache[name] = result
    return result


def snapshot(font):
    """Flattened outline and advance of every glyph, for before/after comparison."""
    cache = {}
    return {
        glyph.glyphname: (flat_outline(font, glyph.glyphname, cache), glyph.width)
        for glyph in font.glyphs()
    }


def referencing(font, names):
    """Glyphs that reference any of `names` directly."""
    names = set(names)
    return {
        glyph.glyphname
        for glyph in font.glyphs()
        if any(ref[0] in names for ref in glyph.references)
    }


def contour(points, like):
    """A closed contour through `points`, matching the order and direction of `like`.

    Points may be fontforge.point objects or (x, y) tuples (on-curve).
    """
    result = fontforge.contour()
    result.is_quadratic = like.is_quadratic
    for point in points:
        if not isinstance(point, fontforge.point):
            point = fontforge.point(point[0], point[1], True)
        result += point
    result.closed = True
    if result.isClockwise() != like.isClockwise():
        raise ValueError("Rebuilt contour reverses the original direction")
    return result


def implied(points):
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


def mapped(points, function):
    """fontforge points moved by `function`, (x, y) to (x, y), and rounded.

    Points that TrueType leaves implied, midway between two handles, stay
    midway between the rounded handles.
    """
    result = [
        fontforge.point(*(round(value) for value in function(p.x, p.y)), p.on_curve)
        for p in points
    ]
    for index, flag in enumerate(implied(points)):
        if flag:
            before, after = result[index - 1], result[(index + 1) % len(result)]
            result[index] = fontforge.point(
                (before.x + after.x) / 2, (before.y + after.y) / 2, True
            )
    return result


def single_contour(glyph):
    if glyph.references or len(glyph.foreground) != 1:
        raise ValueError(
            f"Expected {glyph.glyphname} to be one contour without references"
        )
    return glyph.foreground[0]


def replace_contours(glyph, contours):
    layer = fontforge.layer()
    layer.is_quadratic = glyph.foreground.is_quadratic
    for item in contours:
        layer += item
    glyph.foreground = layer
