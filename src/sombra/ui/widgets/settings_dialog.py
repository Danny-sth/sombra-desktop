"""Settings configuration dialog."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QKeySequenceEdit,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from ...config.settings import get_settings
from ...services.audio_service import AudioService


class SettingsDialog(QDialog):
    """Application settings dialog.

    Allows configuration of:
    - Sombra API endpoint
    - Whisper STT endpoint
    - Theme selection
    - Global hotkey
    - Audio device selection
    """

    # Emitted when settings are saved
    settings_changed = Signal(dict)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)

        self._setup_ui()
        self._load_settings()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # ===== API Settings =====
        api_group = QGroupBox("API Configuration")
        api_layout = QFormLayout(api_group)

        self._sombra_url_input = QLineEdit()
        self._sombra_url_input.setPlaceholderText("http://localhost:8080")
        api_layout.addRow("Sombra API URL:", self._sombra_url_input)

        self._stt_url_input = QLineEdit()
        self._stt_url_input.setPlaceholderText("http://localhost:5000/transcribe")
        api_layout.addRow("Whisper STT URL:", self._stt_url_input)

        self._session_id_input = QLineEdit()
        self._session_id_input.setPlaceholderText("owner")
        api_layout.addRow("Session ID:", self._session_id_input)

        layout.addWidget(api_group)

        # ===== UI Settings =====
        ui_group = QGroupBox("User Interface")
        ui_layout = QFormLayout(ui_group)

        self._theme_combo = QComboBox()
        self._theme_combo.addItems(["dark", "light"])
        ui_layout.addRow("Theme:", self._theme_combo)

        layout.addWidget(ui_group)

        # ===== Hotkey Settings =====
        hotkey_group = QGroupBox("Keyboard Shortcuts")
        hotkey_layout = QFormLayout(hotkey_group)

        self._hotkey_input = QKeySequenceEdit()
        hotkey_layout.addRow("Push-to-talk:", self._hotkey_input)

        layout.addWidget(hotkey_group)

        # ===== Audio Settings =====
        audio_group = QGroupBox("Audio")
        audio_layout = QFormLayout(audio_group)

        self._device_combo = QComboBox()
        self._populate_audio_devices()
        audio_layout.addRow("Input Device:", self._device_combo)

        layout.addWidget(audio_group)

        # ===== Buttons =====
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._save_settings)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

    def _populate_audio_devices(self) -> None:
        """Populate audio device dropdown."""
        self._device_combo.clear()
        self._device_combo.addItem("Default", None)

        try:
            devices = AudioService.get_audio_devices()
            for device in devices:
                self._device_combo.addItem(device["name"], device["id"])
        except Exception:
            pass

    def _load_settings(self) -> None:
        """Populate fields from current settings."""
        settings = get_settings()

        self._sombra_url_input.setText(settings.sombra_api_url)
        self._stt_url_input.setText(settings.stt_url)
        self._session_id_input.setText(settings.sombra_session_id)

        theme_index = self._theme_combo.findText(settings.theme)
        if theme_index >= 0:
            self._theme_combo.setCurrentIndex(theme_index)

        # Set hotkey (convert from string format)
        from PySide6.QtGui import QKeySequence

        hotkey = settings.global_hotkey.replace("+", ", ").replace("ctrl", "Ctrl").replace(
            "shift", "Shift"
        ).replace("alt", "Alt")
        self._hotkey_input.setKeySequence(QKeySequence(hotkey))

        # Set audio device
        if settings.audio_device_id is not None:
            index = self._device_combo.findData(settings.audio_device_id)
            if index >= 0:
                self._device_combo.setCurrentIndex(index)

    def _save_settings(self) -> None:
        """Persist settings and emit signal."""
        new_settings = {
            "sombra_api_url": self._sombra_url_input.text(),
            "stt_url": self._stt_url_input.text(),
            "session_id": self._session_id_input.text(),
            "theme": self._theme_combo.currentText(),
            "hotkey": self._hotkey_input.keySequence().toString(),
            "audio_device_id": self._device_combo.currentData(),
        }

        self.settings_changed.emit(new_settings)
        self.accept()

    def get_settings(self) -> dict:
        """Get current settings from dialog.

        Returns:
            Dictionary of settings values.
        """
        return {
            "sombra_api_url": self._sombra_url_input.text(),
            "stt_url": self._stt_url_input.text(),
            "session_id": self._session_id_input.text(),
            "theme": self._theme_combo.currentText(),
            "hotkey": self._hotkey_input.keySequence().toString(),
            "audio_device_id": self._device_combo.currentData(),
        }
