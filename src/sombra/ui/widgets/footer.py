"""Footer widget with version info and GitHub link."""

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from ... import __version__
from ...themes.colors import DARK_PALETTE, LIGHT_PALETTE

# GitHub repository URL
GITHUB_URL = "https://github.com/Danny-sth/sombra-desktop"


class Footer(QWidget):
    """Footer widget displaying version info and GitHub link.

    Shows:
    - Application version (from __init__.__version__)
    - Clickable GitHub repository link

    Designed to be placed at the bottom of the main window.
    """

    def __init__(self, parent: QWidget | None = None):
        """Initialize footer widget.

        Args:
            parent: Parent widget.
        """
        super().__init__(parent)

        self._theme = "dark"
        self._setup_ui()
        self._update_theme()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(16)

        # Version label (left side)
        self._version_label = QLabel(f"v{__version__}")
        self._version_label.setObjectName("footerVersion")
        self._version_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self._version_label)

        # Spacer
        layout.addStretch()

        # GitHub link (right side)
        self._github_link = QLabel("GitHub")
        self._github_link.setObjectName("footerGithubLink")
        self._github_link.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        self._github_link.setCursor(Qt.CursorShape.PointingHandCursor)
        self._github_link.setToolTip(GITHUB_URL)
        self._github_link.mousePressEvent = self._on_github_click
        layout.addWidget(self._github_link)

        # Set fixed height
        self.setFixedHeight(36)

    def _update_theme(self) -> None:
        """Update styles based on current theme."""
        palette = DARK_PALETTE if self._theme == "dark" else LIGHT_PALETTE

        # Version label style
        self._version_label.setStyleSheet(
            f"color: {palette['text_secondary']}; "
            f"font-size: 12px; "
            f"font-weight: 400;"
        )

        # GitHub link style (accent color, underlined on hover via stylesheet)
        self._github_link.setStyleSheet(
            f"color: {palette['accent_primary']}; "
            f"font-size: 12px; "
            f"font-weight: 500;"
        )

        # Container background
        self.setStyleSheet(
            f"Footer {{ "
            f"background-color: {palette['bg_secondary']}; "
            f"border-top: 1px solid {palette['border_light']}; "
            f"}}"
        )

    def _on_github_click(self, event) -> None:
        """Handle GitHub link click - open in default browser."""
        if event.button() == Qt.MouseButton.LeftButton:
            QDesktopServices.openUrl(GITHUB_URL)

    # ===== Public API =====

    @Slot(str)
    def set_theme(self, theme: str) -> None:
        """Update colors for theme.

        Args:
            theme: Theme name ('dark' or 'light').
        """
        self._theme = theme if theme in ("dark", "light") else "dark"
        self._update_theme()

    @property
    def version(self) -> str:
        """Get displayed version string."""
        return __version__
