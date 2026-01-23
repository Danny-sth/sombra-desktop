"""Unit tests for colors.py - Sombra theme color palette.

Tests verify:
- SOMBRA_PRIMARY color (#e94560) is correctly defined
- Dark and Light palettes have all required keys
- Transparency values for glassmorphism
- Border radius constants
- Shadow definitions for cards and buttons
- Blur values for backdrop effects
- Helper functions work correctly
"""

import re

from sombra.themes.colors import (
    # Blur
    BLUR,
    # Border radius
    BORDER_RADIUS,
    # Palettes
    DARK_PALETTE,
    LIGHT_PALETTE,
    # Shadows
    SHADOWS,
    SOMBRA_CYAN,
    # Brand colors
    SOMBRA_PRIMARY,
    SOMBRA_PRIMARY_DARK,
    SOMBRA_PRIMARY_LIGHT,
    SOMBRA_PRIMARY_MUTED,
    SOMBRA_PURPLE,
    SOMBRA_PURPLE_LIGHT,
    # Transparency
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


class TestSombraBrandColors:
    """Tests for Sombra brand color definitions."""

    def test_sombra_primary_is_pink_red(self):
        """Test SOMBRA_PRIMARY is #e94560."""
        assert SOMBRA_PRIMARY == "#e94560"

    def test_sombra_primary_light(self):
        """Test SOMBRA_PRIMARY_LIGHT is defined correctly."""
        assert SOMBRA_PRIMARY_LIGHT == "#ff6b8a"

    def test_sombra_primary_dark(self):
        """Test SOMBRA_PRIMARY_DARK is defined correctly."""
        assert SOMBRA_PRIMARY_DARK == "#c73e54"

    def test_sombra_primary_muted(self):
        """Test SOMBRA_PRIMARY_MUTED is defined correctly."""
        assert SOMBRA_PRIMARY_MUTED == "#a63346"

    def test_sombra_purple(self):
        """Test SOMBRA_PURPLE secondary color."""
        assert SOMBRA_PURPLE == "#533483"

    def test_sombra_purple_light(self):
        """Test SOMBRA_PURPLE_LIGHT color."""
        assert SOMBRA_PURPLE_LIGHT == "#7c4dff"

    def test_sombra_cyan(self):
        """Test SOMBRA_CYAN accent color for info."""
        assert SOMBRA_CYAN == "#00d9ff"

    def test_all_brand_colors_are_valid_hex(self):
        """Test all brand colors are valid hex format."""
        hex_pattern = re.compile(r'^#[0-9a-fA-F]{6}$')
        colors = [
            SOMBRA_PRIMARY,
            SOMBRA_PRIMARY_LIGHT,
            SOMBRA_PRIMARY_DARK,
            SOMBRA_PRIMARY_MUTED,
            SOMBRA_PURPLE,
            SOMBRA_PURPLE_LIGHT,
            SOMBRA_CYAN,
        ]
        for color in colors:
            assert hex_pattern.match(color), f"Invalid hex color: {color}"


class TestTransparencyValues:
    """Tests for TRANSPARENCY dictionary (glassmorphism effects)."""

    def test_transparency_has_panel_bg(self):
        """Test panel background transparency exists."""
        assert "panel_bg" in TRANSPARENCY
        assert "rgba" in TRANSPARENCY["panel_bg"]

    def test_transparency_has_panel_bg_light(self):
        """Test lighter panel background exists."""
        assert "panel_bg_light" in TRANSPARENCY

    def test_transparency_has_panel_bg_heavy(self):
        """Test heavier panel background exists."""
        assert "panel_bg_heavy" in TRANSPARENCY

    def test_transparency_has_dialog_bg(self):
        """Test dialog background transparency exists."""
        assert "dialog_bg" in TRANSPARENCY

    def test_transparency_has_dialog_overlay(self):
        """Test dialog overlay transparency exists."""
        assert "dialog_overlay" in TRANSPARENCY

    def test_transparency_has_card_bg(self):
        """Test card background transparency exists."""
        assert "card_bg" in TRANSPARENCY

    def test_transparency_has_card_bg_hover(self):
        """Test card hover background exists."""
        assert "card_bg_hover" in TRANSPARENCY

    def test_transparency_has_input_bg(self):
        """Test input background transparency exists."""
        assert "input_bg" in TRANSPARENCY

    def test_transparency_has_input_bg_focus(self):
        """Test input focus background exists."""
        assert "input_bg_focus" in TRANSPARENCY

    def test_transparency_has_button_bg(self):
        """Test button background transparency exists."""
        assert "button_bg" in TRANSPARENCY

    def test_transparency_has_button_bg_hover(self):
        """Test button hover background exists."""
        assert "button_bg_hover" in TRANSPARENCY

    def test_transparency_has_tooltip_bg(self):
        """Test tooltip background exists."""
        assert "tooltip_bg" in TRANSPARENCY

    def test_transparency_has_scrollbar(self):
        """Test scrollbar transparency exists."""
        assert "scrollbar" in TRANSPARENCY
        assert "scrollbar_hover" in TRANSPARENCY

    def test_all_transparency_values_are_rgba(self):
        """Test all transparency values are valid rgba strings."""
        rgba_pattern = re.compile(r'^rgba\(\d+,\s*\d+,\s*\d+,\s*[\d.]+\)$')
        for key, value in TRANSPARENCY.items():
            assert rgba_pattern.match(value), f"Invalid rgba for {key}: {value}"

    def test_panel_bg_has_correct_opacity(self):
        """Test panel_bg has 0.85 opacity for proper blur effect."""
        # rgba(26, 26, 46, 0.85)
        assert "0.85" in TRANSPARENCY["panel_bg"]

    def test_card_bg_has_correct_opacity(self):
        """Test card_bg has 0.80 opacity."""
        # rgba(22, 33, 62, 0.80)
        assert "0.80" in TRANSPARENCY["card_bg"] or "0.8)" in TRANSPARENCY["card_bg"]


class TestBorderRadius:
    """Tests for BORDER_RADIUS constants."""

    def test_border_radius_has_none(self):
        """Test none radius is 0px."""
        assert BORDER_RADIUS["none"] == "0px"

    def test_border_radius_has_sm(self):
        """Test small radius is 4px."""
        assert BORDER_RADIUS["sm"] == "4px"

    def test_border_radius_has_md(self):
        """Test medium radius is 8px for buttons and inputs."""
        assert BORDER_RADIUS["md"] == "8px"

    def test_border_radius_has_lg(self):
        """Test large radius is 12px for cards."""
        assert BORDER_RADIUS["lg"] == "12px"

    def test_border_radius_has_xl(self):
        """Test extra large radius is 16px for panels."""
        assert BORDER_RADIUS["xl"] == "16px"

    def test_border_radius_has_2xl(self):
        """Test 2xl radius is 20px for hero cards."""
        assert BORDER_RADIUS["2xl"] == "20px"

    def test_border_radius_has_full(self):
        """Test full radius for pills/avatars."""
        assert BORDER_RADIUS["full"] == "9999px"

    def test_all_radius_values_are_px(self):
        """Test all radius values end with 'px'."""
        for key, value in BORDER_RADIUS.items():
            assert value.endswith("px"), f"Invalid radius format for {key}: {value}"


class TestShadows:
    """Tests for SHADOWS definitions."""

    def test_shadows_has_basic_sizes(self):
        """Test basic shadow sizes exist."""
        assert "sm" in SHADOWS
        assert "md" in SHADOWS
        assert "lg" in SHADOWS
        assert "xl" in SHADOWS

    def test_shadows_has_glow_effects(self):
        """Test glow effects with Sombra pink exist."""
        assert "glow_sm" in SHADOWS
        assert "glow_md" in SHADOWS
        assert "glow_lg" in SHADOWS

    def test_shadows_has_card_shadows(self):
        """Test card-specific shadows exist."""
        assert "card" in SHADOWS
        assert "card_hover" in SHADOWS

    def test_shadows_has_button_shadows(self):
        """Test button-specific shadows exist."""
        assert "button" in SHADOWS
        assert "button_hover" in SHADOWS

    def test_shadows_has_inset(self):
        """Test inset shadows for inputs exist."""
        assert "inset" in SHADOWS
        assert "inset_focus" in SHADOWS

    def test_shadows_has_dialog(self):
        """Test dialog shadow exists."""
        assert "dialog" in SHADOWS

    def test_glow_shadows_contain_sombra_pink_rgb(self):
        """Test glow shadows use Sombra pink (233, 69, 96)."""
        assert "233, 69, 96" in SHADOWS["glow_sm"]
        assert "233, 69, 96" in SHADOWS["glow_md"]
        assert "233, 69, 96" in SHADOWS["glow_lg"]

    def test_card_shadow_has_subtle_glow(self):
        """Test card shadow includes subtle Sombra glow."""
        assert "233, 69, 96" in SHADOWS["card"]

    def test_button_shadow_has_sombra_color(self):
        """Test button shadow uses Sombra pink."""
        assert "233, 69, 96" in SHADOWS["button"]


class TestBlur:
    """Tests for BLUR values (backdrop-filter)."""

    def test_blur_has_sm(self):
        """Test small blur is 4px."""
        assert BLUR["sm"] == "4px"

    def test_blur_has_md(self):
        """Test medium blur is 8px."""
        assert BLUR["md"] == "8px"

    def test_blur_has_lg(self):
        """Test large blur is 12px."""
        assert BLUR["lg"] == "12px"

    def test_blur_has_xl(self):
        """Test extra large blur is 16px."""
        assert BLUR["xl"] == "16px"

    def test_blur_has_2xl(self):
        """Test 2xl blur is 24px."""
        assert BLUR["2xl"] == "24px"

    def test_all_blur_values_are_px(self):
        """Test all blur values end with 'px'."""
        for key, value in BLUR.items():
            assert value.endswith("px"), f"Invalid blur format for {key}: {value}"


class TestDarkPalette:
    """Tests for DARK_PALETTE color definitions."""

    def test_dark_palette_has_background_colors(self):
        """Test dark palette has all background colors."""
        bg_keys = [
            "bg_primary", "bg_secondary", "bg_tertiary",
            "bg_input", "bg_elevated", "bg_sunken",
        ]
        for key in bg_keys:
            assert key in DARK_PALETTE, f"Missing {key} in DARK_PALETTE"

    def test_dark_palette_has_text_colors(self):
        """Test dark palette has all text colors."""
        text_keys = [
            "text_primary", "text_secondary", "text_disabled",
            "text_placeholder", "text_inverse",
        ]
        for key in text_keys:
            assert key in DARK_PALETTE, f"Missing {key} in DARK_PALETTE"

    def test_dark_palette_has_accent_colors(self):
        """Test dark palette has Sombra accent colors."""
        assert DARK_PALETTE["accent_primary"] == SOMBRA_PRIMARY
        assert DARK_PALETTE["accent_primary_light"] == SOMBRA_PRIMARY_LIGHT
        assert DARK_PALETTE["accent_primary_dark"] == SOMBRA_PRIMARY_DARK
        assert DARK_PALETTE["accent_primary_muted"] == SOMBRA_PRIMARY_MUTED

    def test_dark_palette_has_status_colors(self):
        """Test dark palette has status colors."""
        assert "success" in DARK_PALETTE
        assert "warning" in DARK_PALETTE
        assert "error" in DARK_PALETTE
        assert "info" in DARK_PALETTE

    def test_dark_palette_has_border_colors(self):
        """Test dark palette has border colors."""
        border_keys = [
            "border_subtle", "border_default", "border_strong",
            "border_focus", "border_accent",
        ]
        for key in border_keys:
            assert key in DARK_PALETTE, f"Missing {key} in DARK_PALETTE"

    def test_dark_palette_border_focus_is_sombra_primary(self):
        """Test border_focus uses SOMBRA_PRIMARY."""
        assert DARK_PALETTE["border_focus"] == SOMBRA_PRIMARY

    def test_dark_palette_has_interactive_states(self):
        """Test dark palette has interactive overlay colors."""
        assert "hover_overlay" in DARK_PALETTE
        assert "active_overlay" in DARK_PALETTE
        assert "selected_bg" in DARK_PALETTE

    def test_dark_palette_has_scrollbar_colors(self):
        """Test dark palette has scrollbar colors."""
        assert "scrollbar_track" in DARK_PALETTE
        assert "scrollbar_thumb" in DARK_PALETTE
        assert "scrollbar_thumb_hover" in DARK_PALETTE

    def test_dark_palette_bg_primary_is_dark(self):
        """Test bg_primary is a dark color (#1a1a2e)."""
        assert DARK_PALETTE["bg_primary"] == "#1a1a2e"

    def test_dark_palette_text_primary_is_light(self):
        """Test text_primary is light for dark theme readability."""
        assert DARK_PALETTE["text_primary"] == "#f0f0f0"


class TestLightPalette:
    """Tests for LIGHT_PALETTE color definitions."""

    def test_light_palette_has_same_keys_as_dark(self):
        """Test light palette has same keys as dark palette."""
        for key in DARK_PALETTE.keys():
            assert key in LIGHT_PALETTE, f"Missing {key} in LIGHT_PALETTE"

    def test_light_palette_has_sombra_accent(self):
        """Test light palette uses same Sombra primary accent."""
        assert LIGHT_PALETTE["accent_primary"] == SOMBRA_PRIMARY

    def test_light_palette_bg_primary_is_light(self):
        """Test bg_primary is a light color for light theme."""
        assert LIGHT_PALETTE["bg_primary"] == "#f8f8fa"

    def test_light_palette_text_primary_is_dark(self):
        """Test text_primary is dark for light theme readability."""
        assert LIGHT_PALETTE["text_primary"] == "#1a1a2e"


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_get_palette_returns_dark_by_default(self):
        """Test get_palette returns dark palette by default."""
        palette = get_palette("dark")
        assert palette == DARK_PALETTE

    def test_get_palette_returns_light(self):
        """Test get_palette returns light palette."""
        palette = get_palette("light")
        assert palette == LIGHT_PALETTE

    def test_get_palette_defaults_to_dark_for_invalid(self):
        """Test get_palette returns dark for invalid theme name."""
        palette = get_palette("invalid_theme")
        assert palette == DARK_PALETTE

    def test_get_transparency_returns_value(self):
        """Test get_transparency returns correct value."""
        value = get_transparency("panel_bg")
        assert value == TRANSPARENCY["panel_bg"]

    def test_get_transparency_defaults_to_panel_bg(self):
        """Test get_transparency returns panel_bg for invalid key."""
        value = get_transparency("nonexistent_key")
        assert value == TRANSPARENCY["panel_bg"]

    def test_get_shadow_returns_value(self):
        """Test get_shadow returns correct value."""
        value = get_shadow("card")
        assert value == SHADOWS["card"]

    def test_get_shadow_defaults_to_md(self):
        """Test get_shadow returns md for invalid key."""
        value = get_shadow("nonexistent_key")
        assert value == SHADOWS["md"]

    def test_get_radius_returns_value(self):
        """Test get_radius returns correct value."""
        value = get_radius("lg")
        assert value == BORDER_RADIUS["lg"]

    def test_get_radius_defaults_to_md(self):
        """Test get_radius returns md for invalid key."""
        value = get_radius("nonexistent_key")
        assert value == BORDER_RADIUS["md"]

    def test_get_blur_returns_value(self):
        """Test get_blur returns correct value."""
        value = get_blur("lg")
        assert value == BLUR["lg"]

    def test_get_blur_defaults_to_md(self):
        """Test get_blur returns md for invalid key."""
        value = get_blur("nonexistent_key")
        assert value == BLUR["md"]


class TestRgbaToTuple:
    """Tests for rgba_to_tuple helper function."""

    def test_rgba_to_tuple_parses_rgba(self):
        """Test parsing rgba string to tuple."""
        result = rgba_to_tuple("rgba(233, 69, 96, 0.5)")
        assert result == (233, 69, 96, 0.5)

    def test_rgba_to_tuple_parses_rgba_without_space(self):
        """Test parsing rgba without spaces."""
        result = rgba_to_tuple("rgba(233,69,96,0.5)")
        assert result == (233, 69, 96, 0.5)

    def test_rgba_to_tuple_parses_rgb(self):
        """Test parsing rgb string (without alpha)."""
        result = rgba_to_tuple("rgb(233, 69, 96)")
        assert result == (233, 69, 96, 1.0)

    def test_rgba_to_tuple_returns_none_for_invalid(self):
        """Test invalid string returns None."""
        result = rgba_to_tuple("not a color")
        assert result is None

    def test_rgba_to_tuple_returns_none_for_hex(self):
        """Test hex color returns None."""
        result = rgba_to_tuple("#e94560")
        assert result is None


class TestHexToRgba:
    """Tests for hex_to_rgba helper function."""

    def test_hex_to_rgba_converts_with_default_alpha(self):
        """Test hex to rgba conversion with default alpha."""
        result = hex_to_rgba("#e94560")
        assert result == "rgba(233, 69, 96, 1.0)"

    def test_hex_to_rgba_converts_with_custom_alpha(self):
        """Test hex to rgba conversion with custom alpha."""
        result = hex_to_rgba("#e94560", 0.5)
        assert result == "rgba(233, 69, 96, 0.5)"

    def test_hex_to_rgba_handles_lowercase(self):
        """Test hex conversion handles lowercase."""
        result = hex_to_rgba("#e94560", 0.5)
        assert "233" in result
        assert "69" in result
        assert "96" in result

    def test_hex_to_rgba_handles_uppercase(self):
        """Test hex conversion handles uppercase."""
        result = hex_to_rgba("#E94560", 0.5)
        assert "233" in result
        assert "69" in result
        assert "96" in result

    def test_hex_to_rgba_handles_without_hash(self):
        """Test hex conversion works without # prefix."""
        result = hex_to_rgba("e94560", 0.5)
        assert "233" in result
        assert "69" in result
        assert "96" in result


class TestColorConsistency:
    """Tests for color consistency across the theme system."""

    def test_scrollbar_uses_sombra_pink(self):
        """Test scrollbar colors use Sombra pink."""
        assert "233, 69, 96" in DARK_PALETTE["scrollbar_thumb"]
        assert "233, 69, 96" in DARK_PALETTE["scrollbar_thumb_hover"]

    def test_hover_overlays_use_sombra_pink(self):
        """Test hover overlays use Sombra pink."""
        assert "233, 69, 96" in DARK_PALETTE["hover_overlay"]
        assert "233, 69, 96" in DARK_PALETTE["active_overlay"]

    def test_selected_bg_uses_sombra_pink(self):
        """Test selected background uses Sombra pink."""
        assert "233, 69, 96" in DARK_PALETTE["selected_bg"]

    def test_transparency_button_uses_sombra_pink(self):
        """Test button transparency uses Sombra pink."""
        assert "233, 69, 96" in TRANSPARENCY["button_bg"]
        assert "233, 69, 96" in TRANSPARENCY["button_bg_hover"]

    def test_transparency_scrollbar_uses_sombra_pink(self):
        """Test scrollbar transparency uses Sombra pink."""
        assert "233, 69, 96" in TRANSPARENCY["scrollbar"]
        assert "233, 69, 96" in TRANSPARENCY["scrollbar_hover"]
