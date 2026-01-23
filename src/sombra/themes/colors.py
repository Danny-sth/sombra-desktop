"""Color palette definitions for Sombra themes.

Unified Sombra branding with consistent pink/red accent (#e94560),
transparency values for glassmorphism, and design system constants.
"""

# =============================================================================
# SOMBRA BRAND COLORS
# =============================================================================

# Primary brand color - Sombra Pink/Red
SOMBRA_PRIMARY = "#e94560"
SOMBRA_PRIMARY_LIGHT = "#ff6b8a"
SOMBRA_PRIMARY_DARK = "#c73e54"
SOMBRA_PRIMARY_MUTED = "#a63346"

# Secondary brand colors
SOMBRA_PURPLE = "#533483"
SOMBRA_PURPLE_LIGHT = "#7c4dff"
SOMBRA_CYAN = "#00d9ff"

# =============================================================================
# TRANSPARENCY VALUES (for glassmorphism effects)
# =============================================================================

TRANSPARENCY = {
    # Panel/card backgrounds with blur
    "panel_bg": "rgba(26, 26, 46, 0.85)",          # Main panels
    "panel_bg_light": "rgba(26, 26, 46, 0.70)",   # Lighter panels
    "panel_bg_heavy": "rgba(26, 26, 46, 0.95)",   # More opaque panels

    # Dialog/modal backgrounds
    "dialog_bg": "rgba(22, 33, 62, 0.92)",        # Dialog background
    "dialog_overlay": "rgba(0, 0, 0, 0.60)",      # Backdrop overlay

    # Card backgrounds
    "card_bg": "rgba(22, 33, 62, 0.80)",          # Card background
    "card_bg_hover": "rgba(22, 33, 62, 0.90)",    # Card hover state

    # Input field backgrounds
    "input_bg": "rgba(13, 27, 42, 0.85)",         # Input background
    "input_bg_focus": "rgba(13, 27, 42, 0.95)",   # Input focused

    # Button backgrounds
    "button_bg": "rgba(233, 69, 96, 0.15)",       # Ghost button bg
    "button_bg_hover": "rgba(233, 69, 96, 0.25)", # Ghost button hover

    # Tooltip/popover
    "tooltip_bg": "rgba(26, 26, 46, 0.95)",       # Tooltip background

    # Scrollbar
    "scrollbar": "rgba(233, 69, 96, 0.30)",       # Scrollbar thumb
    "scrollbar_hover": "rgba(233, 69, 96, 0.50)", # Scrollbar hover
}

# =============================================================================
# BORDER RADIUS CONSTANTS
# =============================================================================

BORDER_RADIUS = {
    "none": "0px",
    "sm": "4px",        # Small elements (tags, badges)
    "md": "8px",        # Medium elements (buttons, inputs)
    "lg": "12px",       # Large elements (cards)
    "xl": "16px",       # Extra large (panels, dialogs)
    "2xl": "20px",      # Hero cards
    "full": "9999px",   # Fully rounded (pills, avatars)
}

# =============================================================================
# SHADOW DEFINITIONS
# =============================================================================

SHADOWS = {
    # Subtle shadows for cards and panels
    "sm": "0 1px 2px rgba(0, 0, 0, 0.2)",
    "md": "0 4px 6px rgba(0, 0, 0, 0.25)",
    "lg": "0 8px 16px rgba(0, 0, 0, 0.30)",
    "xl": "0 12px 24px rgba(0, 0, 0, 0.35)",

    # Glow effects with Sombra pink
    "glow_sm": "0 0 8px rgba(233, 69, 96, 0.30)",
    "glow_md": "0 0 16px rgba(233, 69, 96, 0.40)",
    "glow_lg": "0 0 24px rgba(233, 69, 96, 0.50)",

    # Combined shadow + glow for accent elements
    "card": "0 4px 12px rgba(0, 0, 0, 0.25), 0 0 1px rgba(233, 69, 96, 0.10)",
    "card_hover": "0 8px 20px rgba(0, 0, 0, 0.30), 0 0 8px rgba(233, 69, 96, 0.20)",
    "button": "0 2px 8px rgba(233, 69, 96, 0.25)",
    "button_hover": "0 4px 12px rgba(233, 69, 96, 0.35)",

    # Inset shadows for inputs
    "inset": "inset 0 1px 3px rgba(0, 0, 0, 0.20)",
    "inset_focus": "inset 0 1px 3px rgba(0, 0, 0, 0.20), 0 0 0 2px rgba(233, 69, 96, 0.30)",

    # Dialog/modal shadow
    "dialog": "0 16px 48px rgba(0, 0, 0, 0.50), 0 0 1px rgba(233, 69, 96, 0.20)",
}

# =============================================================================
# BLUR VALUES (for backdrop-filter)
# =============================================================================

BLUR = {
    "sm": "4px",
    "md": "8px",
    "lg": "12px",
    "xl": "16px",
    "2xl": "24px",
}

# =============================================================================
# DARK THEME PALETTE - Sombra branded
# =============================================================================

DARK_PALETTE = {
    # Background colors (deep blue/purple tones)
    "bg_primary": "#1a1a2e",           # Main background
    "bg_secondary": "#16213e",         # Cards/panels background
    "bg_tertiary": "#0f3460",          # Hover/active states
    "bg_input": "#0d1b2a",             # Input fields background
    "bg_elevated": "#1e2746",          # Elevated surfaces
    "bg_sunken": "#12121f",            # Sunken/recessed areas

    # Text colors
    "text_primary": "#f0f0f0",         # Primary text (slightly brighter)
    "text_secondary": "#a8a8b3",       # Secondary/muted text
    "text_disabled": "#5a5a6e",        # Disabled text
    "text_placeholder": "#4a4a5e",     # Placeholder text
    "text_inverse": "#1a1a2e",         # Text on accent backgrounds

    # Sombra accent colors
    "accent_primary": SOMBRA_PRIMARY,          # #e94560 - Primary accent
    "accent_primary_light": SOMBRA_PRIMARY_LIGHT,  # #ff6b8a - Hover state
    "accent_primary_dark": SOMBRA_PRIMARY_DARK,    # #c73e54 - Active state
    "accent_primary_muted": SOMBRA_PRIMARY_MUTED,  # #a63346 - Subtle accent
    "accent_secondary": SOMBRA_PURPLE,         # #533483 - Secondary accent
    "accent_secondary_light": SOMBRA_PURPLE_LIGHT, # #7c4dff - Secondary hover

    # Legacy accent names (for compatibility)
    "accent_hover": SOMBRA_PRIMARY_LIGHT,
    "accent_active": SOMBRA_PRIMARY_DARK,

    # Status colors
    "success": "#4ecca3",              # Success/online/connected
    "success_muted": "#3ba583",        # Muted success
    "warning": "#f9a825",              # Warning (warmer yellow)
    "warning_muted": "#c68400",        # Muted warning
    "error": "#ff6b6b",                # Error state
    "error_muted": "#cc5555",          # Muted error
    "info": SOMBRA_CYAN,               # #00d9ff - Info
    "info_muted": "#00a8c7",           # Muted info

    # Border colors
    "border_subtle": "#2a2a45",        # Subtle borders
    "border_default": "#333355",       # Default borders
    "border_strong": "#444466",        # Strong borders
    "border_focus": SOMBRA_PRIMARY,    # Focused element border
    "border_accent": SOMBRA_PRIMARY_MUTED,  # Accent borders

    # Legacy border names (for compatibility)
    "border_light": "#333355",
    "border_dark": "#1a1a2e",

    # Interactive states
    "hover_overlay": "rgba(233, 69, 96, 0.08)",   # Hover overlay
    "active_overlay": "rgba(233, 69, 96, 0.15)",  # Active/pressed overlay
    "selected_bg": "rgba(233, 69, 96, 0.12)",     # Selected item background

    # Special/utility
    "shadow": "rgba(0, 0, 0, 0.35)",
    "overlay": "rgba(26, 26, 46, 0.90)",
    "backdrop": "rgba(0, 0, 0, 0.60)",
    "divider": "rgba(255, 255, 255, 0.08)",

    # Scrollbar
    "scrollbar_track": "#1a1a2e",
    "scrollbar_thumb": "rgba(233, 69, 96, 0.35)",
    "scrollbar_thumb_hover": "rgba(233, 69, 96, 0.55)",
}

# =============================================================================
# LIGHT THEME PALETTE - Sombra branded (maintains pink accent)
# =============================================================================

LIGHT_PALETTE = {
    # Background colors
    "bg_primary": "#f8f8fa",           # Main background
    "bg_secondary": "#ffffff",         # Cards/panels background
    "bg_tertiary": "#f0f0f5",          # Hover/active states
    "bg_input": "#ffffff",             # Input fields background
    "bg_elevated": "#ffffff",          # Elevated surfaces
    "bg_sunken": "#f0f0f5",            # Sunken/recessed areas

    # Text colors
    "text_primary": "#1a1a2e",         # Primary text (matches dark bg)
    "text_secondary": "#5a5a6e",       # Secondary/muted text
    "text_disabled": "#a0a0a8",        # Disabled text
    "text_placeholder": "#b0b0b8",     # Placeholder text
    "text_inverse": "#f0f0f0",         # Text on accent backgrounds

    # Sombra accent colors (same as dark theme for brand consistency)
    "accent_primary": SOMBRA_PRIMARY,
    "accent_primary_light": SOMBRA_PRIMARY_LIGHT,
    "accent_primary_dark": SOMBRA_PRIMARY_DARK,
    "accent_primary_muted": "#d64a5f",     # Slightly adjusted for light bg
    "accent_secondary": SOMBRA_PURPLE_LIGHT,
    "accent_secondary_light": "#9c7aff",

    # Legacy accent names (for compatibility)
    "accent_hover": SOMBRA_PRIMARY_LIGHT,
    "accent_active": SOMBRA_PRIMARY_DARK,

    # Status colors (adjusted for light backgrounds)
    "success": "#2e9b77",              # Darker green for contrast
    "success_muted": "#4ecca3",
    "warning": "#e69500",              # Darker yellow
    "warning_muted": "#f9a825",
    "error": "#d94545",                # Darker red
    "error_muted": "#ff6b6b",
    "info": "#0099cc",                 # Darker cyan
    "info_muted": "#00d9ff",

    # Border colors
    "border_subtle": "#e8e8ee",        # Subtle borders
    "border_default": "#d8d8e0",       # Default borders
    "border_strong": "#c8c8d0",        # Strong borders
    "border_focus": SOMBRA_PRIMARY,
    "border_accent": SOMBRA_PRIMARY_MUTED,

    # Legacy border names (for compatibility)
    "border_light": "#e0e0e8",
    "border_dark": "#d0d0d8",

    # Interactive states
    "hover_overlay": "rgba(233, 69, 96, 0.06)",
    "active_overlay": "rgba(233, 69, 96, 0.12)",
    "selected_bg": "rgba(233, 69, 96, 0.10)",

    # Special/utility
    "shadow": "rgba(0, 0, 0, 0.08)",
    "overlay": "rgba(255, 255, 255, 0.92)",
    "backdrop": "rgba(0, 0, 0, 0.40)",
    "divider": "rgba(0, 0, 0, 0.08)",

    # Scrollbar
    "scrollbar_track": "#f0f0f5",
    "scrollbar_thumb": "rgba(233, 69, 96, 0.25)",
    "scrollbar_thumb_hover": "rgba(233, 69, 96, 0.45)",
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_palette(theme: str) -> dict[str, str]:
    """Get color palette for a theme.

    Args:
        theme: Theme name ('dark' or 'light').

    Returns:
        Color palette dictionary.
    """
    if theme == "light":
        return LIGHT_PALETTE
    return DARK_PALETTE


def get_transparency(key: str) -> str:
    """Get transparency value by key.

    Args:
        key: Transparency key (e.g., 'panel_bg', 'card_bg').

    Returns:
        RGBA color string.
    """
    return TRANSPARENCY.get(key, TRANSPARENCY["panel_bg"])


def get_shadow(key: str) -> str:
    """Get shadow value by key.

    Args:
        key: Shadow key (e.g., 'card', 'button', 'glow_md').

    Returns:
        CSS box-shadow string.
    """
    return SHADOWS.get(key, SHADOWS["md"])


def get_radius(key: str) -> str:
    """Get border radius value by key.

    Args:
        key: Radius key (e.g., 'sm', 'md', 'lg').

    Returns:
        CSS border-radius string.
    """
    return BORDER_RADIUS.get(key, BORDER_RADIUS["md"])


def get_blur(key: str) -> str:
    """Get blur value by key.

    Args:
        key: Blur key (e.g., 'sm', 'md', 'lg').

    Returns:
        CSS blur value string.
    """
    return BLUR.get(key, BLUR["md"])


def rgba_to_tuple(rgba_str: str) -> tuple[int, int, int, float] | None:
    """Parse an rgba string to a tuple.

    Args:
        rgba_str: RGBA color string like 'rgba(233, 69, 96, 0.5)'.

    Returns:
        Tuple of (r, g, b, a) or None if parsing fails.
    """
    import re
    match = re.match(r'rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)', rgba_str)
    if match:
        r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
        a = float(match.group(4)) if match.group(4) else 1.0
        return (r, g, b, a)
    return None


def hex_to_rgba(hex_color: str, alpha: float = 1.0) -> str:
    """Convert hex color to rgba string.

    Args:
        hex_color: Hex color string like '#e94560'.
        alpha: Alpha value (0.0 to 1.0).

    Returns:
        RGBA color string.
    """
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"
