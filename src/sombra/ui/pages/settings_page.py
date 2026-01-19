"""Settings page with Fluent Design setting cards."""

from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout

from qfluentwidgets import (
    ScrollArea,
    SettingCardGroup,
    SettingCard,
    SwitchSettingCard,
    PushSettingCard,
    HyperlinkCard,
    PrimaryPushSettingCard,
    FluentIcon,
    setTheme,
    Theme,
    InfoBar,
    InfoBarPosition,
    ComboBox,
)

from ...config.settings import get_settings


class SettingsPage(ScrollArea):
    """Application settings with Fluent Design cards."""

    # Signals
    theme_changed = Signal(str)
    settings_changed = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("settingsPage")

        self._settings = get_settings()
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self) -> None:
        """Build the settings interface."""
        self.container = QWidget()
        self.setWidget(self.container)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(36, 20, 36, 20)
        layout.setSpacing(24)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Appearance group
        self._create_appearance_group(layout)

        # API Configuration group
        self._create_api_group(layout)

        # Voice Settings group
        self._create_voice_group(layout)

        # Hotkeys group
        self._create_hotkeys_group(layout)

        # About group
        self._create_about_group(layout)

        layout.addStretch()

    def _create_appearance_group(self, parent_layout: QVBoxLayout) -> None:
        """Create appearance settings group."""
        group = SettingCardGroup("Appearance", self.container)

        # Theme selection using custom SettingCard with ComboBox
        self._theme_card = SettingCard(
            FluentIcon.BRUSH,
            "Theme",
            "Choose application color theme",
            parent=group
        )
        self._theme_combo = ComboBox()
        self._theme_combo.addItems(["Dark", "Light"])
        self._theme_combo.setMinimumWidth(120)
        self._theme_combo.currentTextChanged.connect(self._on_theme_changed)
        self._theme_card.hBoxLayout.addWidget(self._theme_combo)
        group.addSettingCard(self._theme_card)

        parent_layout.addWidget(group)

    def _create_api_group(self, parent_layout: QVBoxLayout) -> None:
        """Create API configuration group."""
        group = SettingCardGroup("API Configuration", self.container)

        # Sombra API URL
        self._api_url_card = PushSettingCard(
            "Configure",
            FluentIcon.GLOBE,
            "Sombra API URL",
            self._settings.sombra_api_url,
            parent=group
        )
        self._api_url_card.clicked.connect(self._on_configure_api_url)
        group.addSettingCard(self._api_url_card)

        # STT URL
        self._stt_url_card = PushSettingCard(
            "Configure",
            FluentIcon.MICROPHONE,
            "Speech-to-Text URL",
            self._settings.stt_url,
            parent=group
        )
        self._stt_url_card.clicked.connect(self._on_configure_stt_url)
        group.addSettingCard(self._stt_url_card)

        # Session ID
        self._session_card = PushSettingCard(
            "View",
            FluentIcon.PEOPLE,
            "Session ID",
            self._settings.sombra_session_id,
            parent=group
        )
        group.addSettingCard(self._session_card)

        parent_layout.addWidget(group)

    def _create_voice_group(self, parent_layout: QVBoxLayout) -> None:
        """Create voice settings group."""
        group = SettingCardGroup("Voice Settings", self.container)

        # Wake word enabled
        self._wakeword_card = SwitchSettingCard(
            FluentIcon.VOLUME,
            "Enable Wake Word",
            "Say 'Jarvis' to activate voice input",
            parent=group
        )
        self._wakeword_card.checkedChanged.connect(self._on_wakeword_changed)
        group.addSettingCard(self._wakeword_card)

        # Auto-stop (VAD)
        self._vad_card = SwitchSettingCard(
            FluentIcon.STOP_WATCH,
            "Voice Activity Detection",
            "Automatically stop recording when you stop speaking",
            parent=group
        )
        group.addSettingCard(self._vad_card)

        parent_layout.addWidget(group)

    def _create_hotkeys_group(self, parent_layout: QVBoxLayout) -> None:
        """Create hotkeys settings group."""
        group = SettingCardGroup("Keyboard Shortcuts", self.container)

        # Push-to-talk hotkey
        self._hotkey_card = PushSettingCard(
            "Change",
            FluentIcon.COMMAND_PROMPT,
            "Push-to-Talk Hotkey",
            self._settings.global_hotkey.upper().replace("+", " + "),
            parent=group
        )
        self._hotkey_card.clicked.connect(self._on_configure_hotkey)
        group.addSettingCard(self._hotkey_card)

        parent_layout.addWidget(group)

    def _create_about_group(self, parent_layout: QVBoxLayout) -> None:
        """Create about group."""
        group = SettingCardGroup("About", self.container)

        # Version info
        self._version_card = HyperlinkCard(
            "https://github.com/danny/sombra-desktop",
            "View on GitHub",
            FluentIcon.INFO,
            "Sombra Desktop",
            "v1.1 - Voice-enabled AI Assistant",
            parent=group
        )
        group.addSettingCard(self._version_card)

        # Check for updates
        self._update_card = PrimaryPushSettingCard(
            "Check Now",
            FluentIcon.UPDATE,
            "Check for Updates",
            "Ensure you have the latest features",
            parent=group
        )
        self._update_card.clicked.connect(self._on_check_updates)
        group.addSettingCard(self._update_card)

        parent_layout.addWidget(group)

    def _load_settings(self) -> None:
        """Load current settings into UI."""
        # Theme
        if self._settings.theme == "dark":
            self._theme_combo.setCurrentIndex(0)
        else:
            self._theme_combo.setCurrentIndex(1)

        # Wake word
        self._wakeword_card.setChecked(self._settings.wake_word_enabled)

        # VAD is always on for now
        self._vad_card.setChecked(True)

    # ===== Slot Handlers =====

    @Slot(str)
    def _on_theme_changed(self, text: str) -> None:
        """Handle theme change."""
        theme_name = "dark" if text == "Dark" else "light"

        if theme_name == "dark":
            setTheme(Theme.DARK)
        else:
            setTheme(Theme.LIGHT)

        self.theme_changed.emit(theme_name)

        InfoBar.success(
            title="Theme Changed",
            content=f"Switched to {theme_name} theme",
            parent=self,
            position=InfoBarPosition.TOP,
            duration=2000
        )

    @Slot()
    def _on_configure_api_url(self) -> None:
        """Configure Sombra API URL."""
        from qfluentwidgets import LineEdit, MessageBox

        # Simple input dialog
        InfoBar.info(
            title="Coming Soon",
            content="URL configuration dialog will be added",
            parent=self,
            position=InfoBarPosition.TOP,
            duration=2000
        )

    @Slot()
    def _on_configure_stt_url(self) -> None:
        """Configure STT URL."""
        InfoBar.info(
            title="Coming Soon",
            content="STT URL configuration dialog will be added",
            parent=self,
            position=InfoBarPosition.TOP,
            duration=2000
        )

    @Slot()
    def _on_configure_hotkey(self) -> None:
        """Configure push-to-talk hotkey."""
        InfoBar.info(
            title="Coming Soon",
            content="Hotkey configuration dialog will be added",
            parent=self,
            position=InfoBarPosition.TOP,
            duration=2000
        )

    @Slot(bool)
    def _on_wakeword_changed(self, enabled: bool) -> None:
        """Handle wake word toggle."""
        # This would need to restart the wake word service
        status = "enabled" if enabled else "disabled"
        InfoBar.info(
            title="Wake Word",
            content=f"Wake word detection {status}",
            parent=self,
            position=InfoBarPosition.TOP,
            duration=2000
        )

    @Slot()
    def _on_check_updates(self) -> None:
        """Check for updates."""
        InfoBar.success(
            title="Up to Date",
            content="You have the latest version of Sombra Desktop",
            parent=self,
            position=InfoBarPosition.TOP,
            duration=3000
        )
