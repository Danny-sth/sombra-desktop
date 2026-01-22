"""Unit tests for ConnectionIndicator widget.

Tests verify:
- Connection state changes (connected/connecting/disconnected/error)
- Styling matches theme colors
- Widget structure correctness
- Signal emissions
- Animation behavior
- Public API methods
- Integration with SombraService status strings
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout

from sombra.ui.widgets.connection_indicator import (
    ConnectionIndicator,
    ConnectionState,
)
from sombra.themes.colors import DARK_PALETTE, LIGHT_PALETTE


class TestConnectionState:
    """Tests for ConnectionState enum."""

    def test_state_values(self):
        """Test that all state values are defined."""
        assert ConnectionState.CONNECTED.state_id == "connected"
        assert ConnectionState.CONNECTING.state_id == "connecting"
        assert ConnectionState.DISCONNECTED.state_id == "disconnected"
        assert ConnectionState.ERROR.state_id == "error"

    def test_state_labels(self):
        """Test that all states have user-friendly labels."""
        assert ConnectionState.CONNECTED.label == "Connected"
        assert ConnectionState.CONNECTING.label == "Connecting..."
        assert ConnectionState.DISCONNECTED.label == "Disconnected"
        assert ConnectionState.ERROR.label == "Error"

    def test_state_enum_count(self):
        """Test that we have exactly 4 connection states."""
        assert len(ConnectionState) == 4


class TestConnectionIndicatorCreation:
    """Tests for ConnectionIndicator widget creation."""

    def test_indicator_creation_default(self, qtbot):
        """Test indicator creates with default DISCONNECTED state."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        assert indicator._state == ConnectionState.DISCONNECTED

    def test_indicator_creation_compact_mode(self, qtbot):
        """Test indicator creates in compact mode."""
        indicator = ConnectionIndicator(compact=True)
        qtbot.addWidget(indicator)

        assert indicator._compact is True
        assert indicator._label.isHidden()

    def test_indicator_creation_normal_mode(self, qtbot):
        """Test indicator creates in normal mode (non-compact)."""
        indicator = ConnectionIndicator(compact=False)
        qtbot.addWidget(indicator)

        assert indicator._compact is False
        assert not indicator._label.isHidden()  # Not explicitly hidden

    def test_indicator_default_theme_is_dark(self, qtbot):
        """Test default theme is dark."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        assert indicator._theme == "dark"


class TestConnectionIndicatorWidgetStructure:
    """Tests for ConnectionIndicator widget structure."""

    def test_indicator_has_dot_label(self, qtbot):
        """Test indicator has a dot indicator."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        assert indicator._dot is not None
        assert indicator._dot.text() == "●"
        assert indicator._dot.objectName() == "connectionDot"
        assert indicator._dot.width() == 16
        assert indicator._dot.height() == 16

    def test_indicator_has_status_label(self, qtbot):
        """Test indicator has a status text label."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        assert indicator._label is not None
        assert indicator._label.objectName() == "connectionLabel"
        assert indicator._label.text() == "Disconnected"

    def test_indicator_layout_is_horizontal(self, qtbot):
        """Test indicator uses horizontal layout."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        layout = indicator.layout()
        assert isinstance(layout, QHBoxLayout)

    def test_indicator_layout_spacing(self, qtbot):
        """Test indicator layout has correct spacing."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        layout = indicator.layout()
        assert layout.spacing() == 8

    def test_indicator_layout_margins(self, qtbot):
        """Test indicator layout has correct margins."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        layout = indicator.layout()
        margins = layout.contentsMargins()
        assert margins.left() == 8
        assert margins.top() == 4
        assert margins.right() == 8
        assert margins.bottom() == 4

    def test_indicator_cursor_is_pointer(self, qtbot):
        """Test indicator has pointer cursor for clickability."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        assert indicator.cursor().shape() == Qt.CursorShape.PointingHandCursor

    def test_indicator_has_tooltip(self, qtbot):
        """Test indicator has tooltip."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        assert "Disconnected" in indicator.toolTip()


class TestConnectionIndicatorStateChanges:
    """Tests for ConnectionIndicator state changes."""

    def test_set_state_connected(self, qtbot):
        """Test changing state to CONNECTED."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        indicator.set_state(ConnectionState.CONNECTED)

        assert indicator._state == ConnectionState.CONNECTED
        assert indicator.state == ConnectionState.CONNECTED
        assert indicator._label.text() == "Connected"

    def test_set_state_connecting(self, qtbot):
        """Test changing state to CONNECTING."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        indicator.set_state(ConnectionState.CONNECTING)

        assert indicator._state == ConnectionState.CONNECTING
        assert indicator.state == ConnectionState.CONNECTING
        assert indicator._label.text() == "Connecting..."

    def test_set_state_disconnected(self, qtbot):
        """Test changing state to DISCONNECTED."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        indicator.set_state(ConnectionState.CONNECTED)
        indicator.set_state(ConnectionState.DISCONNECTED)

        assert indicator._state == ConnectionState.DISCONNECTED
        assert indicator.state == ConnectionState.DISCONNECTED
        assert indicator._label.text() == "Disconnected"

    def test_set_state_error(self, qtbot):
        """Test changing state to ERROR."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        indicator.set_state(ConnectionState.ERROR)

        assert indicator._state == ConnectionState.ERROR
        assert indicator.state == ConnectionState.ERROR
        assert indicator._label.text() == "Error"

    def test_state_transitions(self, qtbot):
        """Test multiple state transitions."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        # disconnected -> connecting -> connected -> error -> disconnected
        indicator.set_state(ConnectionState.CONNECTING)
        assert indicator.state == ConnectionState.CONNECTING

        indicator.set_state(ConnectionState.CONNECTED)
        assert indicator.state == ConnectionState.CONNECTED

        indicator.set_state(ConnectionState.ERROR)
        assert indicator.state == ConnectionState.ERROR

        indicator.set_state(ConnectionState.DISCONNECTED)
        assert indicator.state == ConnectionState.DISCONNECTED

    def test_set_state_does_not_emit_if_same(self, qtbot):
        """Test set_state does not emit signal if state unchanged."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        # Set initial state
        indicator.set_state(ConnectionState.CONNECTED)

        # Track signals
        signals_received = []
        indicator.state_changed.connect(lambda s: signals_received.append(s))

        # Set same state again
        indicator.set_state(ConnectionState.CONNECTED)

        # No signal should be emitted
        assert len(signals_received) == 0


class TestConnectionIndicatorSetStatus:
    """Tests for set_status method (string-based status from SombraService)."""

    def test_set_status_connected(self, qtbot):
        """Test set_status with 'Connected' string."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        indicator.set_status("Connected")

        assert indicator.state == ConnectionState.CONNECTED

    def test_set_status_connected_variations(self, qtbot):
        """Test set_status recognizes various connected strings."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        variations = ["Connected", "connected", "CONNECTED"]
        for status in variations:
            indicator.set_state(ConnectionState.DISCONNECTED)  # Reset
            indicator.set_status(status)
            assert indicator.state == ConnectionState.CONNECTED, f"Failed for: {status}"

    def test_set_status_disconnected(self, qtbot):
        """Test set_status with 'Disconnected' string."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        indicator.set_status("Disconnected")

        assert indicator.state == ConnectionState.DISCONNECTED

    def test_set_status_disconnected_variations(self, qtbot):
        """Test set_status recognizes various disconnected strings."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        # First set to connected to verify change
        indicator.set_state(ConnectionState.CONNECTED)

        variations = ["Disconnected", "disconnected", "DISCONNECTED"]
        for status in variations:
            indicator.set_state(ConnectionState.CONNECTED)  # Reset
            indicator.set_status(status)
            assert indicator.state == ConnectionState.DISCONNECTED, f"Failed for: {status}"

    def test_set_status_connecting(self, qtbot):
        """Test set_status with 'Connecting...' string."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        indicator.set_status("Connecting...")

        assert indicator.state == ConnectionState.CONNECTING

    def test_set_status_connecting_variations(self, qtbot):
        """Test set_status recognizes various connecting strings."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        variations = ["Connecting...", "connecting", "Connecting"]
        for status in variations:
            indicator.set_state(ConnectionState.DISCONNECTED)  # Reset
            indicator.set_status(status)
            assert indicator.state == ConnectionState.CONNECTING, f"Failed for: {status}"

    def test_set_status_error(self, qtbot):
        """Test set_status with 'Error' string."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        indicator.set_status("Error")

        assert indicator.state == ConnectionState.ERROR

    def test_set_status_error_with_message(self, qtbot):
        """Test set_status with error message."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        indicator.set_status("Error: Connection refused")

        assert indicator.state == ConnectionState.ERROR

    def test_set_status_rate_limited(self, qtbot):
        """Test set_status with rate limited message shows as connecting."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        indicator.set_status("Rate limited, retrying in 2s...")

        # This should be treated as connecting since it's a transient state
        assert indicator.state == ConnectionState.CONNECTING

    def test_set_status_sending_query(self, qtbot):
        """Test set_status with 'Sending query...' message."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        indicator.set_status("Sending query...")

        # This should be connecting state
        assert indicator.state == ConnectionState.CONNECTING


class TestConnectionIndicatorTheme:
    """Tests for ConnectionIndicator theme support."""

    def test_set_theme_dark(self, qtbot):
        """Test setting dark theme."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        indicator.set_theme("dark")

        assert indicator._theme == "dark"

    def test_set_theme_light(self, qtbot):
        """Test setting light theme."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        indicator.set_theme("light")

        assert indicator._theme == "light"

    def test_set_theme_invalid_defaults_to_dark(self, qtbot):
        """Test setting invalid theme defaults to dark."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        indicator.set_theme("invalid_theme")

        assert indicator._theme == "dark"

    def test_dark_theme_colors_are_correct(self, qtbot):
        """Test dark theme uses correct colors from DARK_PALETTE."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        colors = indicator._COLORS["dark"]
        assert colors[ConnectionState.CONNECTED] == DARK_PALETTE["success"]
        assert colors[ConnectionState.CONNECTING] == DARK_PALETTE["warning"]
        assert colors[ConnectionState.DISCONNECTED] == DARK_PALETTE["error"]
        assert colors[ConnectionState.ERROR] == DARK_PALETTE["error"]

    def test_light_theme_colors_are_correct(self, qtbot):
        """Test light theme uses correct colors from LIGHT_PALETTE."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        colors = indicator._COLORS["light"]
        assert colors[ConnectionState.CONNECTED] == LIGHT_PALETTE["success"]
        assert colors[ConnectionState.CONNECTING] == LIGHT_PALETTE["warning"]
        assert colors[ConnectionState.DISCONNECTED] == LIGHT_PALETTE["error"]
        assert colors[ConnectionState.ERROR] == LIGHT_PALETTE["error"]


class TestConnectionIndicatorSignals:
    """Tests for ConnectionIndicator signals."""

    def test_state_changed_signal_emits_on_change(self, qtbot):
        """Test state_changed signal emits when state changes."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        signals_received = []
        indicator.state_changed.connect(lambda s: signals_received.append(s))

        indicator.set_state(ConnectionState.CONNECTED)

        assert len(signals_received) == 1
        assert signals_received[0] == ConnectionState.CONNECTED

    def test_clicked_signal_emits_on_left_click(self, qtbot):
        """Test clicked signal emits on left mouse click."""
        from PySide6.QtGui import QMouseEvent
        from PySide6.QtCore import QEvent, QPointF

        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        signals_received = []
        indicator.clicked.connect(lambda: signals_received.append(True))

        # Simulate left click
        local_pos = QPointF(10, 10)
        global_pos = indicator.mapToGlobal(local_pos.toPoint())
        event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            local_pos,
            QPointF(global_pos),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        indicator.mousePressEvent(event)

        assert len(signals_received) == 1

    def test_right_click_does_not_emit_clicked(self, qtbot):
        """Test right click does not emit clicked signal."""
        from PySide6.QtGui import QMouseEvent
        from PySide6.QtCore import QEvent, QPointF

        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        signals_received = []
        indicator.clicked.connect(lambda: signals_received.append(True))

        # Simulate right click
        local_pos = QPointF(10, 10)
        global_pos = indicator.mapToGlobal(local_pos.toPoint())
        event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            local_pos,
            QPointF(global_pos),
            Qt.MouseButton.RightButton,
            Qt.MouseButton.RightButton,
            Qt.KeyboardModifier.NoModifier,
        )
        indicator.mousePressEvent(event)

        assert len(signals_received) == 0


class TestConnectionIndicatorAnimation:
    """Tests for ConnectionIndicator animation behavior."""

    def test_animation_starts_on_connecting(self, qtbot):
        """Test pulse animation starts when state is CONNECTING."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        indicator.set_state(ConnectionState.CONNECTING)

        # Animation should be running
        assert indicator._pulse_animation.state() == indicator._pulse_animation.State.Running

    def test_animation_stops_on_connected(self, qtbot):
        """Test pulse animation stops when state changes from CONNECTING to CONNECTED."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        # Start animation
        indicator.set_state(ConnectionState.CONNECTING)
        assert indicator._pulse_animation.state() == indicator._pulse_animation.State.Running

        # Stop animation by changing state
        indicator.set_state(ConnectionState.CONNECTED)
        assert indicator._pulse_animation.state() == indicator._pulse_animation.State.Stopped

    def test_animation_stops_on_disconnected(self, qtbot):
        """Test pulse animation stops when state changes to DISCONNECTED."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        indicator.set_state(ConnectionState.CONNECTING)
        indicator.set_state(ConnectionState.DISCONNECTED)

        assert indicator._pulse_animation.state() == indicator._pulse_animation.State.Stopped

    def test_animation_stops_on_error(self, qtbot):
        """Test pulse animation stops when state changes to ERROR."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        indicator.set_state(ConnectionState.CONNECTING)
        indicator.set_state(ConnectionState.ERROR)

        assert indicator._pulse_animation.state() == indicator._pulse_animation.State.Stopped

    def test_opacity_resets_when_animation_stops(self, qtbot):
        """Test opacity resets to 1.0 when animation stops."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        # Start animation
        indicator.set_state(ConnectionState.CONNECTING)

        # Stop animation
        indicator.set_state(ConnectionState.CONNECTED)

        assert indicator._opacity == 1.0


class TestConnectionIndicatorCompactMode:
    """Tests for ConnectionIndicator compact mode."""

    def test_compact_mode_hides_label(self, qtbot):
        """Test compact mode hides the text label."""
        indicator = ConnectionIndicator(compact=True)
        qtbot.addWidget(indicator)

        assert indicator._label.isHidden()

    def test_normal_mode_shows_label(self, qtbot):
        """Test normal mode shows the text label (not hidden)."""
        indicator = ConnectionIndicator(compact=False)
        qtbot.addWidget(indicator)

        assert not indicator._label.isHidden()  # Not explicitly hidden

    def test_set_compact_hides_label(self, qtbot):
        """Test set_compact(True) hides the label."""
        indicator = ConnectionIndicator(compact=False)
        qtbot.addWidget(indicator)

        assert not indicator._label.isHidden()  # Not hidden initially

        indicator.set_compact(True)

        assert indicator._label.isHidden()  # Now hidden

    def test_set_compact_shows_label(self, qtbot):
        """Test set_compact(False) shows the label."""
        indicator = ConnectionIndicator(compact=True)
        qtbot.addWidget(indicator)

        assert indicator._label.isHidden()  # Initially hidden

        indicator.set_compact(False)

        assert not indicator._label.isHidden()  # No longer hidden


class TestConnectionIndicatorPublicAPI:
    """Tests for ConnectionIndicator public API."""

    def test_state_property(self, qtbot):
        """Test state property returns correct value."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        assert indicator.state == ConnectionState.DISCONNECTED

        indicator.set_state(ConnectionState.CONNECTED)
        assert indicator.state == ConnectionState.CONNECTED

    def test_is_connected_property(self, qtbot):
        """Test is_connected property."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        assert indicator.is_connected is False

        indicator.set_state(ConnectionState.CONNECTED)
        assert indicator.is_connected is True

        indicator.set_state(ConnectionState.CONNECTING)
        assert indicator.is_connected is False

        indicator.set_state(ConnectionState.DISCONNECTED)
        assert indicator.is_connected is False

        indicator.set_state(ConnectionState.ERROR)
        assert indicator.is_connected is False


class TestConnectionIndicatorEdgeCases:
    """Edge case tests for ConnectionIndicator."""

    def test_rapid_state_changes(self, qtbot):
        """Test indicator handles rapid state changes."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        # Rapid state changes
        for _ in range(20):
            indicator.set_state(ConnectionState.CONNECTING)
            indicator.set_state(ConnectionState.CONNECTED)
            indicator.set_state(ConnectionState.ERROR)
            indicator.set_state(ConnectionState.DISCONNECTED)

        assert indicator.state == ConnectionState.DISCONNECTED

    def test_rapid_status_changes(self, qtbot):
        """Test indicator handles rapid status string changes."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        statuses = ["Connected", "Disconnected", "Connecting...", "Error", "Connected"]
        for _ in range(10):
            for status in statuses:
                indicator.set_status(status)

        assert indicator.state == ConnectionState.CONNECTED

    def test_theme_change_preserves_state(self, qtbot):
        """Test changing theme preserves current state."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        indicator.set_state(ConnectionState.CONNECTED)
        indicator.set_theme("light")

        assert indicator.state == ConnectionState.CONNECTED

    def test_compact_change_preserves_state(self, qtbot):
        """Test changing compact mode preserves current state."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        indicator.set_state(ConnectionState.CONNECTED)
        indicator.set_compact(True)

        assert indicator.state == ConnectionState.CONNECTED

    def test_tooltip_updates_on_state_change(self, qtbot):
        """Test tooltip updates when state changes."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        indicator.set_state(ConnectionState.CONNECTED)
        assert "Connected" in indicator.toolTip()

        indicator.set_state(ConnectionState.ERROR)
        assert "Error" in indicator.toolTip()
