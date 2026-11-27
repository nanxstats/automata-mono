"""Glyph customizations applied to Roboto Mono, in order.

To add one, write a Customization subclass in a new module (see base.py for
the contract the build enforces) and append an instance to CUSTOMIZATIONS.
These modules run inside FontForge's Python.
"""

from .a_tail import StraightTailA
from .base import Customization, CustomizationError, Style, apply_customizations
from .brackets import LongerBrackets
from .comma import StraightComma
from .currency_bars import FullCurrencyBars
from .g_spur import SpurG
from .percent import FullPercentSlash
from .r_serifs import SlabR
from .t_top import TallerT
from .tittle import Tittles
from .y_tail import StraightTailY

CUSTOMIZATIONS = (
    StraightComma(),
    Tittles(),
    StraightTailY(),
    TallerT(),
    LongerBrackets(),
    StraightTailA(),
    FullPercentSlash(),
    SlabR(),
    FullCurrencyBars(),
    SpurG(),
)

__all__ = [
    "CUSTOMIZATIONS",
    "Customization",
    "CustomizationError",
    "Style",
    "apply_customizations",
]
