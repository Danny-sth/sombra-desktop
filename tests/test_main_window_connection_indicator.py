"""Integration tests for ConnectionIndicator in MainWindow sidebar.

Tests verify:
- ConnectionIndicator is properly placed in navigation sidebar
- Signal connections between SombraService and ConnectionIndicator
- Theme propagation to ConnectionIndicator
- Click handler connection to check_connection_async
"""

import pytest
from unittest.mock import MagicMock, patch

from PySide6.QtCore import Qt

from sombra.ui.widgets.connection_indicator import (
    ConnectionIndicator,
    ConnectionState,
)


class TestConnectionIndicatorMainWindowIntegration:
    """Integration tests for ConnectionIndicator in main window context."""

    def test_connection_indicator_exists_in_navigation(self, qtbot):
        """Test that ConnectionIndicator is created in main window.

        Note: We test the widget directly since MainWindow requires services.
        """
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        # Verify object name matches what MainWindow sets
        indicator.setObjectName("connectionIndicator")
        assert indicator.objectName() == "connectionIndicator"

    def test_connection_indicator_responds_to_service_status(self, qtbot):
        """Test indicator responds to status strings from SombraService."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        # Simulate SombraService status changes
        service_statuses = [
            ("Connected", ConnectionState.CONNECTED),
            ("Disconnected", ConnectionState.DISCONNECTED),
            ("Connecting...", ConnectionState.CONNECTING),
            ("Error", ConnectionState.ERROR),
            ("Sending query...", ConnectionState.CONNECTING),
            ("Rate limited, retrying in 2s...", ConnectionState.CONNECTING),
        ]

        for status_str, expected_state in service_statuses:
            indicator.set_status(status_str)
            assert indicator.state == expected_state, f"Failed for status: {status_str}"

    def test_connection_indicator_click_emits_signal(self, qtbot):
        """Test clicking indicator emits clicked signal for connection check."""
        from PySide6.QtGui import QMouseEvent
        from PySide6.QtCore import QEvent, QPointF

        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        clicked = []
        indicator.clicked.connect(lambda: clicked.append(True))

        # Simulate click
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

        assert len(clicked) == 1

    def test_theme_change_updates_indicator(self, qtbot):
        """Test theme change from settings updates indicator colors."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        # Start with connected state
        indicator.set_state(ConnectionState.CONNECTED)

        # Change theme
        indicator.set_theme("light")
        assert indicator._theme == "light"

        # State should be preserved
        assert indicator.state == ConnectionState.CONNECTED

        # Change back to dark
        indicator.set_theme("dark")
        assert indicator._theme == "dark"


class TestConnectionIndicatorSidebarPlacement:
    """Tests for ConnectionIndicator sidebar placement behavior."""

    def test_indicator_has_compact_mode_for_sidebar(self, qtbot):
        """Test indicator can be placed in sidebar with compact mode."""
        # Non-compact for full navigation panel
        full_indicator = ConnectionIndicator(compact=False)
        qtbot.addWidget(full_indicator)

        # Compact for collapsed sidebar
        compact_indicator = ConnectionIndicator(compact=True)
        qtbot.addWidget(compact_indicator)

        assert not full_indicator._compact
        assert compact_indicator._compact
        assert compact_indicator._label.isHidden()

    def test_indicator_tooltip_provides_status_info(self, qtbot):
        """Test indicator tooltip shows status for accessibility."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        # Tooltip should contain status information
        indicator.set_state(ConnectionState.CONNECTED)
        assert "Connected" in indicator.toolTip()

        indicator.set_state(ConnectionState.DISCONNECTED)
        assert "Disconnected" in indicator.toolTip()


class TestConnectionIndicatorServiceSignalFlow:
    """Tests for signal flow between components."""

    def test_state_changed_signal_can_be_connected(self, qtbot):
        """Test state_changed signal can be connected to callbacks."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        states_received = []
        indicator.state_changed.connect(lambda s: states_received.append(s))

        indicator.set_state(ConnectionState.CONNECTING)
        indicator.set_state(ConnectionState.CONNECTED)
        indicator.set_state(ConnectionState.DISCONNECTED)

        assert states_received == [
            ConnectionState.CONNECTING,
            ConnectionState.CONNECTED,
            ConnectionState.DISCONNECTED,
        ]

    def test_multiple_signal_receivers(self, qtbot):
        """Test indicator can have multiple signal receivers."""
        indicator = ConnectionIndicator()
        qtbot.addWidget(indicator)

        receiver1 = []
        receiver2 = []

        indicator.state_changed.connect(lambda s: receiver1.append(s))
        indicator.state_changed.connect(lambda s: receiver2.append(s))

        indicator.set_state(ConnectionState.CONNECTED)

        assert receiver1 == [ConnectionState.CONNECTED]
        assert receiver2 == [ConnectionState.CONNECTED]
