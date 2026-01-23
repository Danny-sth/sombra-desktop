"""Unit tests for SciFiTheme class from ui/styles/theme.py.

Tests verify:
- SciFiTheme constants match colors.py definitions
- Chat bubble styles with Sombra branding
- Button styles (primary, secondary, ghost)
- Card styles with shadows
- Panel and dialog styles with glassmorphism
- Scrollbar styles
- Helper methods
"""


from sombra.themes.colors import (
    BLUR,
    BORDER_RADIUS,
    DARK_PALETTE,
    SHADOWS,
    SOMBRA_CYAN,
    SOMBRA_PRIMARY,
    SOMBRA_PRIMARY_DARK,
    SOMBRA_PRIMARY_LIGHT,
    SOMBRA_PRIMARY_MUTED,
    SOMBRA_PURPLE,
    TRANSPARENCY,
)
from sombra.ui.styles.theme import SciFiTheme


class TestSciFiThemePrimaryColors:
    """Tests for SciFiTheme primary color constants."""

    def test_primary_matches_sombra_primary(self):
        """Test PRIMARY is SOMBRA_PRIMARY (#e94560)."""
        assert SciFiTheme.PRIMARY == SOMBRA_PRIMARY
        assert SciFiTheme.PRIMARY == "#e94560"

    def test_primary_rgb_is_correct(self):
        """Test PRIMARY_RGB is correct."""
        assert SciFiTheme.PRIMARY_RGB == "233, 69, 96"

    def test_primary_light_matches(self):
        """Test PRIMARY_LIGHT matches SOMBRA_PRIMARY_LIGHT."""
        assert SciFiTheme.PRIMARY_LIGHT == SOMBRA_PRIMARY_LIGHT
        assert SciFiTheme.PRIMARY_LIGHT == "#ff6b8a"

    def test_primary_dark_matches(self):
        """Test PRIMARY_DARK matches SOMBRA_PRIMARY_DARK."""
        assert SciFiTheme.PRIMARY_DARK == SOMBRA_PRIMARY_DARK
        assert SciFiTheme.PRIMARY_DARK == "#c73e54"

    def test_primary_muted_matches(self):
        """Test PRIMARY_MUTED matches SOMBRA_PRIMARY_MUTED."""
        assert SciFiTheme.PRIMARY_MUTED == SOMBRA_PRIMARY_MUTED
        assert SciFiTheme.PRIMARY_MUTED == "#a63346"


class TestSciFiThemeSecondaryColors:
    """Tests for SciFiTheme secondary color constants."""

    def test_secondary_matches_sombra_purple(self):
        """Test SECONDARY is SOMBRA_PURPLE."""
        assert SciFiTheme.SECONDARY == SOMBRA_PURPLE
        assert SciFiTheme.SECONDARY == "#533483"

    def test_accent_cyan_matches_sombra_cyan(self):
        """Test ACCENT_CYAN is SOMBRA_CYAN."""
        assert SciFiTheme.ACCENT_CYAN == SOMBRA_CYAN
        assert SciFiTheme.ACCENT_CYAN == "#00d9ff"

    def test_legacy_aliases_exist(self):
        """Test legacy aliases for backward compatibility."""
        assert SciFiTheme.CYAN == SOMBRA_CYAN
        assert SciFiTheme.MAGENTA == SciFiTheme.PRIMARY
        assert SciFiTheme.PURPLE == SOMBRA_PURPLE


class TestSciFiThemeBackgroundColors:
    """Tests for SciFiTheme background color constants."""

    def test_bg_dark_from_palette(self):
        """Test BG_DARK matches DARK_PALETTE."""
        assert SciFiTheme.BG_DARK == DARK_PALETTE["bg_sunken"]

    def test_bg_panel_from_palette(self):
        """Test BG_PANEL matches DARK_PALETTE."""
        assert SciFiTheme.BG_PANEL == DARK_PALETTE["bg_primary"]

    def test_bg_card_from_palette(self):
        """Test BG_CARD matches DARK_PALETTE."""
        assert SciFiTheme.BG_CARD == DARK_PALETTE["bg_secondary"]

    def test_bg_elevated_from_palette(self):
        """Test BG_ELEVATED matches DARK_PALETTE."""
        assert SciFiTheme.BG_ELEVATED == DARK_PALETTE["bg_elevated"]

    def test_bg_input_from_palette(self):
        """Test BG_INPUT matches DARK_PALETTE."""
        assert SciFiTheme.BG_INPUT == DARK_PALETTE["bg_input"]


class TestSciFiThemeTextColors:
    """Tests for SciFiTheme text color constants."""

    def test_text_primary_from_palette(self):
        """Test TEXT_PRIMARY matches DARK_PALETTE."""
        assert SciFiTheme.TEXT_PRIMARY == DARK_PALETTE["text_primary"]

    def test_text_secondary_from_palette(self):
        """Test TEXT_SECONDARY matches DARK_PALETTE."""
        assert SciFiTheme.TEXT_SECONDARY == DARK_PALETTE["text_secondary"]

    def test_text_muted_from_palette(self):
        """Test TEXT_MUTED matches DARK_PALETTE."""
        assert SciFiTheme.TEXT_MUTED == DARK_PALETTE["text_disabled"]

    def test_text_placeholder_from_palette(self):
        """Test TEXT_PLACEHOLDER matches DARK_PALETTE."""
        assert SciFiTheme.TEXT_PLACEHOLDER == DARK_PALETTE["text_placeholder"]


class TestSciFiThemeGlassmorphismConstants:
    """Tests for glassmorphism constants."""

    def test_glass_opacity_values(self):
        """Test glass opacity constants."""
        assert SciFiTheme.GLASS_OPACITY == 0.10
        assert SciFiTheme.GLASS_OPACITY_HOVER == 0.15
        assert SciFiTheme.GLASS_OPACITY_ACTIVE == 0.20

    def test_border_opacity_values(self):
        """Test border opacity constants."""
        assert SciFiTheme.BORDER_OPACITY == 0.25
        assert SciFiTheme.BORDER_OPACITY_HOVER == 0.40
        assert SciFiTheme.BORDER_OPACITY_FOCUS == 0.55

    def test_panel_bg_from_transparency(self):
        """Test PANEL_BG matches TRANSPARENCY."""
        assert SciFiTheme.PANEL_BG == TRANSPARENCY["panel_bg"]

    def test_card_bg_from_transparency(self):
        """Test CARD_BG matches TRANSPARENCY."""
        assert SciFiTheme.CARD_BG == TRANSPARENCY["card_bg"]

    def test_dialog_bg_from_transparency(self):
        """Test DIALOG_BG matches TRANSPARENCY."""
        assert SciFiTheme.DIALOG_BG == TRANSPARENCY["dialog_bg"]

    def test_input_bg_from_transparency(self):
        """Test INPUT_BG matches TRANSPARENCY."""
        assert SciFiTheme.INPUT_BG == TRANSPARENCY["input_bg"]


class TestSciFiThemeBlurConstants:
    """Tests for blur constants."""

    def test_blur_sm_from_blur(self):
        """Test BLUR_SM matches BLUR."""
        assert SciFiTheme.BLUR_SM == BLUR["sm"]

    def test_blur_md_from_blur(self):
        """Test BLUR_MD matches BLUR."""
        assert SciFiTheme.BLUR_MD == BLUR["md"]

    def test_blur_lg_from_blur(self):
        """Test BLUR_LG matches BLUR."""
        assert SciFiTheme.BLUR_LG == BLUR["lg"]

    def test_blur_xl_from_blur(self):
        """Test BLUR_XL matches BLUR."""
        assert SciFiTheme.BLUR_XL == BLUR["xl"]


class TestSciFiThemeBorderRadiusConstants:
    """Tests for border radius constants."""

    def test_radius_sm_from_border_radius(self):
        """Test RADIUS_SM matches BORDER_RADIUS."""
        assert SciFiTheme.RADIUS_SM == BORDER_RADIUS["sm"]

    def test_radius_md_from_border_radius(self):
        """Test RADIUS_MD matches BORDER_RADIUS."""
        assert SciFiTheme.RADIUS_MD == BORDER_RADIUS["md"]

    def test_radius_lg_from_border_radius(self):
        """Test RADIUS_LG matches BORDER_RADIUS."""
        assert SciFiTheme.RADIUS_LG == BORDER_RADIUS["lg"]

    def test_radius_xl_from_border_radius(self):
        """Test RADIUS_XL matches BORDER_RADIUS."""
        assert SciFiTheme.RADIUS_XL == BORDER_RADIUS["xl"]

    def test_radius_full_from_border_radius(self):
        """Test RADIUS_FULL matches BORDER_RADIUS."""
        assert SciFiTheme.RADIUS_FULL == BORDER_RADIUS["full"]


class TestSciFiThemeShadowConstants:
    """Tests for shadow constants."""

    def test_shadow_sm_from_shadows(self):
        """Test SHADOW_SM matches SHADOWS."""
        assert SciFiTheme.SHADOW_SM == SHADOWS["sm"]

    def test_shadow_md_from_shadows(self):
        """Test SHADOW_MD matches SHADOWS."""
        assert SciFiTheme.SHADOW_MD == SHADOWS["md"]

    def test_shadow_lg_from_shadows(self):
        """Test SHADOW_LG matches SHADOWS."""
        assert SciFiTheme.SHADOW_LG == SHADOWS["lg"]

    def test_shadow_card_from_shadows(self):
        """Test SHADOW_CARD matches SHADOWS."""
        assert SciFiTheme.SHADOW_CARD == SHADOWS["card"]

    def test_shadow_card_hover_from_shadows(self):
        """Test SHADOW_CARD_HOVER matches SHADOWS."""
        assert SciFiTheme.SHADOW_CARD_HOVER == SHADOWS["card_hover"]

    def test_shadow_button_from_shadows(self):
        """Test SHADOW_BUTTON matches SHADOWS."""
        assert SciFiTheme.SHADOW_BUTTON == SHADOWS["button"]

    def test_shadow_glow_md_from_shadows(self):
        """Test SHADOW_GLOW_MD matches SHADOWS."""
        assert SciFiTheme.SHADOW_GLOW_MD == SHADOWS["glow_md"]


class TestSciFiThemeStatusColors:
    """Tests for status color constants."""

    def test_success_from_palette(self):
        """Test SUCCESS matches DARK_PALETTE."""
        assert SciFiTheme.SUCCESS == DARK_PALETTE["success"]

    def test_warning_from_palette(self):
        """Test WARNING matches DARK_PALETTE."""
        assert SciFiTheme.WARNING == DARK_PALETTE["warning"]

    def test_error_from_palette(self):
        """Test ERROR matches DARK_PALETTE."""
        assert SciFiTheme.ERROR == DARK_PALETTE["error"]

    def test_info_uses_cyan(self):
        """Test INFO uses SOMBRA_CYAN."""
        assert SciFiTheme.INFO == SOMBRA_CYAN


class TestSciFiThemeChatBubbleStyles:
    """Tests for chat bubble style strings."""

    def test_sombra_bubble_has_gradient(self):
        """Test SOMBRA_BUBBLE has gradient background."""
        assert "qlineargradient" in SciFiTheme.SOMBRA_BUBBLE

    def test_sombra_bubble_uses_primary_rgb(self):
        """Test SOMBRA_BUBBLE uses PRIMARY_RGB."""
        assert SciFiTheme.PRIMARY_RGB in SciFiTheme.SOMBRA_BUBBLE

    def test_sombra_bubble_has_hover_state(self):
        """Test SOMBRA_BUBBLE has hover state."""
        assert ":hover" in SciFiTheme.SOMBRA_BUBBLE

    def test_sombra_bubble_has_border_radius(self):
        """Test SOMBRA_BUBBLE has border radius."""
        assert "border-radius:" in SciFiTheme.SOMBRA_BUBBLE

    def test_user_bubble_has_gradient(self):
        """Test USER_BUBBLE has gradient background."""
        assert "qlineargradient" in SciFiTheme.USER_BUBBLE

    def test_user_bubble_uses_lighter_pink(self):
        """Test USER_BUBBLE uses PRIMARY_LIGHT_RGB."""
        assert SciFiTheme.PRIMARY_LIGHT_RGB in SciFiTheme.USER_BUBBLE

    def test_user_bubble_has_hover_state(self):
        """Test USER_BUBBLE has hover state."""
        assert ":hover" in SciFiTheme.USER_BUBBLE

    def test_thinking_bubble_uses_secondary(self):
        """Test THINKING_BUBBLE uses SECONDARY_RGB."""
        assert SciFiTheme.SECONDARY_RGB in SciFiTheme.THINKING_BUBBLE

    def test_streaming_bubble_uses_primary(self):
        """Test STREAMING_BUBBLE uses PRIMARY_RGB."""
        assert SciFiTheme.PRIMARY_RGB in SciFiTheme.STREAMING_BUBBLE


class TestSciFiThemeButtonStyles:
    """Tests for button style strings."""

    def test_button_primary_uses_primary_color(self):
        """Test BUTTON_PRIMARY uses PRIMARY color."""
        assert SciFiTheme.PRIMARY in SciFiTheme.BUTTON_PRIMARY

    def test_button_primary_has_hover_state(self):
        """Test BUTTON_PRIMARY has hover state."""
        assert ":hover" in SciFiTheme.BUTTON_PRIMARY

    def test_button_primary_hover_uses_light(self):
        """Test BUTTON_PRIMARY hover uses PRIMARY_LIGHT."""
        assert SciFiTheme.PRIMARY_LIGHT in SciFiTheme.BUTTON_PRIMARY

    def test_button_primary_has_pressed_state(self):
        """Test BUTTON_PRIMARY has pressed state."""
        assert ":pressed" in SciFiTheme.BUTTON_PRIMARY

    def test_button_primary_pressed_uses_dark(self):
        """Test BUTTON_PRIMARY pressed uses PRIMARY_DARK."""
        assert SciFiTheme.PRIMARY_DARK in SciFiTheme.BUTTON_PRIMARY

    def test_button_primary_has_disabled_state(self):
        """Test BUTTON_PRIMARY has disabled state."""
        assert ":disabled" in SciFiTheme.BUTTON_PRIMARY

    def test_button_secondary_is_transparent(self):
        """Test BUTTON_SECONDARY has transparent background."""
        assert "transparent" in SciFiTheme.BUTTON_SECONDARY

    def test_button_secondary_has_border(self):
        """Test BUTTON_SECONDARY has border."""
        assert "border:" in SciFiTheme.BUTTON_SECONDARY

    def test_button_secondary_has_hover_state(self):
        """Test BUTTON_SECONDARY has hover state."""
        assert ":hover" in SciFiTheme.BUTTON_SECONDARY

    def test_button_ghost_is_transparent(self):
        """Test BUTTON_GHOST has transparent background."""
        assert "transparent" in SciFiTheme.BUTTON_GHOST

    def test_button_ghost_has_no_border(self):
        """Test BUTTON_GHOST has no border."""
        assert "border: none" in SciFiTheme.BUTTON_GHOST

    def test_button_ghost_has_hover_state(self):
        """Test BUTTON_GHOST has hover state."""
        assert ":hover" in SciFiTheme.BUTTON_GHOST


class TestSciFiThemeCardStyles:
    """Tests for card style strings."""

    def test_card_base_has_background(self):
        """Test CARD_BASE has background color."""
        assert "background-color:" in SciFiTheme.CARD_BASE

    def test_card_base_uses_card_bg(self):
        """Test CARD_BASE uses CARD_BG transparency."""
        assert SciFiTheme.CARD_BG in SciFiTheme.CARD_BASE

    def test_card_base_has_border(self):
        """Test CARD_BASE has border."""
        assert "border:" in SciFiTheme.CARD_BASE

    def test_card_base_has_border_radius(self):
        """Test CARD_BASE has border radius."""
        assert "border-radius:" in SciFiTheme.CARD_BASE
        assert SciFiTheme.RADIUS_LG in SciFiTheme.CARD_BASE

    def test_card_base_has_hover_state(self):
        """Test CARD_BASE has hover state."""
        assert ":hover" in SciFiTheme.CARD_BASE

    def test_card_hover_uses_card_bg_hover(self):
        """Test card hover uses CARD_BG_HOVER."""
        assert SciFiTheme.CARD_BG_HOVER in SciFiTheme.CARD_BASE


class TestSciFiThemeStatusCardStyles:
    """Tests for status card style strings."""

    def test_status_connected_uses_success(self):
        """Test STATUS_CONNECTED uses SUCCESS_RGB."""
        assert SciFiTheme.SUCCESS_RGB in SciFiTheme.STATUS_CONNECTED

    def test_status_connected_has_hover(self):
        """Test STATUS_CONNECTED has hover state."""
        assert ":hover" in SciFiTheme.STATUS_CONNECTED

    def test_status_disconnected_uses_error(self):
        """Test STATUS_DISCONNECTED uses ERROR_RGB."""
        assert SciFiTheme.ERROR_RGB in SciFiTheme.STATUS_DISCONNECTED

    def test_status_warning_uses_warning(self):
        """Test STATUS_WARNING uses WARNING_RGB."""
        assert SciFiTheme.WARNING_RGB in SciFiTheme.STATUS_WARNING


class TestSciFiThemePanelStyles:
    """Tests for panel and dialog style strings."""

    def test_panel_glass_uses_panel_bg(self):
        """Test PANEL_GLASS uses PANEL_BG."""
        assert SciFiTheme.PANEL_BG in SciFiTheme.PANEL_GLASS

    def test_panel_glass_has_border(self):
        """Test PANEL_GLASS has border."""
        assert "border:" in SciFiTheme.PANEL_GLASS

    def test_panel_glass_uses_primary_rgb(self):
        """Test PANEL_GLASS uses PRIMARY_RGB for border."""
        assert SciFiTheme.PRIMARY_RGB in SciFiTheme.PANEL_GLASS

    def test_dialog_glass_uses_dialog_bg(self):
        """Test DIALOG_GLASS uses DIALOG_BG."""
        assert SciFiTheme.DIALOG_BG in SciFiTheme.DIALOG_GLASS

    def test_dialog_glass_has_radius_xl(self):
        """Test DIALOG_GLASS has RADIUS_XL."""
        assert SciFiTheme.RADIUS_XL in SciFiTheme.DIALOG_GLASS


class TestSciFiThemeInputStyles:
    """Tests for input field style strings."""

    def test_input_field_uses_input_bg(self):
        """Test INPUT_FIELD uses INPUT_BG."""
        assert SciFiTheme.INPUT_BG in SciFiTheme.INPUT_FIELD

    def test_input_field_has_border(self):
        """Test INPUT_FIELD has border."""
        assert "border:" in SciFiTheme.INPUT_FIELD

    def test_input_field_has_hover_state(self):
        """Test INPUT_FIELD has hover state."""
        assert ":hover" in SciFiTheme.INPUT_FIELD

    def test_input_field_has_focus_state(self):
        """Test INPUT_FIELD has focus state."""
        assert ":focus" in SciFiTheme.INPUT_FIELD

    def test_input_field_focus_uses_input_bg_focus(self):
        """Test INPUT_FIELD focus uses INPUT_BG_FOCUS."""
        assert SciFiTheme.INPUT_BG_FOCUS in SciFiTheme.INPUT_FIELD


class TestSciFiThemeScrollbarStyles:
    """Tests for scrollbar style strings."""

    def test_scrollbar_has_vertical(self):
        """Test SCROLLBAR has vertical scrollbar styling."""
        assert "QScrollBar:vertical" in SciFiTheme.SCROLLBAR

    def test_scrollbar_has_horizontal(self):
        """Test SCROLLBAR has horizontal scrollbar styling."""
        assert "QScrollBar:horizontal" in SciFiTheme.SCROLLBAR

    def test_scrollbar_uses_primary_rgb(self):
        """Test SCROLLBAR uses PRIMARY_RGB."""
        assert SciFiTheme.PRIMARY_RGB in SciFiTheme.SCROLLBAR

    def test_scrollbar_has_handle_hover(self):
        """Test SCROLLBAR has handle hover state."""
        assert "::handle:vertical:hover" in SciFiTheme.SCROLLBAR


class TestSciFiThemeHelperMethods:
    """Tests for SciFiTheme helper methods."""

    def test_get_glow_shadow_default(self):
        """Test get_glow_shadow with default color."""
        result = SciFiTheme.get_glow_shadow()
        assert "border:" in result
        assert SciFiTheme.PRIMARY_RGB in result
        assert "0.4" in result

    def test_get_glow_shadow_custom_color(self):
        """Test get_glow_shadow with custom color."""
        result = SciFiTheme.get_glow_shadow("255, 0, 0")
        assert "255, 0, 0" in result

    def test_get_glow_shadow_custom_intensity(self):
        """Test get_glow_shadow with custom intensity."""
        result = SciFiTheme.get_glow_shadow(intensity=0.8)
        assert "0.8" in result

    def test_get_text_color_dark_theme(self):
        """Test get_text_color for dark theme."""
        result = SciFiTheme.get_text_color(is_dark=True)
        assert result == SciFiTheme.TEXT_PRIMARY

    def test_get_text_color_light_theme(self):
        """Test get_text_color for light theme."""
        result = SciFiTheme.get_text_color(is_dark=False)
        assert result == "#1a1a2e"

    def test_get_accent_gradient_default(self):
        """Test get_accent_gradient with default opacities."""
        result = SciFiTheme.get_accent_gradient()
        assert "qlineargradient" in result
        assert SciFiTheme.PRIMARY_RGB in result

    def test_get_accent_gradient_custom_opacity(self):
        """Test get_accent_gradient with custom opacities."""
        result = SciFiTheme.get_accent_gradient(0.20, 0.08)
        assert "0.2" in result or "0.20" in result
        assert "0.08" in result

    def test_get_card_style_returns_style(self):
        """Test get_card_style returns style string."""
        result = SciFiTheme.get_card_style()
        assert "SimpleCardWidget" in result
        assert "background-color:" in result

    def test_get_card_style_with_hover(self):
        """Test get_card_style with hover state."""
        result = SciFiTheme.get_card_style(hover=True)
        assert ":hover" in result

    def test_get_card_style_without_hover(self):
        """Test get_card_style without hover state."""
        result = SciFiTheme.get_card_style(hover=False)
        assert ":hover" not in result

    def test_get_card_style_custom_accent(self):
        """Test get_card_style with custom accent."""
        result = SciFiTheme.get_card_style(accent_rgb="255, 0, 0")
        assert "255, 0, 0" in result

    def test_get_button_style_primary(self):
        """Test get_button_style returns primary style."""
        result = SciFiTheme.get_button_style("primary")
        assert result == SciFiTheme.BUTTON_PRIMARY

    def test_get_button_style_secondary(self):
        """Test get_button_style returns secondary style."""
        result = SciFiTheme.get_button_style("secondary")
        assert result == SciFiTheme.BUTTON_SECONDARY

    def test_get_button_style_ghost(self):
        """Test get_button_style returns ghost style."""
        result = SciFiTheme.get_button_style("ghost")
        assert result == SciFiTheme.BUTTON_GHOST

    def test_get_button_style_invalid_defaults_to_primary(self):
        """Test get_button_style defaults to primary for invalid variant."""
        result = SciFiTheme.get_button_style("invalid")
        assert result == SciFiTheme.BUTTON_PRIMARY
