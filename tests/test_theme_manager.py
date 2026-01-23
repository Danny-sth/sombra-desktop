"""Unit tests for ThemeManager class.

Tests verify:
- Theme initialization and application
- Dark/Light theme toggle
- Glassmorphism effects (blur, transparency)
- Color utility methods
- Shadow and radius helpers
- Style generation
- Wayland compatibility considerations
"""


from PySide6.QtWidgets import QWidget

from sombra.themes.colors import (
    BLUR,
    BORDER_RADIUS,
    DARK_PALETTE,
    LIGHT_PALETTE,
    SHADOWS,
    SOMBRA_PRIMARY,
    SOMBRA_PRIMARY_DARK,
    SOMBRA_PRIMARY_LIGHT,
    SOMBRA_PRIMARY_MUTED,
    TRANSPARENCY,
)
from sombra.themes.theme_manager import (
    ThemeManager,
    get_theme_manager,
    init_theme_manager,
)


class TestThemeManagerInitialization:
    """Tests for ThemeManager initialization."""

    def test_theme_manager_init_with_app(self, qtbot, qapp):
        """Test ThemeManager initializes with QApplication."""
        manager = ThemeManager(qapp)
        assert manager._app == qapp

    def test_theme_manager_default_theme_is_dark(self, qtbot, qapp):
        """Test default theme is dark."""
        manager = ThemeManager(qapp)
        assert manager._current_theme == "dark"

    def test_theme_manager_current_theme_property(self, qtbot, qapp):
        """Test current_theme property returns correct value."""
        manager = ThemeManager(qapp)
        assert manager.current_theme == "dark"

    def test_theme_manager_is_dark_property(self, qtbot, qapp):
        """Test is_dark property returns True for dark theme."""
        manager = ThemeManager(qapp)
        assert manager.is_dark is True


class TestThemeManagerThemeApplication:
    """Tests for theme application."""

    def test_apply_theme_dark(self, qtbot, qapp):
        """Test applying dark theme."""
        manager = ThemeManager(qapp)
        manager.apply_theme("dark")
        assert manager._current_theme == "dark"

    def test_apply_theme_light(self, qtbot, qapp):
        """Test applying light theme."""
        manager = ThemeManager(qapp)
        manager.apply_theme("light")
        assert manager._current_theme == "light"

    def test_apply_theme_invalid_defaults_to_dark(self, qtbot, qapp):
        """Test applying invalid theme defaults to dark."""
        manager = ThemeManager(qapp)
        manager.apply_theme("invalid_theme")
        assert manager._current_theme == "dark"

    def test_toggle_theme_from_dark_to_light(self, qtbot, qapp):
        """Test toggling from dark to light theme."""
        manager = ThemeManager(qapp)
        manager._current_theme = "dark"
        new_theme = manager.toggle_theme()
        assert new_theme == "light"
        assert manager._current_theme == "light"

    def test_toggle_theme_from_light_to_dark(self, qtbot, qapp):
        """Test toggling from light to dark theme."""
        manager = ThemeManager(qapp)
        manager._current_theme = "light"
        new_theme = manager.toggle_theme()
        assert new_theme == "dark"
        assert manager._current_theme == "dark"


class TestThemeManagerPalette:
    """Tests for color palette access."""

    def test_current_palette_returns_dark_palette(self, qtbot, qapp):
        """Test current_palette returns DARK_PALETTE for dark theme."""
        manager = ThemeManager(qapp)
        manager._current_theme = "dark"
        assert manager.current_palette == DARK_PALETTE

    def test_current_palette_returns_light_palette(self, qtbot, qapp):
        """Test current_palette returns LIGHT_PALETTE for light theme."""
        manager = ThemeManager(qapp)
        manager._current_theme = "light"
        assert manager.current_palette == LIGHT_PALETTE

    def test_get_color_returns_palette_color(self, qtbot, qapp):
        """Test get_color returns correct color from palette."""
        manager = ThemeManager(qapp)
        manager._current_theme = "dark"
        color = manager.get_color("accent_primary")
        assert color == SOMBRA_PRIMARY

    def test_get_color_returns_default_for_invalid_key(self, qtbot, qapp):
        """Test get_color returns default for invalid key."""
        manager = ThemeManager(qapp)
        color = manager.get_color("nonexistent_key")
        assert color == "#000000"


class TestThemeManagerTransparency:
    """Tests for glassmorphism transparency helpers."""

    def test_get_transparency_returns_value(self, qtbot, qapp):
        """Test get_transparency returns correct value."""
        result = ThemeManager.get_transparency("panel_bg")
        assert result == TRANSPARENCY["panel_bg"]

    def test_get_transparency_for_card_bg(self, qtbot, qapp):
        """Test get_transparency for card background."""
        result = ThemeManager.get_transparency("card_bg")
        assert result == TRANSPARENCY["card_bg"]

    def test_get_transparency_for_dialog_bg(self, qtbot, qapp):
        """Test get_transparency for dialog background."""
        result = ThemeManager.get_transparency("dialog_bg")
        assert result == TRANSPARENCY["dialog_bg"]

    def test_get_transparency_for_input_bg(self, qtbot, qapp):
        """Test get_transparency for input background."""
        result = ThemeManager.get_transparency("input_bg")
        assert result == TRANSPARENCY["input_bg"]

    def test_get_transparency_defaults_to_panel_bg(self, qtbot, qapp):
        """Test get_transparency defaults to panel_bg for invalid key."""
        result = ThemeManager.get_transparency("invalid_key")
        assert result == TRANSPARENCY["panel_bg"]


class TestThemeManagerBlur:
    """Tests for blur effect helpers."""

    def test_get_blur_value_default(self, qtbot, qapp):
        """Test get_blur_value returns medium by default."""
        result = ThemeManager.get_blur_value()
        assert result == BLUR["md"]

    def test_get_blur_value_small(self, qtbot, qapp):
        """Test get_blur_value for small blur."""
        result = ThemeManager.get_blur_value("sm")
        assert result == BLUR["sm"]

    def test_get_blur_value_large(self, qtbot, qapp):
        """Test get_blur_value for large blur."""
        result = ThemeManager.get_blur_value("lg")
        assert result == BLUR["lg"]

    def test_get_blur_value_extra_large(self, qtbot, qapp):
        """Test get_blur_value for extra large blur."""
        result = ThemeManager.get_blur_value("xl")
        assert result == BLUR["xl"]

    def test_create_blur_effect_returns_effect(self, qtbot, qapp):
        """Test create_blur_effect returns QGraphicsBlurEffect."""
        from PySide6.QtWidgets import QGraphicsBlurEffect
        effect = ThemeManager.create_blur_effect(10.0)
        assert isinstance(effect, QGraphicsBlurEffect)
        assert effect.blurRadius() == 10.0

    def test_create_blur_effect_custom_radius(self, qtbot, qapp):
        """Test create_blur_effect with custom radius."""
        effect = ThemeManager.create_blur_effect(8.0)
        assert effect.blurRadius() == 8.0


class TestThemeManagerGlassmorphism:
    """Tests for glassmorphism application."""

    def test_apply_glassmorphism_sets_stylesheet(self, qtbot, qapp):
        """Test apply_glassmorphism sets widget stylesheet."""
        widget = QWidget()
        qtbot.addWidget(widget)

        ThemeManager.apply_glassmorphism(widget, blur_radius=10.0, bg_key="panel_bg")

        stylesheet = widget.styleSheet()
        assert "background-color:" in stylesheet
        assert "border:" in stylesheet
        assert "border-radius:" in stylesheet

    def test_apply_glassmorphism_uses_transparency(self, qtbot, qapp):
        """Test apply_glassmorphism uses correct transparency."""
        widget = QWidget()
        qtbot.addWidget(widget)

        ThemeManager.apply_glassmorphism(widget, bg_key="card_bg")

        stylesheet = widget.styleSheet()
        # Should use card_bg transparency
        assert "rgba" in stylesheet


class TestThemeManagerShadow:
    """Tests for shadow helpers."""

    def test_get_shadow_default(self, qtbot, qapp):
        """Test get_shadow returns medium by default."""
        result = ThemeManager.get_shadow()
        assert result == SHADOWS["md"]

    def test_get_shadow_card(self, qtbot, qapp):
        """Test get_shadow for card shadow."""
        result = ThemeManager.get_shadow("card")
        assert result == SHADOWS["card"]

    def test_get_shadow_card_hover(self, qtbot, qapp):
        """Test get_shadow for card hover shadow."""
        result = ThemeManager.get_shadow("card_hover")
        assert result == SHADOWS["card_hover"]

    def test_get_shadow_button(self, qtbot, qapp):
        """Test get_shadow for button shadow."""
        result = ThemeManager.get_shadow("button")
        assert result == SHADOWS["button"]

    def test_get_shadow_glow(self, qtbot, qapp):
        """Test get_shadow for glow effects."""
        result = ThemeManager.get_shadow("glow_md")
        assert result == SHADOWS["glow_md"]


class TestThemeManagerRadius:
    """Tests for border radius helpers."""

    def test_get_radius_default(self, qtbot, qapp):
        """Test get_radius returns medium by default."""
        result = ThemeManager.get_radius()
        assert result == BORDER_RADIUS["md"]

    def test_get_radius_small(self, qtbot, qapp):
        """Test get_radius for small radius."""
        result = ThemeManager.get_radius("sm")
        assert result == BORDER_RADIUS["sm"]

    def test_get_radius_large(self, qtbot, qapp):
        """Test get_radius for large radius (cards)."""
        result = ThemeManager.get_radius("lg")
        assert result == BORDER_RADIUS["lg"]

    def test_get_radius_xl(self, qtbot, qapp):
        """Test get_radius for extra large radius (panels)."""
        result = ThemeManager.get_radius("xl")
        assert result == BORDER_RADIUS["xl"]

    def test_get_radius_full(self, qtbot, qapp):
        """Test get_radius for full radius (pills)."""
        result = ThemeManager.get_radius("full")
        assert result == BORDER_RADIUS["full"]


class TestThemeManagerColorUtilities:
    """Tests for color utility methods."""

    def test_hex_to_rgba_default_alpha(self, qtbot, qapp):
        """Test hex_to_rgba with default alpha."""
        result = ThemeManager.hex_to_rgba("#e94560")
        assert result == "rgba(233, 69, 96, 1.0)"

    def test_hex_to_rgba_custom_alpha(self, qtbot, qapp):
        """Test hex_to_rgba with custom alpha."""
        result = ThemeManager.hex_to_rgba("#e94560", 0.5)
        assert result == "rgba(233, 69, 96, 0.5)"

    def test_get_primary_color_default(self, qtbot, qapp):
        """Test get_primary_color returns default SOMBRA_PRIMARY."""
        result = ThemeManager.get_primary_color()
        assert result == SOMBRA_PRIMARY

    def test_get_primary_color_light(self, qtbot, qapp):
        """Test get_primary_color returns light variant."""
        result = ThemeManager.get_primary_color("light")
        assert result == SOMBRA_PRIMARY_LIGHT

    def test_get_primary_color_dark(self, qtbot, qapp):
        """Test get_primary_color returns dark variant."""
        result = ThemeManager.get_primary_color("dark")
        assert result == SOMBRA_PRIMARY_DARK

    def test_get_primary_color_muted(self, qtbot, qapp):
        """Test get_primary_color returns muted variant."""
        result = ThemeManager.get_primary_color("muted")
        assert result == SOMBRA_PRIMARY_MUTED

    def test_get_primary_color_invalid_defaults(self, qtbot, qapp):
        """Test get_primary_color defaults to primary for invalid variant."""
        result = ThemeManager.get_primary_color("invalid")
        assert result == SOMBRA_PRIMARY


class TestThemeManagerStyleGeneration:
    """Tests for style generation helpers."""

    def test_generate_card_style_includes_background(self, qtbot, qapp):
        """Test generate_card_style includes background color."""
        style = ThemeManager.generate_card_style()
        assert "background-color:" in style

    def test_generate_card_style_includes_border(self, qtbot, qapp):
        """Test generate_card_style includes border."""
        style = ThemeManager.generate_card_style()
        assert "border:" in style

    def test_generate_card_style_includes_radius(self, qtbot, qapp):
        """Test generate_card_style includes border-radius."""
        style = ThemeManager.generate_card_style()
        assert "border-radius:" in style

    def test_generate_card_style_with_hover(self, qtbot, qapp):
        """Test generate_card_style includes hover state."""
        style = ThemeManager.generate_card_style(include_hover=True)
        assert ":hover" in style

    def test_generate_card_style_without_hover(self, qtbot, qapp):
        """Test generate_card_style without hover state."""
        style = ThemeManager.generate_card_style(include_hover=False)
        assert ":hover" not in style

    def test_generate_button_style_primary(self, qtbot, qapp):
        """Test generate_button_style for primary variant."""
        style = ThemeManager.generate_button_style("primary")
        assert SOMBRA_PRIMARY in style
        assert "background-color:" in style

    def test_generate_button_style_secondary(self, qtbot, qapp):
        """Test generate_button_style for secondary variant."""
        style = ThemeManager.generate_button_style("secondary")
        assert "transparent" in style
        assert "border:" in style

    def test_generate_button_style_ghost(self, qtbot, qapp):
        """Test generate_button_style for ghost variant."""
        style = ThemeManager.generate_button_style("ghost")
        assert "transparent" in style
        assert "border: none" in style


class TestThemeManagerCustomCSS:
    """Tests for custom CSS content."""

    def test_custom_css_includes_button_styles(self, qtbot, qapp):
        """Test CUSTOM_CSS includes button styling."""
        assert "PrimaryPushButton" in ThemeManager.CUSTOM_CSS
        assert "PushButton" in ThemeManager.CUSTOM_CSS
        assert "TransparentPushButton" in ThemeManager.CUSTOM_CSS

    def test_custom_css_includes_voice_button(self, qtbot, qapp):
        """Test CUSTOM_CSS includes voice button styling."""
        assert "voiceButton" in ThemeManager.CUSTOM_CSS

    def test_custom_css_includes_input_styles(self, qtbot, qapp):
        """Test CUSTOM_CSS includes input field styling."""
        assert "QLineEdit" in ThemeManager.CUSTOM_CSS
        assert "QTextEdit" in ThemeManager.CUSTOM_CSS

    def test_custom_css_includes_card_styles(self, qtbot, qapp):
        """Test CUSTOM_CSS includes card styling."""
        assert "SimpleCardWidget" in ThemeManager.CUSTOM_CSS
        assert "CardWidget" in ThemeManager.CUSTOM_CSS

    def test_custom_css_includes_dialog_styles(self, qtbot, qapp):
        """Test CUSTOM_CSS includes dialog styling."""
        assert "MessageBox" in ThemeManager.CUSTOM_CSS
        assert "Dialog" in ThemeManager.CUSTOM_CSS

    def test_custom_css_includes_scrollbar_styles(self, qtbot, qapp):
        """Test CUSTOM_CSS includes scrollbar styling."""
        assert "QScrollBar" in ThemeManager.CUSTOM_CSS

    def test_custom_css_uses_sombra_pink_rgb(self, qtbot, qapp):
        """Test CUSTOM_CSS uses Sombra pink RGB values."""
        assert "233, 69, 96" in ThemeManager.CUSTOM_CSS

    def test_custom_css_includes_hover_states(self, qtbot, qapp):
        """Test CUSTOM_CSS includes hover states."""
        assert ":hover" in ThemeManager.CUSTOM_CSS

    def test_custom_css_includes_pressed_states(self, qtbot, qapp):
        """Test CUSTOM_CSS includes pressed states."""
        assert ":pressed" in ThemeManager.CUSTOM_CSS

    def test_custom_css_includes_focus_states(self, qtbot, qapp):
        """Test CUSTOM_CSS includes focus states."""
        assert ":focus" in ThemeManager.CUSTOM_CSS

    def test_custom_css_includes_disabled_states(self, qtbot, qapp):
        """Test CUSTOM_CSS includes disabled states."""
        assert ":disabled" in ThemeManager.CUSTOM_CSS


class TestThemeManagerGlobalInstance:
    """Tests for global ThemeManager instance management."""

    def test_init_theme_manager_creates_instance(self, qtbot, qapp):
        """Test init_theme_manager creates and returns instance."""
        manager = init_theme_manager(qapp)
        assert isinstance(manager, ThemeManager)

    def test_get_theme_manager_returns_initialized_instance(self, qtbot, qapp):
        """Test get_theme_manager returns initialized instance."""
        init_theme_manager(qapp)
        manager = get_theme_manager()
        assert isinstance(manager, ThemeManager)


class TestThemeMapConfiguration:
    """Tests for theme map configuration."""

    def test_theme_map_has_dark(self, qtbot, qapp):
        """Test THEME_MAP has dark theme."""
        assert "dark" in ThemeManager.THEME_MAP

    def test_theme_map_has_light(self, qtbot, qapp):
        """Test THEME_MAP has light theme."""
        assert "light" in ThemeManager.THEME_MAP

    def test_theme_map_dark_uses_xml(self, qtbot, qapp):
        """Test dark theme maps to XML file."""
        assert ThemeManager.THEME_MAP["dark"].endswith(".xml")

    def test_theme_map_light_uses_xml(self, qtbot, qapp):
        """Test light theme maps to XML file."""
        assert ThemeManager.THEME_MAP["light"].endswith(".xml")


class TestThemeManagerBrandConstants:
    """Tests for brand color constants in ThemeManager."""

    def test_primary_constant(self, qtbot, qapp):
        """Test _PRIMARY matches SOMBRA_PRIMARY."""
        assert ThemeManager._PRIMARY == SOMBRA_PRIMARY

    def test_primary_light_constant(self, qtbot, qapp):
        """Test _PRIMARY_LIGHT matches SOMBRA_PRIMARY_LIGHT."""
        assert ThemeManager._PRIMARY_LIGHT == SOMBRA_PRIMARY_LIGHT

    def test_primary_dark_constant(self, qtbot, qapp):
        """Test _PRIMARY_DARK matches SOMBRA_PRIMARY_DARK."""
        assert ThemeManager._PRIMARY_DARK == SOMBRA_PRIMARY_DARK

    def test_primary_rgb_constant(self, qtbot, qapp):
        """Test _PRIMARY_RGB is correct."""
        assert ThemeManager._PRIMARY_RGB == "233, 69, 96"

    def test_primary_light_rgb_constant(self, qtbot, qapp):
        """Test _PRIMARY_LIGHT_RGB is correct."""
        assert ThemeManager._PRIMARY_LIGHT_RGB == "255, 107, 138"


class TestWaylandCompatibility:
    """Tests for Wayland-related considerations.

    Note: Qt blur effects (QGraphicsBlurEffect) apply to widget content,
    not to the window background. True backdrop blur on Wayland requires
    compositor support. These tests verify the fallback behavior works.
    """

    def test_blur_effect_can_be_created(self, qtbot, qapp):
        """Test blur effect can be created (works on all platforms)."""
        effect = ThemeManager.create_blur_effect(12.0)
        assert effect is not None
        assert effect.blurRadius() == 12.0

    def test_glassmorphism_applies_without_error(self, qtbot, qapp):
        """Test glassmorphism applies without error on any platform."""
        widget = QWidget()
        qtbot.addWidget(widget)

        # Should not raise any exception
        ThemeManager.apply_glassmorphism(widget, blur_radius=12.0)

        # Widget should have a stylesheet
        assert widget.styleSheet() != ""

    def test_transparency_values_are_valid_for_wayland(self, qtbot, qapp):
        """Test transparency values work regardless of compositor."""
        # All transparency values should be valid rgba strings
        for key in TRANSPARENCY:
            value = ThemeManager.get_transparency(key)
            assert "rgba" in value
