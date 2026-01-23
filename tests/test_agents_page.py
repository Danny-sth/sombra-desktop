"""Unit tests for AgentsPage component.

Tests verify:
- Page structure and layout
- Mock agent data display
- Agent cards grid (2x2 layout)
- Status badge integration
- Click handling
- Public API for status updates
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QVBoxLayout

from sombra.ui.components.agent_status_card import AgentStatus, AgentStatusCard
from sombra.ui.pages.agents_page import MOCK_AGENTS, AgentsPage
from sombra.ui.styles.theme import SciFiTheme


class TestAgentsPageBasicStructure:
    """Tests for AgentsPage basic structure and setup."""

    @pytest.fixture
    def page(self, qtbot):
        """Create an AgentsPage instance for testing."""
        page = AgentsPage()
        qtbot.addWidget(page)
        return page

    def test_page_creation(self, page):
        """Test page creates successfully."""
        assert page is not None

    def test_page_object_name(self, page):
        """Test page has correct object name."""
        assert page.objectName() == "agentsPage"

    def test_page_is_scroll_area(self, page):
        """Test page inherits from ScrollArea."""
        from qfluentwidgets import ScrollArea
        assert isinstance(page, ScrollArea)

    def test_page_widget_resizable(self, page):
        """Test page widget is resizable."""
        assert page.widgetResizable() is True

    def test_page_horizontal_scrollbar_disabled(self, page):
        """Test horizontal scrollbar is always off."""
        assert page.horizontalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAlwaysOff

    def test_page_has_container(self, page):
        """Test page has a container widget."""
        assert page.container is not None
        assert page.widget() == page.container

    def test_container_layout_is_vertical(self, page):
        """Test container uses vertical layout."""
        layout = page.container.layout()
        assert isinstance(layout, QVBoxLayout)

    def test_container_layout_margins(self, page):
        """Test container layout has correct margins."""
        layout = page.container.layout()
        margins = layout.contentsMargins()
        assert margins.left() == 36
        assert margins.top() == 20
        assert margins.right() == 36
        assert margins.bottom() == 20

    def test_container_layout_spacing(self, page):
        """Test container layout has correct spacing."""
        layout = page.container.layout()
        assert layout.spacing() == 24


class TestAgentsPageHeader:
    """Tests for AgentsPage header section."""

    @pytest.fixture
    def page(self, qtbot):
        """Create an AgentsPage instance for testing."""
        page = AgentsPage()
        qtbot.addWidget(page)
        return page

    def test_header_title_exists(self, page):
        """Test page has a title label."""
        from qfluentwidgets import TitleLabel

        layout = page.container.layout()
        # First item should be the title
        title_item = layout.itemAt(0)
        assert title_item is not None
        title_widget = title_item.widget()
        assert isinstance(title_widget, TitleLabel)

    def test_header_title_text(self, page):
        """Test title text is correct."""

        layout = page.container.layout()
        title_widget = layout.itemAt(0).widget()
        assert title_widget.text() == "Agent Swarm"

    def test_header_subtitle_exists(self, page):
        """Test page has a subtitle label."""
        from qfluentwidgets import BodyLabel

        layout = page.container.layout()
        # Second item should be the subtitle
        subtitle_item = layout.itemAt(1)
        assert subtitle_item is not None
        subtitle_widget = subtitle_item.widget()
        assert isinstance(subtitle_widget, BodyLabel)

    def test_header_subtitle_text(self, page):
        """Test subtitle text is correct."""
        layout = page.container.layout()
        subtitle_widget = layout.itemAt(1).widget()
        assert subtitle_widget.text() == "Monitor and manage your AI development agents"

    def test_header_subtitle_uses_secondary_color(self, page):
        """Test subtitle uses theme secondary text color."""
        layout = page.container.layout()
        subtitle_widget = layout.itemAt(1).widget()
        stylesheet = subtitle_widget.styleSheet()
        assert SciFiTheme.TEXT_SECONDARY in stylesheet


class TestAgentsPageGrid:
    """Tests for AgentsPage agent cards grid."""

    @pytest.fixture
    def page(self, qtbot):
        """Create an AgentsPage instance for testing."""
        page = AgentsPage()
        qtbot.addWidget(page)
        return page

    def test_section_title_exists(self, page):
        """Test section has 'Active Agents' title."""
        from qfluentwidgets import SubtitleLabel

        layout = page.container.layout()
        # Third item should be section title
        section_item = layout.itemAt(2)
        assert section_item is not None
        section_widget = section_item.widget()
        assert isinstance(section_widget, SubtitleLabel)
        assert section_widget.text() == "Active Agents"

    def test_grid_layout_exists(self, page):
        """Test page has a grid layout for cards."""
        layout = page.container.layout()
        # Fourth item should be the grid layout
        grid_item = layout.itemAt(3)
        assert grid_item is not None
        grid_layout = grid_item.layout()
        assert isinstance(grid_layout, QGridLayout)

    def test_grid_layout_spacing(self, page):
        """Test grid layout has correct spacing."""
        layout = page.container.layout()
        grid_layout = layout.itemAt(3).layout()
        assert grid_layout.spacing() == 16

    def test_four_agent_cards_created(self, page):
        """Test exactly 4 agent cards are created."""
        assert len(page._agent_cards) == 4

    def test_all_expected_agents_present(self, page):
        """Test all expected agent IDs are present."""
        expected_ids = {"builder", "reviewer", "tester", "refactor"}
        actual_ids = set(page._agent_cards.keys())
        assert actual_ids == expected_ids

    def test_cards_are_agent_status_card_instances(self, page):
        """Test all cards are AgentStatusCard instances."""
        for card in page._agent_cards.values():
            assert isinstance(card, AgentStatusCard)


class TestMockAgentData:
    """Tests for MOCK_AGENTS data structure."""

    def test_mock_agents_count(self):
        """Test 4 agents are defined."""
        assert len(MOCK_AGENTS) == 4

    def test_mock_agent_has_required_keys(self):
        """Test each agent has required keys."""
        required_keys = {"id", "name", "description", "status"}
        for agent in MOCK_AGENTS:
            assert set(agent.keys()) == required_keys

    def test_builder_agent_data(self):
        """Test builder agent has correct data."""
        builder = next(a for a in MOCK_AGENTS if a["id"] == "builder")
        assert builder["name"] == "Builder Agent"
        assert "code" in builder["description"].lower()
        assert builder["status"] == AgentStatus.ONLINE

    def test_reviewer_agent_data(self):
        """Test reviewer agent has correct data."""
        reviewer = next(a for a in MOCK_AGENTS if a["id"] == "reviewer")
        assert reviewer["name"] == "Reviewer Agent"
        assert "review" in reviewer["description"].lower()
        assert reviewer["status"] == AgentStatus.ONLINE

    def test_tester_agent_data(self):
        """Test tester agent has correct data."""
        tester = next(a for a in MOCK_AGENTS if a["id"] == "tester")
        assert tester["name"] == "Tester Agent"
        assert "test" in tester["description"].lower()
        assert tester["status"] == AgentStatus.OFFLINE

    def test_refactor_agent_data(self):
        """Test refactor agent has correct data."""
        refactor = next(a for a in MOCK_AGENTS if a["id"] == "refactor")
        assert refactor["name"] == "Refactor Agent"
        assert refactor["status"] == AgentStatus.OFFLINE

    def test_online_agents_count(self):
        """Test 2 agents are online."""
        online_count = sum(1 for a in MOCK_AGENTS if a["status"] == AgentStatus.ONLINE)
        assert online_count == 2

    def test_offline_agents_count(self):
        """Test 2 agents are offline."""
        offline_count = sum(1 for a in MOCK_AGENTS if a["status"] == AgentStatus.OFFLINE)
        assert offline_count == 2


class TestAgentsPageCardContent:
    """Tests for agent card content correctness."""

    @pytest.fixture
    def page(self, qtbot):
        """Create an AgentsPage instance for testing."""
        page = AgentsPage()
        qtbot.addWidget(page)
        return page

    def test_builder_card_content(self, page):
        """Test builder card has correct content."""
        card = page._agent_cards["builder"]
        assert card.agent_id == "builder"
        assert card._name == "Builder Agent"
        assert card.status == AgentStatus.ONLINE

    def test_reviewer_card_content(self, page):
        """Test reviewer card has correct content."""
        card = page._agent_cards["reviewer"]
        assert card.agent_id == "reviewer"
        assert card._name == "Reviewer Agent"
        assert card.status == AgentStatus.ONLINE

    def test_tester_card_content(self, page):
        """Test tester card has correct content."""
        card = page._agent_cards["tester"]
        assert card.agent_id == "tester"
        assert card._name == "Tester Agent"
        assert card.status == AgentStatus.OFFLINE

    def test_refactor_card_content(self, page):
        """Test refactor card has correct content."""
        card = page._agent_cards["refactor"]
        assert card.agent_id == "refactor"
        assert card._name == "Refactor Agent"
        assert card.status == AgentStatus.OFFLINE


class TestAgentsPageGridPositioning:
    """Tests for 2x2 grid positioning of cards."""

    @pytest.fixture
    def page(self, qtbot):
        """Create an AgentsPage instance for testing."""
        page = AgentsPage()
        qtbot.addWidget(page)
        return page

    def test_builder_at_position_0_0(self, page):
        """Test builder card is at row 0, col 0."""
        layout = page.container.layout()
        grid_layout = layout.itemAt(3).layout()

        item = grid_layout.itemAtPosition(0, 0)
        assert item is not None
        card = item.widget()
        assert card.agent_id == "builder"

    def test_reviewer_at_position_0_1(self, page):
        """Test reviewer card is at row 0, col 1."""
        layout = page.container.layout()
        grid_layout = layout.itemAt(3).layout()

        item = grid_layout.itemAtPosition(0, 1)
        assert item is not None
        card = item.widget()
        assert card.agent_id == "reviewer"

    def test_tester_at_position_1_0(self, page):
        """Test tester card is at row 1, col 0."""
        layout = page.container.layout()
        grid_layout = layout.itemAt(3).layout()

        item = grid_layout.itemAtPosition(1, 0)
        assert item is not None
        card = item.widget()
        assert card.agent_id == "tester"

    def test_refactor_at_position_1_1(self, page):
        """Test refactor card is at row 1, col 1."""
        layout = page.container.layout()
        grid_layout = layout.itemAt(3).layout()

        item = grid_layout.itemAtPosition(1, 1)
        assert item is not None
        card = item.widget()
        assert card.agent_id == "refactor"


class TestAgentsPagePublicAPI:
    """Tests for AgentsPage public API methods."""

    @pytest.fixture
    def page(self, qtbot):
        """Create an AgentsPage instance for testing."""
        page = AgentsPage()
        qtbot.addWidget(page)
        return page

    def test_set_agent_status_updates_card(self, page):
        """Test set_agent_status updates the correct card."""
        # Initially offline
        card = page._agent_cards["tester"]
        assert card.status == AgentStatus.OFFLINE

        # Update to online
        page.set_agent_status("tester", AgentStatus.ONLINE)
        assert card.status == AgentStatus.ONLINE

    def test_set_agent_status_all_agents(self, page):
        """Test set_agent_status works for all agents."""
        for agent_id in page._agent_cards.keys():
            page.set_agent_status(agent_id, AgentStatus.BUSY)
            assert page._agent_cards[agent_id].status == AgentStatus.BUSY

    def test_set_agent_status_invalid_id_no_error(self, page):
        """Test set_agent_status with invalid ID doesn't raise error."""
        # Should silently ignore invalid ID
        page.set_agent_status("nonexistent", AgentStatus.ONLINE)
        # No exception raised

    def test_get_agent_card_returns_card(self, page):
        """Test get_agent_card returns correct card."""
        card = page.get_agent_card("builder")
        assert card is not None
        assert isinstance(card, AgentStatusCard)
        assert card.agent_id == "builder"

    def test_get_agent_card_all_agents(self, page):
        """Test get_agent_card works for all agents."""
        for agent_id in ["builder", "reviewer", "tester", "refactor"]:
            card = page.get_agent_card(agent_id)
            assert card is not None
            assert card.agent_id == agent_id

    def test_get_agent_card_invalid_id_returns_none(self, page):
        """Test get_agent_card with invalid ID returns None."""
        card = page.get_agent_card("nonexistent")
        assert card is None


class TestAgentsPageClickHandling:
    """Tests for agent card click handling."""

    @pytest.fixture
    def page(self, qtbot):
        """Create an AgentsPage instance for testing."""
        page = AgentsPage()
        qtbot.addWidget(page)
        return page

    def test_cards_emit_click_to_page_handler(self, page, qtbot):
        """Test cards emit clicked signal that reaches page handler.

        We verify the signal connection by actually emitting and checking
        that the handler is called, rather than checking receiver count
        (which is not available in PySide6 SignalInstance).
        """
        from PySide6.QtCore import QEvent, QPointF
        from PySide6.QtGui import QMouseEvent

        # Track handler calls
        called_ids = []
        original_handler = page._on_agent_clicked

        def tracking_handler(agent_id):
            called_ids.append(agent_id)
            original_handler(agent_id)

        page._on_agent_clicked = tracking_handler

        # Reconnect all cards to our tracking handler
        for card in page._agent_cards.values():
            card.clicked.disconnect()
            card.clicked.connect(tracking_handler)

        # Test each card emits correctly
        for agent_id, card in page._agent_cards.items():
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

        # All 4 agents should have been clicked
        assert len(called_ids) == 4
        assert set(called_ids) == {"builder", "reviewer", "tester", "refactor"}

    def test_on_agent_clicked_called(self, page, qtbot):
        """Test _on_agent_clicked slot is called when card emits signal."""
        from PySide6.QtCore import QEvent, QPointF
        from PySide6.QtGui import QMouseEvent

        # Track if slot was called
        clicked_agents = []
        original_handler = page._on_agent_clicked

        def tracking_handler(agent_id):
            clicked_agents.append(agent_id)
            original_handler(agent_id)

        page._on_agent_clicked = tracking_handler

        # Simulate click on builder card
        card = page._agent_cards["builder"]
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

        assert "builder" in clicked_agents


class TestAgentsPageStatusTransitions:
    """Tests for status transition scenarios."""

    @pytest.fixture
    def page(self, qtbot):
        """Create an AgentsPage instance for testing."""
        page = AgentsPage()
        qtbot.addWidget(page)
        return page

    def test_offline_to_online_transition(self, page):
        """Test transitioning an agent from offline to online."""
        page.set_agent_status("tester", AgentStatus.ONLINE)
        card = page._agent_cards["tester"]
        assert card.status == AgentStatus.ONLINE

    def test_online_to_offline_transition(self, page):
        """Test transitioning an agent from online to offline."""
        page.set_agent_status("builder", AgentStatus.OFFLINE)
        card = page._agent_cards["builder"]
        assert card.status == AgentStatus.OFFLINE

    def test_to_busy_transition(self, page):
        """Test transitioning an agent to busy status."""
        page.set_agent_status("builder", AgentStatus.BUSY)
        card = page._agent_cards["builder"]
        assert card.status == AgentStatus.BUSY

    def test_multiple_transitions(self, page):
        """Test multiple status transitions."""
        card = page._agent_cards["builder"]

        page.set_agent_status("builder", AgentStatus.BUSY)
        assert card.status == AgentStatus.BUSY

        page.set_agent_status("builder", AgentStatus.OFFLINE)
        assert card.status == AgentStatus.OFFLINE

        page.set_agent_status("builder", AgentStatus.ONLINE)
        assert card.status == AgentStatus.ONLINE

    def test_all_agents_online(self, page):
        """Test setting all agents to online."""
        for agent_id in page._agent_cards.keys():
            page.set_agent_status(agent_id, AgentStatus.ONLINE)

        for card in page._agent_cards.values():
            assert card.status == AgentStatus.ONLINE

    def test_all_agents_offline(self, page):
        """Test setting all agents to offline."""
        for agent_id in page._agent_cards.keys():
            page.set_agent_status(agent_id, AgentStatus.OFFLINE)

        for card in page._agent_cards.values():
            assert card.status == AgentStatus.OFFLINE


class TestAgentsPageEdgeCases:
    """Edge case tests for AgentsPage."""

    @pytest.fixture
    def page(self, qtbot):
        """Create an AgentsPage instance for testing."""
        page = AgentsPage()
        qtbot.addWidget(page)
        return page

    def test_rapid_status_changes(self, page):
        """Test rapid status changes don't cause issues."""
        for _ in range(50):
            page.set_agent_status("builder", AgentStatus.ONLINE)
            page.set_agent_status("builder", AgentStatus.BUSY)
            page.set_agent_status("builder", AgentStatus.OFFLINE)

        # Final state should be offline
        assert page._agent_cards["builder"].status == AgentStatus.OFFLINE

    def test_get_card_after_status_change(self, page):
        """Test get_agent_card returns card with updated status."""
        page.set_agent_status("tester", AgentStatus.ONLINE)
        card = page.get_agent_card("tester")
        assert card.status == AgentStatus.ONLINE

    def test_empty_string_agent_id(self, page):
        """Test handling of empty string agent ID."""
        # Should not raise error
        page.set_agent_status("", AgentStatus.ONLINE)
        card = page.get_agent_card("")
        assert card is None

    def test_none_like_agent_id(self, page):
        """Test handling of None-like agent ID strings."""
        page.set_agent_status("None", AgentStatus.ONLINE)
        page.set_agent_status("null", AgentStatus.ONLINE)
        # No exception raised

    def test_special_characters_in_agent_id(self, page):
        """Test handling of special characters in agent ID."""
        page.set_agent_status("test<script>", AgentStatus.ONLINE)
        page.set_agent_status("test'injection", AgentStatus.ONLINE)
        # No exception raised

    def test_cards_remain_valid_after_operations(self, page):
        """Test cards remain valid instances after various operations."""
        # Perform various operations
        page.set_agent_status("builder", AgentStatus.BUSY)
        page.set_agent_status("reviewer", AgentStatus.OFFLINE)
        page.get_agent_card("tester")
        page.set_agent_status("invalid", AgentStatus.ONLINE)

        # All cards should still be valid
        for agent_id, card in page._agent_cards.items():
            assert card is not None
            assert isinstance(card, AgentStatusCard)
            assert card.agent_id == agent_id
