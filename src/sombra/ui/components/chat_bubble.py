"""Chat message bubble components with Sombra branding."""

import re

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget, QTextBrowser, QHBoxLayout

from qfluentwidgets import CardWidget, CaptionLabel, isDarkTheme, TransparentToolButton, FluentIcon

from ..styles.theme import SciFiTheme
from sombra.themes.colors import (
    SOMBRA_PRIMARY,
    SOMBRA_PRIMARY_LIGHT,
    SOMBRA_PRIMARY_MUTED,
    BORDER_RADIUS,
    TRANSPARENCY,
)

try:
    import markdown
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import get_lexer_by_name, guess_lexer

    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False


# Sombra brand RGB values
_PRIMARY_RGB = "233, 69, 96"
_PRIMARY_LIGHT_RGB = "255, 107, 138"
_SECONDARY_RGB = "83, 52, 131"


class ChatBubble(CardWidget):
    """Message bubble card for chat display with Sombra branding.

    Supports markdown rendering and syntax highlighting.
    Uses unified Sombra pink (#e94560) as primary accent.
    """

    # Signal emitted when play button is clicked (sends content text for TTS)
    play_requested = Signal(str)
    # Signal emitted when cached audio should be played
    play_audio = Signal(bytes)
    # Signal emitted when stop button is clicked
    stop_requested = Signal()

    def __init__(
        self,
        content: str,
        is_user: bool = False,
        parent: QWidget | None = None
    ):
        super().__init__(parent)

        self._is_user = is_user
        self._content = content
        self._cached_audio: bytes | None = None

        self._setup_ui()
        self._apply_style()

    def _setup_ui(self) -> None:
        """Build the bubble UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # Header row with role label and play button
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        # Role label with Sombra colors
        role_text = "You" if self._is_user else "Sombra"
        self._role_label = CaptionLabel(role_text)

        # Unified Sombra pink for both - lighter for user, primary for Sombra
        role_color = SOMBRA_PRIMARY_LIGHT if self._is_user else SOMBRA_PRIMARY
        self._role_label.setStyleSheet(f"color: {role_color}; font-weight: 600;")

        header_layout.addWidget(self._role_label)
        header_layout.addStretch()

        # Play/Stop buttons (only for Sombra messages)
        if not self._is_user:
            self._play_button = TransparentToolButton(FluentIcon.VOLUME)
            self._play_button.setFixedSize(24, 24)
            self._play_button.setToolTip("Play audio")
            self._play_button.clicked.connect(self._on_play_clicked)
            self._play_button.setStyleSheet(f"""
                TransparentToolButton {{
                    border-radius: {BORDER_RADIUS["sm"]};
                }}
                TransparentToolButton:hover {{
                    background-color: rgba({_PRIMARY_RGB}, 0.12);
                }}
            """)
            header_layout.addWidget(self._play_button)

            self._stop_button = TransparentToolButton(FluentIcon.PAUSE)
            self._stop_button.setFixedSize(24, 24)
            self._stop_button.setToolTip("Stop audio")
            self._stop_button.clicked.connect(self._on_stop_clicked)
            self._stop_button.setStyleSheet(f"""
                TransparentToolButton {{
                    border-radius: {BORDER_RADIUS["sm"]};
                }}
                TransparentToolButton:hover {{
                    background-color: rgba({_PRIMARY_RGB}, 0.12);
                }}
            """)
            header_layout.addWidget(self._stop_button)

        layout.addLayout(header_layout)

        # Content browser (for markdown)
        self._content_browser = QTextBrowser()
        self._content_browser.setOpenExternalLinks(True)
        self._content_browser.setReadOnly(True)
        self._content_browser.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._content_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Style the browser with Sombra selection color
        self._content_browser.setStyleSheet(f"""
            QTextBrowser {{
                background-color: transparent;
                border: none;
                padding: 0;
                selection-background-color: rgba({_PRIMARY_RGB}, 0.35);
                selection-color: #f0f0f0;
            }}
        """)

        # Render content
        self._render_content()

        layout.addWidget(self._content_browser)

    def _apply_style(self) -> None:
        """Apply Sombra bubble styling based on sender."""
        if self._is_user:
            # User bubble - lighter pink accent with glassmorphism
            self.setStyleSheet(SciFiTheme.USER_BUBBLE)
        else:
            # Sombra bubble - primary pink accent with glassmorphism
            self.setStyleSheet(SciFiTheme.SOMBRA_BUBBLE)

    def _render_content(self) -> None:
        """Render markdown content to HTML."""
        if not self._content:
            self._content_browser.clear()
            return

        if HAS_MARKDOWN:
            html = self._render_markdown(self._content)
        else:
            # Fallback: basic HTML escaping
            html = self._content.replace("&", "&amp;")
            html = html.replace("<", "&lt;")
            html = html.replace(">", "&gt;")
            html = html.replace("\n", "<br>")

        # Text color based on theme
        text_color = SciFiTheme.get_text_color(isDarkTheme())

        # Link color uses Sombra primary
        styled_html = f"""
        <style>
            a {{ color: {SOMBRA_PRIMARY}; text-decoration: none; }}
            a:hover {{ color: {SOMBRA_PRIMARY_LIGHT}; text-decoration: underline; }}
            code {{ background-color: rgba({_PRIMARY_RGB}, 0.10); padding: 2px 6px; border-radius: 4px; }}
        </style>
        <div style="font-family: 'Segoe UI', sans-serif; font-size: 14px;
                    line-height: 1.6; color: {text_color};">
            {html}
        </div>
        """

        self._content_browser.setHtml(styled_html)

        # Adjust height to content
        doc = self._content_browser.document()
        doc.setTextWidth(self._content_browser.viewport().width())
        height = int(doc.size().height()) + 10
        self._content_browser.setMinimumHeight(min(height, 400))
        self._content_browser.setMaximumHeight(max(height, 50))

    def _render_markdown(self, content: str) -> str:
        """Convert markdown to HTML with syntax highlighting."""
        # Process code blocks for syntax highlighting
        content = self._highlight_code_blocks(content)

        # Convert markdown to HTML
        html = markdown.markdown(
            content,
            extensions=["fenced_code", "tables", "nl2br"],
        )

        return html

    def _highlight_code_blocks(self, content: str) -> str:
        """Apply syntax highlighting to code blocks with Sombra-themed styling."""
        if not HAS_MARKDOWN:
            return content

        def highlight_match(match: re.Match) -> str:
            language = match.group(1) or ""
            code = match.group(2)

            try:
                if language:
                    lexer = get_lexer_by_name(language)
                else:
                    lexer = guess_lexer(code)

                formatter = HtmlFormatter(
                    style="monokai",
                    noclasses=True,
                    nowrap=True,
                )
                highlighted = highlight(code, lexer, formatter)

                # Sombra-styled code block with rounded corners
                return f'''<pre style="background-color: #12121f; padding: 12px;
                    border-radius: {BORDER_RADIUS["md"]}; overflow-x: auto; margin: 8px 0;
                    border: 1px solid rgba({_PRIMARY_RGB}, 0.15);"><code>{highlighted}</code></pre>'''

            except Exception:
                escaped = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                return f'''<pre style="background-color: #12121f; padding: 12px;
                    border-radius: {BORDER_RADIUS["md"]};
                    border: 1px solid rgba({_PRIMARY_RGB}, 0.15);"><code>{escaped}</code></pre>'''

        pattern = r"```(\w*)\n(.*?)```"
        return re.sub(pattern, highlight_match, content, flags=re.DOTALL)

    def set_content(self, content: str) -> None:
        """Update the bubble content."""
        self._content = content
        self._render_content()

    def append_content(self, chunk: str) -> None:
        """Append content for streaming."""
        self._content += chunk
        self._render_content()

    def _on_play_clicked(self) -> None:
        """Handle play button click."""
        if self._cached_audio:
            # Use cached audio
            self.play_audio.emit(self._cached_audio)
        elif self._content:
            # Request TTS synthesis
            self.play_requested.emit(self._content)

    def _on_stop_clicked(self) -> None:
        """Handle stop button click."""
        self.stop_requested.emit()

    def set_audio(self, audio: bytes) -> None:
        """Cache audio data for this bubble."""
        self._cached_audio = audio

    def has_audio(self) -> bool:
        """Check if audio is cached."""
        return self._cached_audio is not None


class ThinkingBubble(CardWidget):
    """Thinking indicator bubble with Sombra styling."""

    def __init__(self, text: str = "", parent: QWidget | None = None):
        super().__init__(parent)

        self._text = text

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        # Thinking label with muted Sombra color
        self._label = CaptionLabel(text if text else "Thinking...")
        self._label.setStyleSheet(f"color: {SciFiTheme.TEXT_SECONDARY}; font-style: italic;")
        layout.addWidget(self._label)
        layout.addStretch()

        # Sombra-branded thinking style
        self.setStyleSheet(SciFiTheme.THINKING_BUBBLE)

    def set_text(self, text: str) -> None:
        """Update thinking text."""
        self._text = text
        self._label.setText(text)


class StreamingBubble(CardWidget):
    """Bubble for streaming responses with Sombra styling."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._content = ""
        self._is_streaming = False

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Build the streaming bubble UI with Sombra styling."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # Role label with Sombra primary accent
        self._role_label = CaptionLabel("Sombra")
        self._role_label.setStyleSheet(f"color: {SOMBRA_PRIMARY}; font-weight: 600;")
        layout.addWidget(self._role_label)

        # Content browser with transparent background
        self._content_browser = QTextBrowser()
        self._content_browser.setOpenExternalLinks(True)
        self._content_browser.setReadOnly(True)
        self._content_browser.setStyleSheet(f"""
            QTextBrowser {{
                background-color: transparent;
                border: none;
                padding: 0;
                selection-background-color: rgba({_PRIMARY_RGB}, 0.35);
                selection-color: #f0f0f0;
            }}
        """)
        layout.addWidget(self._content_browser)

        # Sombra streaming style
        self.setStyleSheet(SciFiTheme.STREAMING_BUBBLE)

    def start_streaming(self) -> None:
        """Start streaming mode."""
        self._is_streaming = True
        self._content = ""
        self._content_browser.clear()

    def append_chunk(self, chunk: str) -> None:
        """Append a streaming chunk."""
        self._content += chunk
        self._render()

    def set_content(self, content: str) -> None:
        """Set full content."""
        self._content = content
        self._render()

    def end_streaming(self) -> None:
        """End streaming mode."""
        self._is_streaming = False

    def _render(self) -> None:
        """Render content."""
        if not self._content:
            return

        text_color = SciFiTheme.get_text_color(isDarkTheme())

        if HAS_MARKDOWN:
            # Process markdown
            html = markdown.markdown(
                self._content,
                extensions=["fenced_code", "tables", "nl2br"],
            )
        else:
            html = self._content.replace("\n", "<br>")

        # Sombra-styled HTML with link colors
        styled_html = f"""
        <style>
            a {{ color: {SOMBRA_PRIMARY}; text-decoration: none; }}
            a:hover {{ color: {SOMBRA_PRIMARY_LIGHT}; text-decoration: underline; }}
            code {{ background-color: rgba({_PRIMARY_RGB}, 0.10); padding: 2px 6px; border-radius: 4px; }}
        </style>
        <div style="font-family: 'Segoe UI', sans-serif; font-size: 14px;
                    line-height: 1.6; color: {text_color};">
            {html}
        </div>
        """

        self._content_browser.setHtml(styled_html)

        # Auto-scroll
        scrollbar = self._content_browser.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear(self) -> None:
        """Clear content."""
        self._content = ""
        self._content_browser.clear()

    def get_content(self) -> str:
        """Get current content."""
        return self._content
