"""Unit tests for AgentStatusCard component.

Tests verify:
- Status badge changes (online/offline/busy)
- Styling matches SciFiTheme
- Widget structure correctness
- Signal emissions
- Public API methods
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout

from sombra.ui.components.agent_status_card import (
    AgentStatus,
    AgentStatusCard,
    StatusBadge,
)
from sombra.ui.styles.theme import SciFiTheme


class TestAgentStatus:
    """Tests for AgentStatus enum."""

    def test_status_values(self):
        """Test that all status values are defined."""
        assert AgentStatus.ONLINE.value == "online"
        assert AgentStatus.OFFLINE.value == "offline"
        assert AgentStatus.BUSY.value == "busy"

    def test_status_enum_count(self):
        """Test that we have exactly 3 status types."""
        assert len(AgentStatus) == 3


class TestStatusBadge:
    """Tests for StatusBadge component."""

    def test_badge_creation_default_status(self, qtbot):
        """Test badge creates with default OFFLINE status."""
        badge = StatusBadge()
        qtbot.addWidget(badge)

        assert badge._status == AgentStatus.OFFLINE

    def test_badge_creation_with_status(self, qtbot):
        """Test badge creates with specified status."""
        badge = StatusBadge(status=AgentStatus.ONLINE)
        qtbot.addWidget(badge)

        assert badge._status == AgentStatus.ONLINE

    def test_badge_has_dot_label(self, qtbot):
        """Test badge has a dot indicator."""
        badge = StatusBadge()
        qtbot.addWidget(badge)

        assert badge._dot is not None
        assert badge._dot.text() == "●"
        assert badge._dot.width() == 12

    def test_badge_has_status_label(self, qtbot):
        """Test badge has a status text label."""
        badge = StatusBadge(status=AgentStatus.ONLINE)
        qtbot.addWidget(badge)

        assert badge._label is not None
        assert badge._label.text() == "Online"

    def test_badge_status_label_text_matches_status(self, qtbot):
        """Test label text matches the current status."""
        for status in AgentStatus:
            badge = StatusBadge(status=status)
            qtbot.addWidget(badge)

            expected_text = status.value.capitalize()
            assert badge._label.text() == expected_text

    def test_badge_set_status_updates_status(self, qtbot):
        """Test set_status method updates internal status."""
        badge = StatusBadge(status=AgentStatus.OFFLINE)
        qtbot.addWidget(badge)

        badge.set_status(AgentStatus.ONLINE)

        assert badge._status == AgentStatus.ONLINE

    def test_badge_set_status_updates_label(self, qtbot):
        """Test set_status method updates label text."""
        badge = StatusBadge(status=AgentStatus.OFFLINE)
        qtbot.addWidget(badge)

        badge.set_status(AgentStatus.BUSY)

        assert badge._label.text() == "Busy"

    def test_badge_color_online(self, qtbot):
        """Test online status uses green color."""
        badge = StatusBadge(status=AgentStatus.ONLINE)
        qtbot.addWidget(badge)

        expected_color = StatusBadge.COLORS[AgentStatus.ONLINE]
        assert expected_color == "#4ecca3"

    def test_badge_color_offline(self, qtbot):
        """Test offline status uses gray color."""
        badge = StatusBadge(status=AgentStatus.OFFLINE)
        qtbot.addWidget(badge)

        expected_color = StatusBadge.COLORS[AgentStatus.OFFLINE]
        assert expected_color == "#555566"

    def test_badge_color_busy(self, qtbot):
        """Test busy status uses yellow/orange color."""
        badge = StatusBadge(status=AgentStatus.BUSY)
        qtbot.addWidget(badge)

        expected_color = StatusBadge.COLORS[AgentStatus.BUSY]
        assert expected_color == "#f9a825"

    def test_hex_to_rgb_conversion(self):
        """Test hex color to RGB string conversion."""
        result = StatusBadge._hex_to_rgb("#4ecca3")
        assert result == "78, 204, 163"

        result = StatusBadge._hex_to_rgb("#ffffff")
        assert result == "255, 255, 255"

        result = StatusBadge._hex_to_rgb("#000000")
        assert result == "0, 0, 0"

    def test_hex_to_rgb_without_hash(self):
        """Test hex conversion works without leading hash."""
        result = StatusBadge._hex_to_rgb("ff0000")
        assert result == "255, 0, 0"

    def test_badge_layout_is_horizontal(self, qtbot):
        """Test badge uses horizontal layout."""
        badge = StatusBadge()
        qtbot.addWidget(badge)

        layout = badge.layout()
        assert isinstance(layout, QHBoxLayout)

    def test_badge_layout_spacing(self, qtbot):
        """Test badge layout has correct spacing."""
        badge = StatusBadge()
        qtbot.addWidget(badge)

        layout = badge.layout()
        assert layout.spacing() == 6

    def test_badge_layout_margins(self, qtbot):
        """Test badge layout has correct margins."""
        badge = StatusBadge()
        qtbot.addWidget(badge)

        layout = badge.layout()
        margins = layout.contentsMargins()
        assert margins.left() == 8
        assert margins.top() == 4
        assert margins.right() == 10
        assert margins.bottom() == 4


class TestAgentStatusCard:
    """Tests for AgentStatusCard component."""

    @pytest.fixture
    def default_card(self, qtbot):
        """Create a default agent card for testing."""
        card = AgentStatusCard(
            agent_id="builder",
            name="Builder Agent",
            description="Builds code",
        )
        qtbot.addWidget(card)
        return card

    @pytest.fixture
    def online_card(self, qtbot):
        """Create an online agent card for testing."""
        card = AgentStatusCard(
            agent_id="reviewer",
            name="Reviewer Agent",
            description="Reviews code",
            status=AgentStatus.ONLINE,
        )
        qtbot.addWidget(card)
        return card

    # === Card Creation Tests ===

    def test_card_creation_basic(self, default_card):
        """Test card creates with basic parameters."""
        assert default_card._agent_id == "builder"
        assert default_card._name == "Builder Agent"
        assert default_card._description == "Builds code"
        assert default_card._status == AgentStatus.OFFLINE

    def test_card_default_status_is_offline(self, default_card):
        """Test default status is OFFLINE."""
        assert default_card.status == AgentStatus.OFFLINE

    def test_card_object_name(self, default_card):
        """Test card has correct object name."""
        assert default_card.objectName() == "agentCard_builder"

    def test_card_fixed_height(self, default_card):
        """Test card has fixed height."""
        assert default_card.maximumHeight() == 120
        assert default_card.minimumHeight() == 120

    def test_card_cursor_is_pointer(self, default_card):
        """Test card has pointer cursor for clickability."""
        assert default_card.cursor().shape() == Qt.CursorShape.PointingHandCursor

    # === Widget Structure Tests ===

    def test_card_has_name_label(self, default_card):
        """Test card has a name label."""
        assert default_card._name_label is not None
        assert default_card._name_label.text() == "Builder Agent"

    def test_card_has_description_label(self, default_card):
        """Test card has a description label."""
        assert default_card._desc_label is not None
        assert default_card._desc_label.text() == "Builds code"

    def test_card_description_has_word_wrap(self, default_card):
        """Test description label has word wrap enabled."""
        assert default_card._desc_label.wordWrap() is True

    def test_card_has_status_badge(self, default_card):
        """Test card has a status badge."""
        assert default_card._status_badge is not None
        assert isinstance(default_card._status_badge, StatusBadge)

    def test_card_has_icon_widget(self, default_card):
        """Test card has an icon widget."""
        assert default_card._icon_widget is not None
        assert default_card._icon_widget.width() == 36
        assert default_card._icon_widget.height() == 36

    def test_card_layout_is_vertical(self, default_card):
        """Test card uses vertical layout."""
        layout = default_card.layout()
        assert isinstance(layout, QVBoxLayout)

    def test_card_layout_margins(self, default_card):
        """Test card layout has correct margins."""
        layout = default_card.layout()
        margins = layout.contentsMargins()
        assert margins.left() == 20
        assert margins.top() == 16
        assert margins.right() == 20
        assert margins.bottom() == 16

    def test_card_layout_spacing(self, default_card):
        """Test card layout has correct spacing."""
        layout = default_card.layout()
        assert layout.spacing() == 12

    # === Status Change Tests ===

    def test_set_status_online(self, default_card):
        """Test changing status to ONLINE."""
        default_card.set_status(AgentStatus.ONLINE)

        assert default_card._status == AgentStatus.ONLINE
        assert default_card.status == AgentStatus.ONLINE

    def test_set_status_offline(self, online_card):
        """Test changing status to OFFLINE."""
        online_card.set_status(AgentStatus.OFFLINE)

        assert online_card._status == AgentStatus.OFFLINE
        assert online_card.status == AgentStatus.OFFLINE

    def test_set_status_busy(self, default_card):
        """Test changing status to BUSY."""
        default_card.set_status(AgentStatus.BUSY)

        assert default_card._status == AgentStatus.BUSY
        assert default_card.status == AgentStatus.BUSY

    def test_set_status_updates_badge(self, default_card):
        """Test set_status updates the status badge."""
        default_card.set_status(AgentStatus.ONLINE)

        assert default_card._status_badge._status == AgentStatus.ONLINE

    def test_status_transitions(self, default_card):
        """Test multiple status transitions."""
        # offline -> online -> busy -> offline
        default_card.set_status(AgentStatus.ONLINE)
        assert default_card.status == AgentStatus.ONLINE

        default_card.set_status(AgentStatus.BUSY)
        assert default_card.status == AgentStatus.BUSY

        default_card.set_status(AgentStatus.OFFLINE)
        assert default_card.status == AgentStatus.OFFLINE

    # === Property Tests ===

    def test_agent_id_property(self, default_card):
        """Test agent_id property returns correct value."""
        assert default_card.agent_id == "builder"

    def test_status_property(self, default_card):
        """Test status property returns correct value."""
        assert default_card.status == AgentStatus.OFFLINE

        default_card.set_status(AgentStatus.ONLINE)
        assert default_card.status == AgentStatus.ONLINE

    # === Public API Tests ===

    def test_set_name_updates_label(self, default_card):
        """Test set_name updates the name label."""
        default_card.set_name("New Builder Name")

        assert default_card._name == "New Builder Name"
        assert default_card._name_label.text() == "New Builder Name"

    def test_set_description_updates_label(self, default_card):
        """Test set_description updates the description label."""
        default_card.set_description("New description text")

        assert default_card._description == "New description text"
        assert default_card._desc_label.text() == "New description text"

    # === Icon Tests ===

    def test_builder_uses_developer_tools_icon(self, qtbot):
        """Test builder agent uses developer tools icon."""
        from qfluentwidgets import FluentIcon

        card = AgentStatusCard(
            agent_id="builder",
            name="Builder",
            description="Test",
        )
        qtbot.addWidget(card)

        assert card._icon == FluentIcon.DEVELOPER_TOOLS

    def test_reviewer_uses_view_icon(self, qtbot):
        """Test reviewer agent uses view icon."""
        from qfluentwidgets import FluentIcon

        card = AgentStatusCard(
            agent_id="reviewer",
            name="Reviewer",
            description="Test",
        )
        qtbot.addWidget(card)

        assert card._icon == FluentIcon.VIEW

    def test_tester_uses_checkbox_icon(self, qtbot):
        """Test tester agent uses checkbox icon."""
        from qfluentwidgets import FluentIcon

        card = AgentStatusCard(
            agent_id="tester",
            name="Tester",
            description="Test",
        )
        qtbot.addWidget(card)

        assert card._icon == FluentIcon.CHECKBOX

    def test_refactor_uses_sync_icon(self, qtbot):
        """Test refactor agent uses sync icon."""
        from qfluentwidgets import FluentIcon

        card = AgentStatusCard(
            agent_id="refactor",
            name="Refactor",
            description="Test",
        )
        qtbot.addWidget(card)

        assert card._icon == FluentIcon.SYNC

    def test_unknown_agent_uses_robot_icon(self, qtbot):
        """Test unknown agent uses robot icon as fallback."""
        from qfluentwidgets import FluentIcon

        card = AgentStatusCard(
            agent_id="unknown_agent",
            name="Unknown",
            description="Test",
        )
        qtbot.addWidget(card)

        assert card._icon == FluentIcon.ROBOT

    def test_custom_icon_overrides_default(self, qtbot):
        """Test custom icon overrides agent type default."""
        from qfluentwidgets import FluentIcon

        card = AgentStatusCard(
            agent_id="builder",
            name="Builder",
            description="Test",
            icon=FluentIcon.HEART,
        )
        qtbot.addWidget(card)

        assert card._icon == FluentIcon.HEART

    # === Signal Tests ===

    def test_clicked_signal_emits_agent_id(self, qtbot, default_card):
        """Test pressing card emits clicked signal with agent_id.

        Note: We test via mousePress instead of mouseClick because the parent
        class SimpleCardWidget has its own clicked signal that conflicts.
        Our implementation emits on mousePressEvent for left button.
        """
        from PySide6.QtCore import QEvent, QPointF
        from PySide6.QtGui import QMouseEvent

        signals_received = []
        default_card.clicked.connect(lambda x: signals_received.append(x))

        # Simulate mouse press event using new Qt6 API
        local_pos = QPointF(10, 10)
        global_pos = default_card.mapToGlobal(local_pos.toPoint())
        event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            local_pos,
            QPointF(global_pos),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        default_card.mousePressEvent(event)

        assert signals_received == ["builder"]

    def test_clicked_signal_different_agents(self, qtbot):
        """Test clicked signal emits correct agent_id for different agents."""
        from PySide6.QtCore import QEvent, QPointF
        from PySide6.QtGui import QMouseEvent

        agents = ["builder", "reviewer", "tester", "refactor"]

        for agent_id in agents:
            card = AgentStatusCard(
                agent_id=agent_id,
                name=f"{agent_id.title()} Agent",
                description="Test",
            )
            qtbot.addWidget(card)

            signals_received = []
            card.clicked.connect(lambda x, received=signals_received: received.append(x))

            local_pos = QPointF(10, 10)
            global_pos = card.mapToGlobal(local_pos.toPoint())
            event = QMouseEvent(
                QEvent.Type.MouseButtonPress,
                local_pos,
                QPointF(global_pos),
                Qt.MouseButton.LeftButton,
                Qt.MouseButton.LeftButton,
                Qt.KeyboardModifier.NoModifier,
            )
            card.mousePressEvent(event)

            assert signals_received == [agent_id]

    def test_right_click_does_not_emit_signal(self, qtbot, default_card):
        """Test right clicking card does not emit our clicked signal."""
        from PySide6.QtCore import QEvent, QPointF
        from PySide6.QtGui import QMouseEvent

        signals_received = []
        default_card.clicked.connect(lambda x: signals_received.append(x))

        # Right button press should not trigger our signal
        local_pos = QPointF(10, 10)
        global_pos = default_card.mapToGlobal(local_pos.toPoint())
        event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            local_pos,
            QPointF(global_pos),
            Qt.MouseButton.RightButton,
            Qt.MouseButton.RightButton,
            Qt.KeyboardModifier.NoModifier,
        )
        default_card.mousePressEvent(event)

        assert len(signals_received) == 0

    # === Theme/Styling Tests ===

    def test_name_label_uses_theme_primary_color(self, default_card):
        """Test name label uses SciFiTheme primary text color."""
        stylesheet = default_card._name_label.styleSheet()
        assert SciFiTheme.TEXT_PRIMARY in stylesheet

    def test_description_label_uses_theme_secondary_color(self, default_card):
        """Test description label uses SciFiTheme secondary text color."""
        stylesheet = default_card._desc_label.styleSheet()
        assert SciFiTheme.TEXT_SECONDARY in stylesheet

    def test_card_stylesheet_contains_cyan_rgb_when_online(self, online_card):
        """Test online card stylesheet uses cyan accent."""
        stylesheet = online_card.styleSheet()
        assert SciFiTheme.CYAN_RGB in stylesheet

    def test_card_stylesheet_changes_on_status_change(self, default_card):
        """Test card stylesheet updates when status changes."""
        offline_style = default_card.styleSheet()

        default_card.set_status(AgentStatus.ONLINE)
        online_style = default_card.styleSheet()

        # Styles should be different
        assert offline_style != online_style
        # Online style should contain cyan
        assert SciFiTheme.CYAN_RGB in online_style


class TestAgentStatusCardEdgeCases:
    """Edge case tests for AgentStatusCard."""

    def test_empty_description(self, qtbot):
        """Test card handles empty description."""
        card = AgentStatusCard(
            agent_id="test",
            name="Test Agent",
            description="",
        )
        qtbot.addWidget(card)

        assert card._desc_label.text() == ""

    def test_long_description(self, qtbot):
        """Test card handles long description."""
        long_desc = "This is a very long description " * 10
        card = AgentStatusCard(
            agent_id="test",
            name="Test Agent",
            description=long_desc,
        )
        qtbot.addWidget(card)

        assert card._desc_label.text() == long_desc
        # Word wrap should handle long text
        assert card._desc_label.wordWrap() is True

    def test_special_characters_in_name(self, qtbot):
        """Test card handles special characters in name."""
        card = AgentStatusCard(
            agent_id="test",
            name="Test <Agent> & \"More\"",
            description="Description",
        )
        qtbot.addWidget(card)

        assert card._name_label.text() == "Test <Agent> & \"More\""

    def test_unicode_in_description(self, qtbot):
        """Test card handles unicode in description."""
        card = AgentStatusCard(
            agent_id="test",
            name="Test Agent",
            description="Description with unicode: 你好 🚀 ñ",
        )
        qtbot.addWidget(card)

        assert "你好" in card._desc_label.text()
        assert "🚀" in card._desc_label.text()

    def test_case_insensitive_agent_id_for_icons(self, qtbot):
        """Test agent ID matching for icons is case-insensitive."""
        from qfluentwidgets import FluentIcon

        card = AgentStatusCard(
            agent_id="BUILDER",
            name="Builder",
            description="Test",
        )
        qtbot.addWidget(card)

        assert card._icon == FluentIcon.DEVELOPER_TOOLS

    def test_multiple_status_changes(self, qtbot):
        """Test card handles rapid status changes."""
        card = AgentStatusCard(
            agent_id="test",
            name="Test",
            description="Test",
        )
        qtbot.addWidget(card)

        # Rapid status changes
        for _ in range(10):
            card.set_status(AgentStatus.ONLINE)
            card.set_status(AgentStatus.BUSY)
            card.set_status(AgentStatus.OFFLINE)

        assert card.status == AgentStatus.OFFLINE
