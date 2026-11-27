# Automata Mono

A coding font based on [Roboto Mono](https://github.com/googlefonts/RobotoMono),
with [Fira Code](https://github.com/tonsky/FiraCode) programming ligatures added
by [Ligaturizer](https://github.com/ToxicFrog/Ligaturizer) and a few redrawn
glyphs. Everything else is Roboto Mono, unchanged.

## Changes from Roboto Mono

### Glyphs

| Glyph | Roboto Mono | Automata Mono |
| --- | --- | --- |
| `,` `;` | Flat head with a curved hook | Straight, slightly tapered tail in the style of [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono) |
| `i` `j` | Small dots; gap shrinks from 0.116 em (Thin) to 0.063 em (Bold) | Dots 15% larger, 0.11 em above the stem in every weight, slightly left of center |
| `y` | Hooked tail | Straight tail cut flat at the descender, as in JetBrains Mono and [DM Mono](https://github.com/googlefonts/dm-mono) |
| `t` | Stem rises 70% of the way from x-height to cap height (78% in Thin) | Stem rises 86% of the way in every weight, as in JetBrains Mono |
| `[` `]` | Arms extend 0.18 of the cell past the stem in Regular, shrinking to 0.14 in Bold | Arms extend 0.30 of the cell in every weight |
| `a` | Stem bends right into a small spur at the baseline | Stem runs straight down to a flat foot, as in JetBrains Mono, DM Mono, and [Source Code Pro](https://github.com/adobe-fonts/source-code-pro) |
| `%` | Short slash across the middle of the glyph, ends cut square to the stroke | Slash runs from the baseline to the cap height across the rings, cut flat like `/`, as in JetBrains Mono |

Details:

- **Comma.** Keeps Roboto's head (position, width, height) and depth in each
  weight, so the comma still scales with the stem and the semicolon stays
  aligned under its dot. The tail leans about 10 degrees, and the foot is 85%
  as wide as the head. These proportions are measured from JetBrains Mono.
  The semicolon uses the comma, so it changes too. The Cyrillic letters with
  a tail (Ҋ ҋ Ӆ ӆ Ӊ ӊ Ӎ ӎ) reuse the comma for their descenders and keep
  Roboto's design.
- **i and j.** Roboto keeps its dots at about the same height in every weight
  and grows them downward, so heavier weights crowd the stem. At small sizes,
  the dot blurs into the stem. Automata Mono places every dot 225 units
  (0.11 em) above the stem, between JetBrains Mono (about 0.10 em) and Fira
  Code (about 0.13 em). Heavier dots grow upward, like theirs.
  - **Size.** Roboto's dots are also small for their stems. Dot width over
    stem width in Regular is 1.20, against 1.57 to 1.67 in JetBrains Mono,
    IBM Plex Mono, DM Mono, and Source Code Pro. Dots are scaled up 15% from
    the bottom, keeping the gap. That gives 1.38 in Regular and puts Light
    and Bold in the range of those fonts. A larger scale would overshoot in
    Light and Bold. The dieresis and dot accent keep their size.
  - **Position.** JetBrains Mono, DM Mono, and Source Code Pro place their
    dots about 0.009 em left of the stem center. That offsets the top serif
    of i and the hook of j, which pull the letter's mass left. Roboto
    centers its dots within 0.004 em; Automata Mono uses 0.009 em (18 units).

  This also applies to į, ĳ, ị, and Cyrillic і ј.
- **y.** The right stroke continues straight to the descender of p and q, at
  the width it has at the x-height. The arms are unchanged. Accented and
  Cyrillic forms (ý ŷ ÿ ỳ ỵ ỷ ỹ, у ў ӯ ӱ ӳ) follow.
- **t.** A short stem makes t read close to `+` and `f` at small sizes. The
  stem top moves up to 1404 units in every weight: 60 units higher in
  Regular through Bold, and 30 in Thin. Fira Code is at about 80%. The
  reference is the cap height because Roboto's ascenders rise above it, so t
  stays shorter than the capitals. The crossbar is unchanged. ŧ, ť, ţ, and ț
  follow; the apostrophe of ť keeps its clearance.
- **Brackets.** Short arms make `[` and `]` hard to tell from `|` and `l`
  at small sizes. Roboto's arms are also shorter in heavier weights, where
  they get stubby. The arms now extend 0.30 of the cell past the stem in
  every weight: 369 units upright. That is two-thirds longer than before in
  Regular and more than twice as long in Bold. It sits between JetBrains
  Mono (about 0.26) and IBM Plex Mono and Source Code Pro (about 0.35). The
  stem, the arm thickness, and the height are unchanged. Italic arm tips
  keep their slant.
- **a.** Below its straight part, Roboto's stem bends right into a spur
  that sticks out 30 to 45 units past the stem at the baseline. Italic
  stems also turn upright there. The stem now continues straight to the
  baseline and is cut flat, so italic stems keep their slant. The bowl is
  unchanged. The foot's inner edge starts where the bowl meets the stem,
  parallel to the outer edge. Roboto's bowl joins slightly inside the stem,
  so the foot is 96% to 100% of the stem width in upright styles and 90% to
  94% in italics. ą gets the same foot, and its ogonek moves up to 10 units
  sideways so that it still hangs from the stem's outer corner. Accented and
  Cyrillic forms (à á â ã ä å ā ă ǻ ḁ ạ ả ấ ầ ẩ ẫ ậ ắ ằ ẳ ẵ ặ, а ӑ ӓ) follow.
- **Percent.** Roboto's slash covers only the middle three-quarters of the
  cap height, and its ends are cut square to the stroke. The slash now runs
  from the baseline at the left edge of the upper ring to the cap height at
  the right edge of the lower ring, with flat ends like `/`, as in
  JetBrains Mono. It leans at about 55 degrees instead of 61, also as in
  JetBrains Mono, and keeps its thickness. So it sits 5% to 35% farther
  from the rings than before. The rings are unchanged. Italics slant the
  upright design, as JetBrains Mono does. Their slash ends reach 66 to 116
  units past the cell, closer to neighboring glyphs than upstream but
  within the spacing of Roboto's own tightest italic pairs. `‰` keeps
  Roboto's design.

Italics get the same changes, slanted to Roboto Mono Italic's 10-degree angle.

### Ligatures

Each style has 126 Fira Code (v3.1) programming ligatures in the `calt`
feature. Ligatures keep the one-cell-per-character layout. These ligatures are
left out:

`&&`, `~@`, `\/`, `.?`, `?:`, `?=`, `?.`, `??`, `;;`, `/\`, `www`

`www` is excluded because Fira Code's condensed letters do not match the
height and shapes of Roboto Mono's lowercase.

This Fira Code revision has no `~=` ligature.

Each style takes its ligatures from the Fira Code weight with the closest
operator stroke weight. Roboto Mono draws its operators lighter than its
letters:

| Automata Mono | Fira Code | Hyphen thickness (Roboto / Fira, 2048 UPM) |
| --- | --- | --- |
| Thin | Light | 54 / 122 |
| Light | Light | 103 / 122 |
| Regular | Regular | 152 / 153 |
| Medium | Medium | 194 / 193 |
| Bold | SemiBold | 225 / 221 |

Fira Code has no weight close to Thin, so Thin's ligatures are noticeably
heavier than its text. Ligature outlines are Fira Code's own, with two
adjustments:

- In italic styles, they are slanted about the math axis to match Roboto's
  italic operators.
- `||` is scaled to the height of Roboto's `|`. Fira's taller bar would not
  match, and Windows would clip it at the bottom.

Ligaturizer registers `calt` under a fixed list of languages. The build moves
it to the scripts Roboto Mono uses, so small caps (`smcp`) keep working in
every language.

### Metadata

- **Names.** Fonts are named Automata Mono, following Roboto Mono's naming
  scheme. Roboto's trademark notice is dropped.
- **Monospace flag.** The fonts are marked fixed pitch; upstream leaves this
  unset.
- **Hinting.** Hinting is regenerated with ttfautohint.
- **Metrics.** Vertical metrics, line spacing, and the character set are
  unchanged.

## Styles

| Weight | Upright | Italic |
| --- | --- | --- |
| Thin (100) | `AutomataMono-Thin.ttf` | `AutomataMono-ThinItalic.ttf` |
| Light (300) | `AutomataMono-Light.ttf` | `AutomataMono-LightItalic.ttf` |
| Regular (400) | `AutomataMono-Regular.ttf` | `AutomataMono-Italic.ttf` |
| Medium (500) | `AutomataMono-Medium.ttf` | `AutomataMono-MediumItalic.ttf` |
| Bold (700) | `AutomataMono-Bold.ttf` | `AutomataMono-BoldItalic.ttf` |

Install the files from `fonts/` and select **Automata Mono**. Ligatures need
`calt`, which most editors and terminals enable along with ligatures (for
example, `"editor.fontLigatures": true` in VS Code). Turn off `calt` to show
plain operators.

## Build

The build needs Git, Make, [FontForge](https://fontforge.org/) with Python,
[ttfautohint](https://freetype.org/ttfautohint/), and
[uv](https://docs.astral.sh/uv/). On macOS:

```sh
brew install fontforge ttfautohint
make
```

- `make` builds and validates all ten styles.
- `make build` writes the fonts and license files to `fonts/`.
- `make check` validates the fonts (see [Validation](#validation)).
- `make proof` renders comparison sheets to `build/proof/`. They show the
  redrawn glyphs and ligatures in every style, plus Regular and Bold code at
  11 to 16 px with and without hinting.
- `make sources` fetches the pinned upstream sources.
- `make clean` removes `build/` and the generated fonts.

Each style goes through three steps:

1. **`scripts/build_font.py`** runs in FontForge. It applies the glyph
   customizations to the upstream TTF and adds the ligatures. It writes
   `build/AutomataMono-<Style>.fontforge.ttf` and a JSON manifest of every
   glyph it changed.
2. **`scripts/finalize.py`** runs with fontTools under uv. It removes
   FontForge artifacts and writes names. It also recomputes the side
   bearings and restores the caret slope and underline position, which
   FontForge rewrites.
3. **ttfautohint** hints the font into `fonts/AutomataMono-<Style>.ttf`.

Upstream sources are fetched at pinned commits. An existing checkout at a
different commit stops the build. To update, change the pin in the
`Makefile`, run `make clean`, and run `make` again.

| Directory | Source | Commit |
| --- | --- | --- |
| `RobotoMono/` | `googlefonts/RobotoMono` | `7bf0b33` |
| `Ligaturizer/` | `ToxicFrog/Ligaturizer` | `c406518` |
| `Ligaturizer/fonts/fira/` | Fira Code v3.1, Ligaturizer's submodule | `e9943d2` |

uv manages the Python dependencies: fontTools, uharfbuzz, freetype-py, and
Pillow. `pyproject.toml` sets a 7-day dependency cooldown
(`exclude-newer = "7 days"`). FontForge steps use FontForge's own Python and
only the standard library.

## Validation

[`scripts/validate.py`](scripts/validate.py) checks every style against the
upstream font and Fira Code. It checks:

- **Changed glyphs.** Every glyph outside the build manifest has the same
  outline and advance as Roboto Mono. Declared changes really differ, and
  preserved glyphs do not.
- **Tables and metadata.** The table set, `OS/2`, `hhea`, `head`, and `post`
  fields match upstream, except for intended changes. Names, version, and the
  fixed-pitch flag are correct. Every left side bearing equals the outline's
  minimum x. No glyph extends past the Windows clipping bounds.
- **Ligature outlines.** Each ligature matches its Fira Code source after
  Ligaturizer's scaling and the documented adjustments.
- **Shaping.** With HarfBuzz in eight script and language settings, and with
  CoreText on macOS:
  - Every retained ligature forms.
  - Every exclusion stays unligated.
  - `calt=0` disables ligatures.
  - Small caps work.
  - All characters keep a single cell advance.
- **Upstream parity.** With ligatures off, every character and the sample
  strings shape exactly as in Roboto Mono.

## Adding a glyph customization

Customizations live in [`scripts/customizations/`](scripts/customizations/).
Each one is a `Customization` subclass that declares what it touches and
redraws outlines in FontForge:

```python
from .base import Customization


class ExampleCustomization(Customization):
    name = "example"
    summary = "What changes and why"
    redraws = ("zero",)  # glyphs whose outlines redraw() replaces
    inherits = ()        # composites using them that should follow
    preserves = ()       # composites using them that keep the old design

    def redraw(self, font, style):
        ...  # edit font["zero"]; style has em, slant, descender
```

Add an instance to `CUSTOMIZATIONS` in `scripts/customizations/__init__.py`.
The build enforces the declaration:

- Every composite that references a redrawn glyph must be listed as inherited
  or preserved.
- Preserved composites get their references decomposed and must stay
  identical.
- Nothing else may change, advances included.

The manifest records the result, and `make check` verifies it in the final
fonts. Helpers in `outline.py` and `geometry.py` cover the common needs:
flattening outlines, rebuilding contours in their original direction, and
line and curve intersections. Measure from the upstream outline rather than
hard-coding coordinates, so one rule works across weights and italics. Then
run `make check` and `make proof`.

## License

The fonts are licensed under the SIL Open Font License 1.1 ([LICENSE](LICENSE)).
The build copies Roboto Mono's and Fira Code's copyright and license notices
to `fonts/OFL-Roboto-Mono.txt` and `fonts/OFL-Fira-Code.txt`. Keep them with
any redistributed fonts.
