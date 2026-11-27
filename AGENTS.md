# AGENTS.md

## Project

- Automata Mono is Roboto Mono (static TTFs, 2048 UPM, ten styles) with Fira
  Code ligatures via Ligaturizer and a set of glyph customizations.
- Outputs: `fonts/AutomataMono-<Style>.ttf` and the upstream OFL notices.
  Style names follow upstream; the regular italic is `Italic`.
- Cell width is 1229 units upright and 1202 italic. Read it from the font;
  never hard-code it.

## Pipeline

- `make` builds and validates; `make check` must pass after any change to
  the build. `make proof` renders before/after sheets to `build/proof/`;
  look at them after changing glyph designs.
- After any Python change, run `uv run --locked ruff format` and
  `uv run --locked ruff check`; both must be clean.
- `scripts/build_font.py` runs in FontForge's Python (`fontforge -script`):
  standard library, `fontforge`, `psMat`, and Ligaturizer only.
  `scripts/finalize.py`, `validate.py`, and `proof.py` run with `uv run`.
  `scripts/config.py` is shared and must stay standard-library only.
- Upstream checkouts (`RobotoMono/`, `Ligaturizer/`) are fetched at commits
  pinned in the `Makefile`. Never modify them. Update a pin deliberately and
  rebuild from clean.
- `STYLES` and `FIRA_WEIGHTS` appear in both the `Makefile` and
  `scripts/config.py`; keep them in sync. The Makefile must work with GNU
  Make 3.81.
- Python dependencies are managed with uv (`uv add`, `uv sync`; commands
  run with `--locked`). Keep the 7-day cooldown (`exclude-newer`) in
  `pyproject.toml`. Ask before adding Homebrew dependencies.

## Glyph customizations

- One `Customization` subclass per module in `scripts/customizations/`,
  registered in `CUSTOMIZATIONS`. Declare `redraws`, `inherits`, and
  `preserves`; the build fails on any undeclared change or unclassified
  composite. Do not weaken these checks to make a build pass.
- Derive geometry from the upstream outlines and per-style metrics (`Style`)
  so one rule covers every weight and italic. Assert the structure you rely
  on, and preserve contour direction.
- Current customizations: straight comma (Cyrillic tailed letters keep the
  upstream comma), i/j dots 15% larger at a 0.11 em gap and 0.009 em left
  of the stem center, straight-tail y, t stem at 0.86 of the way from
  x-height to cap height, bracket arms 0.30 of the cell past the stem,
  a straight a stem cut flat at the baseline (ą follows), a % slash from
  the baseline to the cap height across the rings, cut flat, an r with
  i's flag and foot, its stem 0.10 of the cell left of i's, and its arm
  ending level with f's hook (ŕ ř ŗ accents move with the stem), $ and ¢
  bars through the glyph at $'s width, and a G stem cut flat at the
  baseline with a spur, joined to the bowl like d's at heights scaled by
  cap height over x-height (Ğ Ĝ Ģ Ġ and small caps follow), a Q tail at 50
  degrees, cut flat at upstream's depth and thickness with its right corner
  under the bowl's right edge (the small cap follows), a 0 with a dot in
  place of the slash: the period at 0.85 of its width, at most 0.6 of the
  counter's, a 1 with l's foot under the upstream flag, 6 and 9 with
  straight strokes at 60 degrees, tangent to the counter and as thick as
  7's leg, cut flat at the figure height and on the baseline, the bowl's
  side rebuilt into the stroke and the counter's corner rounded off, and
  hooks of f, g, j, and t that run flat along l's top, p's bottom, or the
  baseline into an upright cut at upstream's reach, moved along the stem
  by their overshoot (ŧ, ĳ, and dotless j follow).

## Ligatures

- Keep the exclusions: `&&`, `~@`, `\/`, `.?`, `?:`, `?=`, `?.`, `??`, `;;`,
  `/\`, `www`. Fira Code v3.1 lacks `~=`.
- Ligatures come from the Fira Code weight with the closest operator stroke
  (Bold uses SemiBold; Thin uses Light). Use Ligaturizer's
  `LigatureCreator`; do not patch Ligaturizer.
- `calt` is registered only under the font's own script systems, so that
  `smcp` keeps working. Italic ligatures are slanted about the math axis.
  `||` is fitted to Roboto's `|`.

## Release invariants

- With ligatures off, shaping must match Roboto Mono exactly.
- Keep these as upstream has them:
  - Vertical metrics and the character map.
  - The table set: no GDEF, GPOS, or AAT tables.
- Every glyph has the cell advance, and every left side bearing equals the
  outline's xMin.
- Keep upstream copyright and license notices with the fonts; do not ship
  Roboto's trademark notice.

## Working here

- Respect existing changes; never reset or revert unless asked.
- Keep comments for non-obvious reasons, not narration.
