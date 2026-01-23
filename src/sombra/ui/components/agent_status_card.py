"""Agent status card component for displaying agent state."""

from enum import Enum

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    CaptionLabel,
    FluentIcon,
    IconWidget,
    SimpleCardWidget,
    StrongBodyLabel,
)

from ..styles.theme import SciFiTheme


class AgentStatus(Enum):
    """Agent online/offline status."""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"


class StatusBadge(QFrame):
    """Small status indicator badge with dot and label."""

    # Status colors matching SciFiTheme
    COLORS = {
        AgentStatus.ONLINE: "#4ecca3",   # Green - connected
        AgentStatus.OFFLINE: "#555566",  # Muted gray
        AgentStatus.BUSY: "#f9a825",     # Yellow/Orange
    }

    def __init__(self, status: AgentStatus = AgentStatus.OFFLINE, parent: QWidget | None = None):
        super().__init__(parent)
        self._status = status
        self._setup_ui()
        self._update_style()

    def _setup_ui(self) -> None:
        """Build badge UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 10, 4)
        layout.setSpacing(6)

        # Status dot
        self._dot = BodyLabel("●")
        self._dot.setFixedWidth(12)
        layout.addWidget(self._dot)

        # Status text
        self._label = CaptionLabel(self._status.value.capitalize())
        layout.addWidget(self._label)

    def _update_style(self) -> None:
        """Update visual style based on status."""
        color = self.COLORS.get(self._status, self.COLORS[AgentStatus.OFFLINE])

        # Badge background
        self.setStyleSheet(f"""
            StatusBadge {{
                background-color: rgba({self._hex_to_rgb(color)}, 0.15);
                border: 1px solid rgba({self._hex_to_rgb(color)}, 0.4);
                border-radius: 10px;
            }}
        """)

        # Dot color
        self._dot.setStyleSheet(f"color: {color}; font-size: 10px;")

        # Label
        self._label.setText(self._status.value.capitalize())
        self._label.setStyleSheet(f"color: {color}; font-size: 11px;")

    def set_status(self, status: AgentStatus) -> None:
        """Update the badge status."""
        self._status = status
        self._update_style()

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> str:
        """Convert hex color to RGB string."""
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return f"{r}, {g}, {b}"


class AgentStatusCard(SimpleCardWidget):
    """Card displaying agent information with status indicator.

    Shows agent name, description, icon, and online/offline status badge.
    Uses SciFiTheme cyberpunk colors.
    """

    # Signal emitted when card is clicked
    clicked = Signal(str)  # Emits agent_id

    # Default icons for known agent types
    AGENT_ICONS = {
        "builder": FluentIcon.DEVELOPER_TOOLS,
        "reviewer": FluentIcon.VIEW,
        "tester": FluentIcon.CHECKBOX,
        "refactor": FluentIcon.SYNC,
    }

    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        status: AgentStatus = AgentStatus.OFFLINE,
        icon: FluentIcon | None = None,
        parent: QWidget | None = None
    ):
        super().__init__(parent)

        self._agent_id = agent_id
        self._name = name
        self._description = description
        self._status = status
        self._icon = icon or self.AGENT_ICONS.get(agent_id.lower(), FluentIcon.ROBOT)

        self.setObjectName(f"agentCard_{agent_id}")
        self._setup_ui()
        self._apply_theme()

    def _setup_ui(self) -> None:
        """Build the card UI."""
        self.setFixedHeight(120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(12)

        # Top row: Icon + Name + Status badge
        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        # Agent icon
        self._icon_widget = IconWidget(self._icon)
        self._icon_widget.setFixedSize(36, 36)
        top_row.addWidget(self._icon_widget)

        # Agent name
        self._name_label = StrongBodyLabel(self._name)
        self._name_label.setStyleSheet(f"color: {SciFiTheme.TEXT_PRIMARY};")
        top_row.addWidget(self._name_label)

        top_row.addStretch()

        # Status badge
        self._status_badge = StatusBadge(self._status)
        top_row.addWidget(self._status_badge)

        main_layout.addLayout(top_row)

        # Description
        self._desc_label = CaptionLabel(self._description)
        self._desc_label.setWordWrap(True)
        self._desc_label.setStyleSheet(f"color: {SciFiTheme.TEXT_SECONDARY};")
        main_layout.addWidget(self._desc_label)

        main_layout.addStretch()

    def _apply_theme(self) -> None:
        """Apply cyberpunk theme styling."""
        # Base card style with glassmorphism effect
        accent_rgb = SciFiTheme.CYAN_RGB if self._status == AgentStatus.ONLINE else "100, 100, 120"

        self.setStyleSheet(f"""
            AgentStatusCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba({accent_rgb}, 0.08),
                    stop:1 rgba({accent_rgb}, 0.02));
                border: 1px solid rgba({accent_rgb}, 0.2);
                border-radius: 12px;
            }}
            AgentStatusCard:hover {{
                border: 1px solid rgba({SciFiTheme.CYAN_RGB}, 0.4);
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba({SciFiTheme.CYAN_RGB}, 0.12),
                    stop:1 rgba({SciFiTheme.CYAN_RGB}, 0.04));
            }}
        """)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press to emit clicked signal."""
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._agent_id)

    # ===== Public API =====

    @property
    def agent_id(self) -> str:
        """Get agent identifier."""
        return self._agent_id

    @property
    def status(self) -> AgentStatus:
        """Get current agent status."""
        return self._status

    def set_status(self, status: AgentStatus) -> None:
        """Update the agent status.

        Args:
            status: New status (ONLINE, OFFLINE, BUSY)
        """
        self._status = status
        self._status_badge.set_status(status)
        self._apply_theme()

    def set_name(self, name: str) -> None:
        """Update agent display name."""
        self._name = name
        self._name_label.setText(name)

    def set_description(self, description: str) -> None:
        """Update agent description."""
        self._description = description
        self._desc_label.setText(description)

    def set_icon(self, icon: FluentIcon) -> None:
        """Update agent icon."""
        self._icon = icon
        self._icon_widget.setIcon(icon)
