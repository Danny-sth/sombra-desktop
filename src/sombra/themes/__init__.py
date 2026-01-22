"""Themes module - Theme management and stylesheets.

Provides unified Sombra branding with consistent color palette,
transparency values, shadows, and border radius constants.
"""

from .theme_manager import ThemeManager
from .colors import (
    # Brand colors
    SOMBRA_PRIMARY,
    SOMBRA_PRIMARY_LIGHT,
    SOMBRA_PRIMARY_DARK,
    SOMBRA_PRIMARY_MUTED,
    SOMBRA_PURPLE,
    SOMBRA_PURPLE_LIGHT,
    SOMBRA_CYAN,
    # Design system constants
    TRANSPARENCY,
    BORDER_RADIUS,
    SHADOWS,
    BLUR,
    # Theme palettes
    DARK_PALETTE,
    LIGHT_PALETTE,
    # Helper functions
    get_palette,
    get_transparency,
    get_shadow,
    get_radius,
    get_blur,
    hex_to_rgba,
    rgba_to_tuple,
)

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
