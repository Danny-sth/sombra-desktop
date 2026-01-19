"""Agents page - Placeholder for future agent management."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout

from qfluentwidgets import (
    ScrollArea,
    TitleLabel,
    SubtitleLabel,
    BodyLabel,
    IconWidget,
    FluentIcon,
    SimpleCardWidget,
    CaptionLabel,
)


class AgentsPage(ScrollArea):
    """Placeholder for future agents management interface."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("agentsPage")

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Build the placeholder interface."""
        self.container = QWidget()
        self.setWidget(self.container)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(36, 20, 36, 20)
        layout.setSpacing(24)

        # Header
        header = TitleLabel("Agents")
        layout.addWidget(header)

        subtitle = SubtitleLabel("Manage your AI agents")
        subtitle.setStyleSheet("color: #888888;")
        layout.addWidget(subtitle)

        # Coming soon card
        layout.addStretch()

        # Center content
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.setSpacing(16)

        # Icon
        icon = IconWidget(FluentIcon.ROBOT)
        icon.setFixedSize(64, 64)
        center_layout.addWidget(icon, alignment=Qt.AlignmentFlag.AlignCenter)

        # Title
        title = SubtitleLabel("Agent Management")
        center_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Description
        desc = BodyLabel("This feature is coming soon!")
        desc.setStyleSheet("color: #888888;")
        center_layout.addWidget(desc, alignment=Qt.AlignmentFlag.AlignCenter)

        # Details card
        card = SimpleCardWidget()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(8)

        features_title = BodyLabel("Planned Features:")
        card_layout.addWidget(features_title)

        features = [
            "Create and configure AI agents",
            "Assign tasks to specific agents",
            "Monitor agent activity and performance",
            "Agent collaboration and workflows",
            "Custom agent personalities and capabilities",
        ]

        for feature in features:
            feature_label = CaptionLabel(f"  {feature}")
            feature_label.setStyleSheet("color: #888888;")
            card_layout.addWidget(feature_label)

        center_layout.addWidget(card)
        layout.addWidget(center_widget)

        layout.addStretch()
