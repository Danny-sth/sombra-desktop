"""Streaming output display widget with markdown rendering."""

import re

from PySide6.QtCore import Slot
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QTextBrowser, QVBoxLayout, QWidget

try:
    import markdown
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import get_lexer_by_name, guess_lexer

    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False


class OutputDisplay(QWidget):
    """Streaming markdown display with auto-scroll and syntax highlighting.

    Features:
    - Real-time streaming text display
    - Markdown rendering
    - Code syntax highlighting
    - Auto-scroll to bottom
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._content_buffer = ""
        self._auto_scroll = True
        self._is_streaming = False

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Main text browser for rendered output
        self._text_browser = QTextBrowser()
        self._text_browser.setOpenExternalLinks(True)
        self._text_browser.setReadOnly(True)

        # Set placeholder text
        self._text_browser.setPlaceholderText(
            "Sombra response will appear here...\n\n"
            "Press and hold the microphone button to speak."
        )

        layout.addWidget(self._text_browser)

    @property
    def auto_scroll(self) -> bool:
        """Get auto-scroll state."""
        return self._auto_scroll

    @auto_scroll.setter
    def auto_scroll(self, enabled: bool) -> None:
        """Set auto-scroll state."""
        self._auto_scroll = enabled

    @Slot(str)
    def append_chunk(self, chunk: str) -> None:
        """Append a streaming chunk and re-render.

        Args:
            chunk: Text chunk to append.
        """
        self._content_buffer += chunk
        self._render_content()

    @Slot(str)
    def set_content(self, content: str) -> None:
        """Set the full content (replacing existing).

        Args:
            content: Full content text.
        """
        self._content_buffer = content
        self._render_content()

    @Slot(str)
    def append_thinking(self, thinking: str) -> None:
        """Append a thinking update (styled differently).

        Args:
            thinking: Thinking text to append.
        """
        # Add thinking with special styling
        thinking_html = f'<p style="color: #a0a0a0; font-style: italic;">{thinking}</p>'
        cursor = self._text_browser.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(thinking_html)

        if self._auto_scroll:
            self._scroll_to_bottom()

    @Slot()
    def clear(self) -> None:
        """Clear display content."""
        self._content_buffer = ""
        self._text_browser.clear()
        self._is_streaming = False

    @Slot()
    def start_streaming(self) -> None:
        """Mark the start of a new streaming response."""
        self._is_streaming = True
        self.clear()

    @Slot()
    def end_streaming(self) -> None:
        """Mark the end of streaming."""
        self._is_streaming = False

    def _render_content(self) -> None:
        """Render markdown content to HTML."""
        if not self._content_buffer:
            self._text_browser.clear()
            return

        if HAS_MARKDOWN:
            html = self._render_markdown(self._content_buffer)
        else:
            # Fallback: basic HTML escaping with line breaks
            html = self._content_buffer.replace("&", "&amp;")
            html = html.replace("<", "&lt;")
            html = html.replace(">", "&gt;")
            html = html.replace("\n", "<br>")

        # Add styling wrapper
        styled_html = f"""
        <div style="font-family: 'Segoe UI', sans-serif; font-size: 14px; line-height: 1.6;">
            {html}
        </div>
        """

        self._text_browser.setHtml(styled_html)

        if self._auto_scroll:
            self._scroll_to_bottom()

    def _render_markdown(self, content: str) -> str:
        """Convert markdown to HTML with syntax highlighting.

        Args:
            content: Markdown content.

        Returns:
            HTML string.
        """
        # Process code blocks for syntax highlighting
        content = self._highlight_code_blocks(content)

        # Convert markdown to HTML
        html = markdown.markdown(
            content,
            extensions=["fenced_code", "tables", "nl2br"],
        )

        return html

    def _highlight_code_blocks(self, content: str) -> str:
        """Apply syntax highlighting to code blocks.

        Args:
            content: Content with code blocks.

        Returns:
            Content with highlighted code blocks.
        """
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

                return (
                    '<pre style="background-color: #1e1e1e; padding: 12px; '
                    f'border-radius: 6px; overflow-x: auto;"><code>{highlighted}</code></pre>'
                )

            except Exception:
                # Fallback to plain code block
                escaped = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                return (
                    '<pre style="background-color: #1e1e1e; padding: 12px; '
                    f'border-radius: 6px;"><code>{escaped}</code></pre>'
                )

        # Match fenced code blocks
        pattern = r"```(\w*)\n(.*?)```"
        return re.sub(pattern, highlight_match, content, flags=re.DOTALL)

    def _scroll_to_bottom(self) -> None:
        """Scroll to the bottom of the display."""
        scrollbar = self._text_browser.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def set_auto_scroll(self, enabled: bool) -> None:
        """Toggle auto-scroll behavior.

        Args:
            enabled: Whether to auto-scroll.
        """
        self._auto_scroll = enabled

    def get_content(self) -> str:
        """Get the current content buffer.

        Returns:
            Current content text.
        """
        return self._content_buffer
