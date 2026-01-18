"""Color palette definitions for themes."""

# Dark Theme Palette - Modern cyberpunk-inspired
DARK_PALETTE = {
    # Background colors
    "bg_primary": "#1a1a2e",       # Main background
    "bg_secondary": "#16213e",     # Cards/panels background
    "bg_tertiary": "#0f3460",      # Hover/active states
    "bg_input": "#0d1b2a",         # Input fields background

    # Text colors
    "text_primary": "#eaeaea",     # Primary text
    "text_secondary": "#a0a0a0",   # Secondary/muted text
    "text_disabled": "#666666",    # Disabled text
    "text_placeholder": "#555555", # Placeholder text

    # Accent colors
    "accent_primary": "#e94560",   # Primary accent (red-pink)
    "accent_secondary": "#533483", # Secondary accent (purple)
    "accent_hover": "#ff6b8a",     # Accent hover state
    "accent_active": "#c73e54",    # Accent active state

    # Status colors
    "success": "#4ecca3",          # Success/online
    "warning": "#ffc107",          # Warning
    "error": "#ff6b6b",            # Error/recording
    "info": "#00d9ff",             # Info

    # Border colors
    "border_light": "#333355",     # Light border
    "border_dark": "#1a1a2e",      # Dark border
    "border_focus": "#e94560",     # Focused element border

    # Special
    "shadow": "rgba(0, 0, 0, 0.3)",
    "overlay": "rgba(26, 26, 46, 0.9)",
}

# Light Theme Palette - Clean and modern
LIGHT_PALETTE = {
    # Background colors
    "bg_primary": "#f5f5f5",       # Main background
    "bg_secondary": "#ffffff",     # Cards/panels background
    "bg_tertiary": "#e8e8e8",      # Hover/active states
    "bg_input": "#ffffff",         # Input fields background

    # Text colors
    "text_primary": "#212121",     # Primary text
    "text_secondary": "#757575",   # Secondary/muted text
    "text_disabled": "#bdbdbd",    # Disabled text
    "text_placeholder": "#9e9e9e", # Placeholder text

    # Accent colors
    "accent_primary": "#e94560",   # Primary accent (red-pink)
    "accent_secondary": "#7c4dff", # Secondary accent (purple)
    "accent_hover": "#ff6b8a",     # Accent hover state
    "accent_active": "#c73e54",    # Accent active state

    # Status colors
    "success": "#4caf50",          # Success/online
    "warning": "#ff9800",          # Warning
    "error": "#f44336",            # Error/recording
    "info": "#2196f3",             # Info

    # Border colors
    "border_light": "#e0e0e0",     # Light border
    "border_dark": "#bdbdbd",      # Dark border
    "border_focus": "#e94560",     # Focused element border

    # Special
    "shadow": "rgba(0, 0, 0, 0.1)",
    "overlay": "rgba(255, 255, 255, 0.9)",
}


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
