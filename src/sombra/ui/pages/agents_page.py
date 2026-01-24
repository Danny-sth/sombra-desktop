"""Agents page - Swarm status and management dashboard."""

import logging
from typing import Optional

from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

from qfluentwidgets import (
    BodyLabel,
    CaptionLabel,
    FluentIcon,
    InfoBar,
    InfoBarPosition,
    LineEdit,
    PrimaryPushButton,
    PushButton,
    ScrollArea,
    SimpleCardWidget,
    StrongBodyLabel,
    SubtitleLabel,
    TitleLabel,
)

from ..components.agent_status_card import AgentStatus as UIAgentStatus, AgentStatusCard
from ..components.agent_output_panel import AgentOutputPanel
from ...services.swarm_service import (
    AgentRole,
    AgentStatus,
    SwarmMode,
    SwarmService,
    SwarmState,
    SwarmTask,
    TaskStatus,
    get_swarm_service,
)

logger = logging.getLogger(__name__)


# Map server AgentStatus to UI AgentStatus
STATUS_MAP = {
    AgentStatus.IDLE: UIAgentStatus.OFFLINE,
    AgentStatus.WORKING: UIAgentStatus.BUSY,
    AgentStatus.WAITING: UIAgentStatus.BUSY,
    AgentStatus.ERROR: UIAgentStatus.OFFLINE,
    AgentStatus.STOPPED: UIAgentStatus.OFFLINE,
}


class TaskCard(SimpleCardWidget):
    """Card showing current task status."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._setup_ui()
        self._task: Optional[SwarmTask] = None

    def _setup_ui(self) -> None:
        """Build task card UI."""
        self.setFixedHeight(180)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # Header row
        header = QHBoxLayout()
        self._title = StrongBodyLabel("No Active Task")
        header.addWidget(self._title)
        header.addStretch()
        self._status_label = CaptionLabel("")
        self._status_label.setStyleSheet("color: #888888;")
        header.addWidget(self._status_label)
        layout.addLayout(header)

        # Description
        self._desc = BodyLabel("")
        self._desc.setWordWrap(True)
        layout.addWidget(self._desc)

        # Stats row
        stats = QHBoxLayout()
        self._files_label = CaptionLabel("Files: -")
        self._cost_label = CaptionLabel("Cost: $0.00")
        self._time_label = CaptionLabel("Time: -")
        stats.addWidget(self._files_label)
        stats.addWidget(self._cost_label)
        stats.addWidget(self._time_label)
        stats.addStretch()
        layout.addLayout(stats)

        layout.addStretch()

    def update_task(self, task: Optional[SwarmTask], state: SwarmState) -> None:
        """Update card with task data."""
        self._task = task

        if task is None:
            self._title.setText("No Active Task")
            self._status_label.setText("")
            self._desc.setText("Start a new task to see progress here.")
            self._files_label.setText("Files: -")
            self._cost_label.setText("Cost: $0.00")
            self._time_label.setText("Time: -")
            return

        # Title and status
        status_emoji = self._get_status_emoji(task.status)
        self._title.setText(f"{status_emoji} Task: {task.id}")
        self._status_label.setText(task.status.value.replace("_", " ").title())

        # Description (truncated)
        desc = task.description
        if len(desc) > 100:
            desc = desc[:100] + "..."
        self._desc.setText(desc)

        # Stats
        self._files_label.setText(f"Files: {len(task.changed_files)}")
        self._cost_label.setText(f"Cost: ${state.total_cost_usd:.2f}")

        if state.total_duration_seconds:
            mins = int(state.total_duration_seconds // 60)
            secs = int(state.total_duration_seconds % 60)
            self._time_label.setText(f"Time: {mins}m {secs}s")
        else:
            self._time_label.setText("Time: -")

    @staticmethod
    def _get_status_emoji(status: TaskStatus) -> str:
        """Get emoji for task status."""
        return {
            TaskStatus.PENDING: "⏳",
            TaskStatus.DECOMPOSING: "🔍",
            TaskStatus.RUNNING: "🔄",
            TaskStatus.REVIEWING: "👀",
            TaskStatus.TESTING: "🧪",
            TaskStatus.AWAITING_APPROVAL: "❓",
            TaskStatus.APPROVED: "✅",
            TaskStatus.REJECTED: "🔙",
            TaskStatus.COMPLETED: "🎉",
            TaskStatus.FAILED: "❌",
            TaskStatus.RUNNING_PYTEST: "🧪",
            TaskStatus.PUSHING_CI: "📤",
            TaskStatus.WAITING_CI: "⏳",
            TaskStatus.RUNNING_QA: "🔬",
            TaskStatus.ANALYZING_FAILURES: "🔍",
            TaskStatus.GENERATING_REPORT: "📊",
            TaskStatus.WAITING_FOR_INPUT: "💬",
        }.get(status, "❓")


class AgentsPage(ScrollArea):
    """Swarm status dashboard with task management and agent cards."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("agentsPage")

        self._agent_cards: dict[str, AgentStatusCard] = {}
        self._swarm_service: Optional[SwarmService] = None
        self._refresh_timer: Optional[QTimer] = None

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Build the agents dashboard interface."""
        self.container = QWidget()
        self.setWidget(self.container)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(36, 20, 36, 20)
        layout.setSpacing(24)

        # Header with connection status
        self._create_header(layout)

        # Task input section
        self._create_task_input(layout)

        # Current task card
        self._create_task_card(layout)

        # Agent cards grid
        self._create_agents_grid(layout)

        # Agent output panel (real-time logs)
        self._create_output_panel(layout)

        # Action buttons
        self._create_action_buttons(layout)

        layout.addStretch()

    def _create_header(self, parent_layout: QVBoxLayout) -> None:
        """Create page header with connection status."""
        header_row = QHBoxLayout()

        header = TitleLabel("Agent Swarm")
        header_row.addWidget(header)

        header_row.addStretch()

        self._connection_label = CaptionLabel("Checking...")
        self._connection_label.setStyleSheet("color: #888888;")
        header_row.addWidget(self._connection_label)

        parent_layout.addLayout(header_row)

        subtitle = BodyLabel("Orchestrate Claude Code agents for development tasks")
        parent_layout.addWidget(subtitle)

    def _create_task_input(self, parent_layout: QVBoxLayout) -> None:
        """Create task input section."""
        section = SubtitleLabel("New Task")
        parent_layout.addWidget(section)

        input_row = QHBoxLayout()

        self._task_input = LineEdit()
        self._task_input.setPlaceholderText("Describe the task for the swarm...")
        self._task_input.setClearButtonEnabled(True)
        input_row.addWidget(self._task_input, stretch=1)

        self._start_btn = PrimaryPushButton("Start Task")
        self._start_btn.setIcon(FluentIcon.PLAY)
        self._start_btn.clicked.connect(self._on_start_task)
        input_row.addWidget(self._start_btn)

        parent_layout.addLayout(input_row)

    def _create_task_card(self, parent_layout: QVBoxLayout) -> None:
        """Create current task status card."""
        section = SubtitleLabel("Current Task")
        parent_layout.addWidget(section)

        self._task_card = TaskCard()
        parent_layout.addWidget(self._task_card)

    def _create_agents_grid(self, parent_layout: QVBoxLayout) -> None:
        """Create grid of agent status cards (3 core agents)."""
        section_title = SubtitleLabel("Agents")
        parent_layout.addWidget(section_title)

        grid = QGridLayout()
        grid.setSpacing(16)

        # Create cards for 3 core agent roles
        agents_info = [
            ("coder", "💻 Coder", "Writes code, tests, commits (no push)"),
            ("deploy", "🚀 Deploy", "CI/CD: review, push, monitor CI, deploy"),
            ("qa", "🧪 QA", "Quality Assurance: write autotests, run against deployed app"),
        ]

        for idx, (agent_id, name, desc) in enumerate(agents_info):
            card = AgentStatusCard(
                agent_id=agent_id,
                name=name,
                description=desc,
                status=UIAgentStatus.OFFLINE,
            )
            card.clicked.connect(self._on_agent_clicked)
            self._agent_cards[agent_id] = card

            # 3 cards in a row
            grid.addWidget(card, 0, idx)

        parent_layout.addLayout(grid)

    def _create_output_panel(self, parent_layout: QVBoxLayout) -> None:
        """Create agent output panel for real-time logs."""
        section_title = SubtitleLabel("Real-time Output")
        parent_layout.addWidget(section_title)

        self._output_panel = AgentOutputPanel()
        parent_layout.addWidget(self._output_panel)

    def _create_action_buttons(self, parent_layout: QVBoxLayout) -> None:
        """Create action buttons for task management."""
        buttons_row = QHBoxLayout()

        self._approve_btn = PushButton("Approve")
        self._approve_btn.setIcon(FluentIcon.ACCEPT)
        self._approve_btn.clicked.connect(self._on_approve)
        self._approve_btn.setEnabled(False)
        buttons_row.addWidget(self._approve_btn)

        self._reject_btn = PushButton("Reject")
        self._reject_btn.setIcon(FluentIcon.CLOSE)
        self._reject_btn.clicked.connect(self._on_reject)
        self._reject_btn.setEnabled(False)
        buttons_row.addWidget(self._reject_btn)

        self._stop_btn = PushButton("Stop")
        self._stop_btn.setIcon(FluentIcon.PAUSE)
        self._stop_btn.clicked.connect(self._on_stop)
        self._stop_btn.setEnabled(False)
        buttons_row.addWidget(self._stop_btn)

        buttons_row.addStretch()

        self._refresh_btn = PushButton("Refresh")
        self._refresh_btn.setIcon(FluentIcon.SYNC)
        self._refresh_btn.clicked.connect(self._on_refresh)
        buttons_row.addWidget(self._refresh_btn)

        parent_layout.addLayout(buttons_row)

    def _connect_signals(self) -> None:
        """Connect to SwarmService signals."""
        self._swarm_service = get_swarm_service()

        self._swarm_service.state_updated.connect(self._on_state_updated)
        self._swarm_service.connection_status.connect(self._on_connection_status)
        self._swarm_service.error_occurred.connect(self._on_error)
        self._swarm_service.question_received.connect(self._on_question)
        self._swarm_service.agent_output.connect(self._on_agent_output)

        # Enter key starts task
        self._task_input.returnPressed.connect(self._on_start_task)

    def showEvent(self, event) -> None:
        """Handle page show - start SSE streams and refresh timer."""
        super().showEvent(event)

        if self._swarm_service:
            # Check connection and get initial status
            self._swarm_service.check_connection_async()
            self._swarm_service.get_status_async()

            # Start SSE streams
            self._swarm_service.start_status_stream()
            self._swarm_service.start_output_stream()

        # Refresh every 5 seconds as backup
        if self._refresh_timer is None:
            self._refresh_timer = QTimer(self)
            self._refresh_timer.timeout.connect(self._on_refresh)
            self._refresh_timer.start(5000)

    def hideEvent(self, event) -> None:
        """Handle page hide - stop streams."""
        super().hideEvent(event)

        if self._swarm_service:
            self._swarm_service.stop_streams()

        if self._refresh_timer:
            self._refresh_timer.stop()

    # ===== Slot Handlers =====

    @Slot(object)
    def _on_state_updated(self, state: SwarmState) -> None:
        """Handle swarm state update."""
        # Update agent cards
        for role, agent in state.agents.items():
            card_id = role.value
            if card_id in self._agent_cards:
                ui_status = STATUS_MAP.get(agent.status, UIAgentStatus.OFFLINE)
                self._agent_cards[card_id].set_status(ui_status)

                # Update description with current subtask if working
                if agent.current_subtask:
                    subtask_desc = agent.current_subtask.get("description", "")
                    if subtask_desc:
                        self._agent_cards[card_id].set_description(
                            f"Working: {subtask_desc[:50]}..."
                        )
                elif agent.status == AgentStatus.IDLE:
                    # Reset to default description when idle
                    default_descs = {
                        "coder": "Writes code, tests, commits (no push)",
                        "deploy": "CI/CD: review, push, monitor CI, deploy",
                        "qa": "Quality Assurance: write autotests, run against deployed app",
                    }
                    self._agent_cards[card_id].set_description(
                        default_descs.get(card_id, "")
                    )

                # Update agent statistics
                cost_usd = 0.0
                if agent.usage:
                    # Calculate cost from usage (rough estimate: $3/M input, $15/M output for Sonnet)
                    input_tokens = agent.usage.get("input_tokens", 0)
                    output_tokens = agent.usage.get("output_tokens", 0)
                    cost_usd = (input_tokens / 1_000_000 * 3.0) + (output_tokens / 1_000_000 * 15.0)

                self._agent_cards[card_id].update_stats(
                    iterations=agent.iterations,
                    cost_usd=cost_usd,
                )

        # Update task card
        self._task_card.update_task(state.current_task, state)

        # Update button states
        self._update_buttons(state)

    @Slot(str)
    def _on_connection_status(self, status: str) -> None:
        """Handle connection status update."""
        self._connection_label.setText(status)

        if "Connected" in status:
            self._connection_label.setStyleSheet("color: #4ecca3;")
        else:
            self._connection_label.setStyleSheet("color: #f44336;")

    @Slot(str)
    def _on_error(self, error: str) -> None:
        """Handle error."""
        InfoBar.error(
            title="Swarm Error",
            content=error,
            position=InfoBarPosition.TOP_RIGHT,
            parent=self,
        )

    @Slot(str, list)
    def _on_question(self, question: str, options: list) -> None:
        """Handle question from swarm."""
        # Show question dialog or inline input
        # For now, just show an info bar
        InfoBar.info(
            title="Swarm Question",
            content=question,
            position=InfoBarPosition.TOP_RIGHT,
            parent=self,
        )

    @Slot(str, str)
    def _on_agent_output(self, agent: str, message: str) -> None:
        """Handle agent output message."""
        self._output_panel.append_output(agent, message)

    @Slot(str)
    def _on_agent_clicked(self, agent_id: str) -> None:
        """Handle agent card click."""
        logger.debug("Agent clicked: %s", agent_id)
        # Future: Show agent details panel

    @Slot()
    def _on_start_task(self) -> None:
        """Start a new swarm task."""
        description = self._task_input.text().strip()
        if not description:
            InfoBar.warning(
                title="Empty Task",
                content="Please enter a task description",
                position=InfoBarPosition.TOP_RIGHT,
                parent=self,
            )
            return

        if self._swarm_service:
            # Clear previous output
            self._output_panel.clear()

            self._swarm_service.start_task_async(
                description=description,
                mode=SwarmMode.DEVELOPMENT,
            )
            self._task_input.clear()

    @Slot()
    def _on_approve(self) -> None:
        """Approve current task."""
        if self._swarm_service:
            self._swarm_service.approve_task_async()

    @Slot()
    def _on_reject(self) -> None:
        """Reject current task."""
        if self._swarm_service:
            self._swarm_service.reject_task_async("Rejected by user")

    @Slot()
    def _on_stop(self) -> None:
        """Stop current task."""
        if self._swarm_service:
            self._swarm_service.stop_task_async()

    @Slot()
    def _on_refresh(self) -> None:
        """Refresh swarm status."""
        if self._swarm_service:
            self._swarm_service.get_status_async()

    def _update_buttons(self, state: SwarmState) -> None:
        """Update button enabled states based on swarm state."""
        is_running = state.is_running
        awaiting_approval = (
            state.current_task is not None and
            state.current_task.status == TaskStatus.AWAITING_APPROVAL
        )

        self._start_btn.setEnabled(not is_running)
        self._stop_btn.setEnabled(is_running)
        self._approve_btn.setEnabled(awaiting_approval)
        self._reject_btn.setEnabled(awaiting_approval)

    # ===== Public API =====

    def set_agent_status(self, agent_id: str, status: UIAgentStatus) -> None:
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
