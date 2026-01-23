"""Agents page - Agent swarm status and management."""

import logging
from typing import TypedDict

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QGridLayout, QVBoxLayout, QWidget

from qfluentwidgets import (
    BodyLabel,
    ScrollArea,
    SubtitleLabel,
    TitleLabel,
)

from ..components.agent_status_card import AgentStatus, AgentStatusCard

logger = logging.getLogger(__name__)


class AgentData(TypedDict):
    """Type definition for agent mock data."""

    id: str
    name: str
    description: str
    status: AgentStatus


# Mock agent data for display
MOCK_AGENTS: list[AgentData] = [
    {
        "id": "builder",
        "name": "Builder Agent",
        "description": "Implements features and writes clean, maintainable code.",
        "status": AgentStatus.ONLINE,
    },
    {
        "id": "reviewer",
        "name": "Reviewer Agent",
        "description": "Reviews code for quality, security, and best practices.",
        "status": AgentStatus.ONLINE,
    },
    {
        "id": "tester",
        "name": "Tester Agent",
        "description": "Creates and runs tests. Ensures code coverage and reliability.",
        "status": AgentStatus.OFFLINE,
    },
    {
        "id": "refactor",
        "name": "Refactor Agent",
        "description": "Optimizes and restructures code for better performance.",
        "status": AgentStatus.OFFLINE,
    },
]


class AgentsPage(ScrollArea):
    """Agent swarm status dashboard with agent cards."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("agentsPage")

        self._agent_cards: dict[str, AgentStatusCard] = {}
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Build the agents dashboard interface."""
        self.container = QWidget()
        self.setWidget(self.container)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(36, 20, 36, 20)
        layout.setSpacing(24)

        # Header
        self._create_header(layout)

        # Agent cards grid
        self._create_agents_grid(layout)

        layout.addStretch()

    def _create_header(self, parent_layout: QVBoxLayout) -> None:
        """Create page header."""
        header = TitleLabel("Agent Swarm")
        parent_layout.addWidget(header)

        subtitle = BodyLabel("Monitor and manage your AI development agents")
        parent_layout.addWidget(subtitle)

    def _create_agents_grid(self, parent_layout: QVBoxLayout) -> None:
        """Create 2x2 grid of agent status cards."""
        section_title = SubtitleLabel("Active Agents")
        parent_layout.addWidget(section_title)

        grid = QGridLayout()
        grid.setSpacing(16)

        # Create cards from mock data in 2x2 grid
        for idx, agent_data in enumerate(MOCK_AGENTS):
            card = AgentStatusCard(
                agent_id=agent_data["id"],
                name=agent_data["name"],
                description=agent_data["description"],
                status=agent_data["status"],
            )
            card.clicked.connect(self._on_agent_clicked)

            # Store reference for later updates
            self._agent_cards[agent_data["id"]] = card

            # Position in 2x2 grid
            row = idx // 2
            col = idx % 2
            grid.addWidget(card, row, col)

        parent_layout.addLayout(grid)

    # ===== Slot Handlers =====

    @Slot(str)
    def _on_agent_clicked(self, agent_id: str) -> None:
        """Handle agent card click.

        Args:
            agent_id: ID of the clicked agent
        """
        # Future: Open agent details panel or start interaction
        logger.debug("Agent clicked: %s", agent_id)

    # ===== Public API =====

    def set_agent_status(self, agent_id: str, status: AgentStatus) -> None:
        """Update status for a specific agent.

        Args:
            agent_id: Agent identifier (builder, reviewer, tester, refactor)
            status: New status to display
        """
        if agent_id in self._agent_cards:
            self._agent_cards[agent_id].set_status(status)

    def get_agent_card(self, agent_id: str) -> AgentStatusCard | None:
        """Get agent card by ID for external manipulation.

        Args:
            agent_id: Agent identifier

        Returns:
            AgentStatusCard instance or None if not found
        """
        return self._agent_cards.get(agent_id)
