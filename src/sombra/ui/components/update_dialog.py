"""Update dialog with download progress."""

from PySide6.QtCore import Signal
from qfluentwidgets import (
    BodyLabel,
    MessageBoxBase,
    ProgressBar,
    SubtitleLabel,
    TextEdit,
)


class UpdateAvailableDialog(MessageBoxBase):
    """Dialog shown when update is available."""

    def __init__(self, version: str, release_notes: str, parent=None):
        super().__init__(parent)
        self.version = version

        # Title
        self.titleLabel = SubtitleLabel(f"🚀 Доступно обновление v{version}", self)

        # Release notes
        self.notesLabel = BodyLabel("Что нового:", self)
        self.notesEdit = TextEdit(self)
        self.notesEdit.setPlainText(release_notes or "Нет описания")
        self.notesEdit.setReadOnly(True)
        self.notesEdit.setMaximumHeight(150)

        # Add to layout
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addSpacing(12)
        self.viewLayout.addWidget(self.notesLabel)
        self.viewLayout.addWidget(self.notesEdit)

        # Buttons
        self.yesButton.setText("Обновить")
        self.cancelButton.setText("Позже")

        # Set minimum width
        self.widget.setMinimumWidth(400)


class UpdateProgressDialog(MessageBoxBase):
    """Dialog showing download progress."""

    cancelled = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Title
        self.titleLabel = SubtitleLabel("⬇️ Загрузка обновления...", self)

        # Progress bar
        self.progressBar = ProgressBar(self)
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)

        # Status label
        self.statusLabel = BodyLabel("Подготовка...", self)

        # Add to layout
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addSpacing(16)
        self.viewLayout.addWidget(self.progressBar)
        self.viewLayout.addWidget(self.statusLabel)

        # Hide yes button, only show cancel
        self.yesButton.hide()
        self.cancelButton.setText("Отмена")

        # Set minimum width
        self.widget.setMinimumWidth(400)

    def update_progress(self, downloaded: int, total: int):
        """Update progress bar."""
        if total > 0:
            percent = int(downloaded * 100 / total)
            self.progressBar.setValue(percent)

            # Format size
            downloaded_mb = downloaded / (1024 * 1024)
            total_mb = total / (1024 * 1024)
            self.statusLabel.setText(f"{downloaded_mb:.1f} / {total_mb:.1f} МБ")
        else:
            self.statusLabel.setText(f"{downloaded / (1024 * 1024):.1f} МБ загружено")

    def set_extracting(self):
        """Show extracting state."""
        self.titleLabel.setText("📦 Установка обновления...")
        self.progressBar.setRange(0, 0)  # Indeterminate
        self.statusLabel.setText("Распаковка файлов...")
        self.cancelButton.setEnabled(False)

    def set_ready(self):
        """Show ready to restart state."""
        self.titleLabel.setText("✅ Обновление готово!")
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(100)
        self.statusLabel.setText("Приложение будет перезапущено")

        # Show restart button
        self.yesButton.setText("Перезапустить")
        self.yesButton.show()
        self.cancelButton.hide()

    def __on_cancel_clicked(self):
        """Handle cancel click."""
        self.cancelled.emit()
        self.reject()


class UpdateErrorDialog(MessageBoxBase):
    """Dialog shown when update fails."""

    def __init__(self, error: str, parent=None):
        super().__init__(parent)

        # Title
        self.titleLabel = SubtitleLabel("❌ Ошибка обновления", self)

        # Error message
        self.errorLabel = BodyLabel(error, self)
        self.errorLabel.setWordWrap(True)

        # Add to layout
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addSpacing(12)
        self.viewLayout.addWidget(self.errorLabel)

        # Only OK button
        self.yesButton.setText("OK")
        self.cancelButton.hide()

        # Set minimum width
        self.widget.setMinimumWidth(350)
