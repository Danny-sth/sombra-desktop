"""Themes module - Theme management and stylesheets.

Provides unified Sombra branding with consistent color palette,
transparency values, shadows, and border radius constants.
"""

from .colors import (
    BLUR,
    BORDER_RADIUS,
    # Theme palettes
    DARK_PALETTE,
    LIGHT_PALETTE,
    SHADOWS,
    SOMBRA_CYAN,
    # Brand colors
    SOMBRA_PRIMARY,
    SOMBRA_PRIMARY_DARK,
    SOMBRA_PRIMARY_LIGHT,
    SOMBRA_PRIMARY_MUTED,
    SOMBRA_PURPLE,
    SOMBRA_PURPLE_LIGHT,
    # Design system constants
    TRANSPARENCY,
    get_blur,
    # Helper functions
    get_palette,
    get_radius,
    get_shadow,
    get_transparency,
    hex_to_rgba,
    rgba_to_tuple,
)
from .theme_manager import ThemeManager

__all__ = [
    # Manager
    "ThemeManager",
    # Brand colors
    "SOMBRA_PRIMARY",
    "SOMBRA_PRIMARY_LIGHT",
    "SOMBRA_PRIMARY_DARK",
    "SOMBRA_PRIMARY_MUTED",
    "SOMBRA_PURPLE",
    "SOMBRA_PURPLE_LIGHT",
    "SOMBRA_CYAN",
    # Design system constants
    "TRANSPARENCY",
    "BORDER_RADIUS",
    "SHADOWS",
    "BLUR",
    # Theme palettes
    "DARK_PALETTE",
    "LIGHT_PALETTE",
    # Helper functions
    "get_palette",
    "get_transparency",
    "get_shadow",
    "get_radius",
    "get_blur",
    "hex_to_rgba",
    "rgba_to_tuple",
]
