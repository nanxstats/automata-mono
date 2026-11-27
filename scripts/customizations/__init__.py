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
from .flat_hooks import FlatHooks
from .g_spur import SpurG
from .one_foot import FootedOne
from .open_six_nine import OpenSixNine
from .percent import FullPercentSlash
from .q_tail import FlatTailQ
from .r_serifs import SlabR
from .t_top import TallerT
from .tittle import Tittles
from .y_tail import StraightTailY
from .zero_dot import DottedZero

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
    FlatTailQ(),
    DottedZero(),
    FootedOne(),
    OpenSixNine(),
    FlatHooks(),
)

__all__ = [
    "CUSTOMIZATIONS",
    "Customization",
    "CustomizationError",
    "Style",
    "apply_customizations",
]
