"""Glyph customizations applied to Roboto Mono, in order.

To add one, write a Customization subclass in a new module (see base.py for
the contract the build enforces) and append an instance to CUSTOMIZATIONS.
These modules run inside FontForge's Python.
"""

from .base import Customization, CustomizationError, Style, apply_customizations
from .brackets import LongerBrackets
from .comma import StraightComma
from .t_top import TallerT
from .tittle import Tittles
from .y_tail import StraightTailY

CUSTOMIZATIONS = (
    StraightComma(),
    Tittles(),
    StraightTailY(),
    TallerT(),
    LongerBrackets(),
)

__all__ = ["CUSTOMIZATIONS", "Customization", "CustomizationError", "Style", "apply_customizations"]
