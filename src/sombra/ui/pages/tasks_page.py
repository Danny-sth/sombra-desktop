"""Tasks page - Placeholder for future orchestrator task management."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    CaptionLabel,
    FluentIcon,
    IconWidget,
    ScrollArea,
    SimpleCardWidget,
    SubtitleLabel,
    TitleLabel,
)


class TasksPage(ScrollArea):
    """Placeholder for future task orchestrator interface."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("tasksPage")

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
        header = TitleLabel("Tasks")
        layout.addWidget(header)

        subtitle = SubtitleLabel("Orchestrator task management")
        subtitle.setStyleSheet("color: #888888;")
        layout.addWidget(subtitle)

        # Coming soon content
        layout.addStretch()

        # Center content
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.setSpacing(16)

        # Icon
        icon = IconWidget(FluentIcon.CHECKBOX)
        icon.setFixedSize(64, 64)
        center_layout.addWidget(icon, alignment=Qt.AlignmentFlag.AlignCenter)

        # Title
        title = SubtitleLabel("Task Orchestrator")
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
            "View and manage running tasks",
            "Create complex multi-step workflows",
            "Schedule automated tasks",
            "Monitor task progress and results",
            "Task dependencies and chaining",
            "Priority and resource management",
        ]

        for feature in features:
            feature_label = CaptionLabel(f"  {feature}")
            feature_label.setStyleSheet("color: #888888;")
            card_layout.addWidget(feature_label)

        center_layout.addWidget(card)
        layout.addWidget(center_widget)

        layout.addStretch()
