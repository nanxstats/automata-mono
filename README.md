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
| `r` | Bare stem; arm stops short of `f`'s hook | Flag at the x-height and foot bar on the baseline, drawn like Roboto's own `i`, and an arm as long as `f`'s hook, as in [IBM Plex Mono](https://github.com/IBM/plex), DM Mono, and [Geist Mono](https://github.com/vercel/geist-font) |
| `$` `¢` | Bar ends stick out above and below the outline | Bar runs through the glyph from top to bottom, as in JetBrains Mono, IBM Plex Mono, and DM Mono |
| `G` | Bowl sweeps into a stem that stops above the baseline, as in Source Code Pro | Stem runs straight down to a flat foot, with a spur where the bowl joins it like `d`'s, as in IBM Plex Mono, DM Mono, and Geist Mono |
| `Q` | Tail leans 40 to 46 degrees, its end cut square to the stroke | Straight tail at 50 degrees, cut flat under the right edge of the bowl, as in JetBrains Mono and DM Mono |
| `0` | Slashed, like `Ø` | Round dot in the middle of the counter, as in JetBrains Mono, IBM Plex Mono, and Source Code Pro |

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
- **r.** Roboto Mono gives i, j, and l slab serifs but leaves r a bare
  stem, with a wide gap on its left. r now gets a flag at the x-height and
  a foot bar on the baseline, as in IBM Plex Mono, DM Mono, and Geist Mono.
  Both have the thickness of i's flag and foot in each weight. The
  proportions are measured from those three fonts:
  - **Stem.** It moves 110 to 120 units right, to 0.10 of the cell left of
    i's stem (0.08 to 0.11 in those fonts). Upstream, it sits 0.20 left of
    i's, which leaves no room for a flag.
  - **Flag.** It is 0.75 as long as i's (0.68 to 0.81).
  - **Foot.** It starts below the end of the flag and reaches 1.25 times as
    far right of the stem as left of it (1.22 to 1.32).
  - **Arm.** Upstream, r's arm stops 0.047 of the cell short of f's hook.
    JetBrains Mono ends the two together, and in IBM Plex Mono, DM Mono, and
    Geist Mono, r's arm reaches 0.01 to 0.07 of the cell further. The arm
    now reaches as far as f's hook, 30 to 58 units further than upstream.
    The shoulder narrows to 0.85 to 0.89 of its width to make room for the
    stem. The tightest gap after r is 145 units in Regular (`r%`, `rw`) and
    105 in Bold (`rw`), against 85 for Roboto's own `ww` in Regular.

  ŕ, ř, and ŗ follow, and their accents move with the stem. Relative to
  the stem, Roboto already places the acute and caron where those fonts do,
  and the comma of ŗ stays under the stem, as in ļ. At 11 and 12 px, r
  reads close to a small capital I, as it does in those fonts.
- **Dollar and cent.** Roboto's bar ends stick out above and below the
  outline but stop at it. The bar now runs straight through, as in
  JetBrains Mono, IBM Plex Mono, and DM Mono. It closes the two counters of
  `$` and the left of the counter of `¢`.
  - **Position.** Upstream draws the two ends of `$`'s bar up to 21 units
    apart in upright styles, and up to 49 in italics, varying by weight. The
    bar runs halfway between them, upright or at the italic angle.
  - **Width.** `$` keeps the width of its bar ends, 0.81 of the stem of n
    in Regular. Those fonts draw both bars at the same width, 0.50 to 0.83
    of their stems. Roboto's `¢` ends are as wide as the stroke of c, which
    would clog the counter, so `¢` takes `$`'s bar width: 149 units instead
    of 185 in Regular, and 160 instead of 200 in Bold.
- **G.** Roboto's bowl sweeps out to the stem's outer edge, and the stem
  stops above the baseline, as in Source Code Pro, so G has no spur. The
  stem now runs straight down to the baseline and is cut flat, as in IBM
  Plex Mono, DM Mono, and Geist Mono. Those fonts join the bowl to the stem
  as in their own `d`, scaled up: G's crotch sits 0.13 to 0.30 of the cap
  height up, 0.8 to 1.1 times the fraction of the x-height at which `d`'s
  sits. G now takes Roboto's own `d` join the same way, with its heights
  scaled by the cap height over the x-height and its width fitted between
  the bottom of the bowl and the stem:
  - **Crotch.** The bowl's outer edge meets the stem 0.105 of the cap
    height up in Regular through Bold (152 to 153 units), 0.128 in Light,
    and 0.150 in Thin, the fractions of the x-height at which `d`'s does.
  - **Counter.** It curves up into the stem at 343 (Thin) to 433 (Bold)
    units instead of 181 to 270, so the bowl keeps its stroke into the
    stem. In Bold, it rounds up almost to the bar, as in IBM Plex Mono.
  - **Stem.** Both edges continue upstream's lines to the baseline. The
    bar, the top of the bowl, and the terminal are unchanged.

  At 11 to 14 px, the stem reaches the baseline as a square corner that C
  and 6 lack. Ğ, Ĝ, Ģ, Ġ, and the small capital G (`smcp`) follow; small
  caps scale the join by the small-cap height instead.
- **Q.** Roboto's tail leans 40 to 46 degrees, and its end is cut square
  to the stroke. JetBrains Mono and DM Mono cut their straight tails flat:
  JetBrains Mono's leans 59 degrees and DM Mono's 46 to 48. Their flat ends
  are 1.0 to 1.3 times as wide as the bowl's stroke. The tail now leans 50
  degrees and is cut flat, with Roboto's thickness and depth (246 to 263
  units below the baseline):
  - **End.** It is 1.05 (Bold Italic) to 1.30 (Thin) strokes wide. Cut
    flat at Roboto's angle, it would be up to 1.5 strokes wide and end in
    a sharp corner.
  - **Position.** The end's right corner sits under the bowl's right edge,
    as in those fonts: JetBrains Mono's ends up to 31 units past it, and DM
    Mono's up to 37 short of it. Roboto's ranges from 37 units short
    (Thin) to 61 past (Bold). In Regular through Bold, the tail moves 66 to
    150 units toward the middle of the bowl. Its center line now crosses
    the baseline 0.31 to 0.39 of the bowl's half-width right of center,
    against 0.51 to 0.59 upstream and 0.23 to 0.36 in those fonts. In Thin,
    it moves 33 units right.
  - **Bowl.** The bowl's outer edge is closed under the old tail with one
    curve, tangent to Roboto's on both sides, and the new tail leaves it
    there. The rest of the bowl and the counter are unchanged.

  The small capital Q (`smcp`) follows.
- **Zero.** Roboto slashes its zero, so it reads close to `Ø`, and the
  slash darkens it at small sizes. The zero now has a round dot in the
  middle of its counter, as in JetBrains Mono, IBM Plex Mono, and Source
  Code Pro.
  - **Dot.** It is the style's own period, scaled down, so it keeps
    Roboto's dot shape in every weight. It is 0.85 as wide as the period,
    so in Regular it is 0.44 as wide as the counter, against 0.39 to 0.48
    in those fonts and Fira Mono. Roboto's period grows faster with weight
    than the counter of 0, so the dot is at most 0.6 as wide as the
    counter, as in those fonts' Bold (0.52 to 0.66). Medium and Bold reach
    that limit. Dots are 101 units wide in Thin, 249 in Regular, 279 in
    Medium, and 232 in Bold.
  - **Counter.** The slash cut the counter in two. Each side is closed with
    one curve tangent to both halves, or a straight line in Bold, where
    the halves end on the counter's straight sides. In Light, interpolated
    between masters that the slash cuts in different places, the counter
    narrows by up to 9 units next to the slash. That narrowing is smoothed
    out. The outer outline is unchanged.

  At 11 to 14 px, the dot is one to two pixels across in Regular, lighter
  than the slash. In Bold at 11 and 12 px, it runs into the sides of the counter as
  the slash did, but 0 stays narrower than O.

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
    redraws = ("l",)  # glyphs whose outlines redraw() replaces
    inherits = ()  # composites using them that should follow
    preserves = ()  # composites using them that keep the old design

    def redraw(self, font, style):
        # Edit font["l"]; style has em, slant, descender.
        ...
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
