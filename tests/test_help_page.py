"""Unit tests for HelpPage component.

Tests verify:
- Page structure and layout
- Header section with title and subtitle
- Keyboard shortcuts section with all expected shortcuts
- Voice activation section
- Getting Started section with steps
- Tips & Tricks section
- Navigation integration
"""

from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout
from qfluentwidgets import (
    BodyLabel,
    ScrollArea,
    SettingCard,
    SettingCardGroup,
    SimpleCardWidget,
    SubtitleLabel,
    TitleLabel,
)


class TestHelpPageBasicStructure:
    """Tests for HelpPage basic structure and setup."""

    @pytest.fixture
    def settings_mock(self):
        """Mock settings for HelpPage."""
        mock = MagicMock()
        mock.global_hotkey = "ctrl+shift+s"
        mock.wake_word = "jarvis"
        return mock

    @pytest.fixture
    def page(self, qtbot, settings_mock):
        """Create a HelpPage instance for testing."""
        with patch("sombra.ui.pages.help_page.get_settings", return_value=settings_mock):
            from sombra.ui.pages.help_page import HelpPage
            page = HelpPage()
            qtbot.addWidget(page)
            return page

    def test_page_creation(self, page):
        """Test page creates successfully."""
        assert page is not None

    def test_page_object_name(self, page):
        """Test page has correct object name."""
        assert page.objectName() == "helpPage"

    def test_page_is_scroll_area(self, page):
        """Test page inherits from ScrollArea."""
        assert isinstance(page, ScrollArea)

    def test_page_widget_resizable(self, page):
        """Test page widget is resizable."""
        assert page.widgetResizable() is True

    def test_page_horizontal_scrollbar_disabled(self, page):
        """Test horizontal scrollbar is always off."""
        assert page.horizontalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAlwaysOff

    def test_page_has_container(self, page):
        """Test page has a container widget."""
        assert page.container is not None
        assert page.widget() == page.container

    def test_container_layout_is_vertical(self, page):
        """Test container uses vertical layout."""
        layout = page.container.layout()
        assert isinstance(layout, QVBoxLayout)

    def test_container_layout_margins(self, page):
        """Test container layout has correct margins."""
        layout = page.container.layout()
        margins = layout.contentsMargins()
        assert margins.left() == 36
        assert margins.top() == 20
        assert margins.right() == 36
        assert margins.bottom() == 20

    def test_container_layout_spacing(self, page):
        """Test container layout has correct spacing."""
        layout = page.container.layout()
        assert layout.spacing() == 24


class TestHelpPageHeader:
    """Tests for HelpPage header section."""

    @pytest.fixture
    def settings_mock(self):
        """Mock settings for HelpPage."""
        mock = MagicMock()
        mock.global_hotkey = "ctrl+shift+s"
        mock.wake_word = "jarvis"
        return mock

    @pytest.fixture
    def page(self, qtbot, settings_mock):
        """Create a HelpPage instance for testing."""
        with patch("sombra.ui.pages.help_page.get_settings", return_value=settings_mock):
            from sombra.ui.pages.help_page import HelpPage
            page = HelpPage()
            qtbot.addWidget(page)
            return page

    def test_header_title_exists(self, page):
        """Test page has a title label."""
        titles = page.findChildren(TitleLabel)
        assert len(titles) >= 1

    def test_header_title_text(self, page):
        """Test title text is correct."""
        titles = page.findChildren(TitleLabel)
        title_texts = [t.text() for t in titles]
        assert "Help & Shortcuts" in title_texts

    def test_header_has_subtitle(self, page):
        """Test page has a subtitle/description."""
        body_labels = page.findChildren(BodyLabel)
        # First BodyLabel after title should be the description
        assert len(body_labels) >= 1


class TestHelpPageKeyboardShortcuts:
    """Tests for keyboard shortcuts section."""

    @pytest.fixture
    def settings_mock(self):
        """Mock settings for HelpPage."""
        mock = MagicMock()
        mock.global_hotkey = "ctrl+shift+s"
        mock.wake_word = "jarvis"
        return mock

    @pytest.fixture
    def page(self, qtbot, settings_mock):
        """Create a HelpPage instance for testing."""
        with patch("sombra.ui.pages.help_page.get_settings", return_value=settings_mock):
            from sombra.ui.pages.help_page import HelpPage
            page = HelpPage()
            qtbot.addWidget(page)
            return page

    def test_setting_card_groups_exist(self, page):
        """Test SettingCardGroups are created."""
        groups = page.findChildren(SettingCardGroup)
        assert len(groups) >= 2  # At least Keyboard Shortcuts and Voice Activation

    def test_setting_cards_exist(self, page):
        """Test SettingCards for shortcuts are created."""
        cards = page.findChildren(SettingCard)
        assert len(cards) >= 4  # At least 4 keyboard shortcuts + 2 voice

    def test_push_to_talk_shortcut_exists(self, page):
        """Test Push-to-Talk shortcut card exists."""
        cards = page.findChildren(SettingCard)
        card_titles = [c.titleLabel.text() for c in cards if hasattr(c, 'titleLabel')]
        assert "Push-to-Talk" in card_titles

    def test_send_message_shortcut_exists(self, page):
        """Test Send Message shortcut card exists."""
        cards = page.findChildren(SettingCard)
        card_titles = [c.titleLabel.text() for c in cards if hasattr(c, 'titleLabel')]
        assert "Send Message" in card_titles

    def test_new_line_shortcut_exists(self, page):
        """Test New Line shortcut card exists."""
        cards = page.findChildren(SettingCard)
        card_titles = [c.titleLabel.text() for c in cards if hasattr(c, 'titleLabel')]
        assert "New Line" in card_titles

    def test_cancel_recording_shortcut_exists(self, page):
        """Test Cancel Recording shortcut card exists."""
        cards = page.findChildren(SettingCard)
        card_titles = [c.titleLabel.text() for c in cards if hasattr(c, 'titleLabel')]
        assert "Cancel Recording" in card_titles

    def test_push_to_talk_shows_configured_hotkey(self, page, settings_mock):
        """Test Push-to-Talk shows the configured hotkey."""
        cards = page.findChildren(SettingCard)
        ptt_card = None
        for card in cards:
            if hasattr(card, 'titleLabel') and card.titleLabel.text() == "Push-to-Talk":
                ptt_card = card
                break

        assert ptt_card is not None
        # The content label should contain the hotkey
        if hasattr(ptt_card, 'contentLabel'):
            content = ptt_card.contentLabel.text().upper()
            # Hotkey is "ctrl+shift+s" -> should show "CTRL + SHIFT + S"
            assert "CTRL" in content or "SHIFT" in content


class TestHelpPageVoiceSection:
    """Tests for voice activation section."""

    @pytest.fixture
    def settings_mock(self):
        """Mock settings for HelpPage."""
        mock = MagicMock()
        mock.global_hotkey = "ctrl+shift+s"
        mock.wake_word = "jarvis"
        return mock

    @pytest.fixture
    def page(self, qtbot, settings_mock):
        """Create a HelpPage instance for testing."""
        with patch("sombra.ui.pages.help_page.get_settings", return_value=settings_mock):
            from sombra.ui.pages.help_page import HelpPage
            page = HelpPage()
            qtbot.addWidget(page)
            return page

    def test_wake_word_card_exists(self, page):
        """Test wake word card exists."""
        cards = page.findChildren(SettingCard)
        card_titles = [c.titleLabel.text() for c in cards if hasattr(c, 'titleLabel')]
        # Wake word card shows 'Say "Jarvis"'
        assert any("Say" in title for title in card_titles)

    def test_wake_word_shows_configured_word(self, page, settings_mock):
        """Test wake word card shows the configured wake word."""
        cards = page.findChildren(SettingCard)
        for card in cards:
            if hasattr(card, 'titleLabel') and "Say" in card.titleLabel.text():
                # Should contain the capitalized wake word
                assert "Jarvis" in card.titleLabel.text()
                break

    def test_vad_auto_stop_card_exists(self, page):
        """Test Auto-Stop Recording (VAD) card exists."""
        cards = page.findChildren(SettingCard)
        card_titles = [c.titleLabel.text() for c in cards if hasattr(c, 'titleLabel')]
        assert "Auto-Stop Recording" in card_titles


class TestHelpPageUsageSection:
    """Tests for Getting Started usage section."""

    @pytest.fixture
    def settings_mock(self):
        """Mock settings for HelpPage."""
        mock = MagicMock()
        mock.global_hotkey = "ctrl+shift+s"
        mock.wake_word = "jarvis"
        return mock

    @pytest.fixture
    def page(self, qtbot, settings_mock):
        """Create a HelpPage instance for testing."""
        with patch("sombra.ui.pages.help_page.get_settings", return_value=settings_mock):
            from sombra.ui.pages.help_page import HelpPage
            page = HelpPage()
            qtbot.addWidget(page)
            return page

    def test_getting_started_section_exists(self, page):
        """Test Getting Started section title exists."""
        subtitles = page.findChildren(SubtitleLabel)
        subtitle_texts = [s.text() for s in subtitles]
        assert "Getting Started" in subtitle_texts

    def test_usage_card_exists(self, page):
        """Test usage instructions card exists."""
        cards = page.findChildren(SimpleCardWidget)
        assert len(cards) >= 1

    def test_usage_has_step_numbers(self, page):
        """Test usage section has numbered steps."""
        # Check for step numbers (1, 2, 3, 4) in BodyLabels
        body_labels = page.findChildren(BodyLabel)
        step_numbers = ["1", "2", "3", "4"]
        found_numbers = []
        for label in body_labels:
            text = label.text().strip()
            if text in step_numbers:
                found_numbers.append(text)

        # Should have at least 4 step numbers
        assert len(found_numbers) >= 4


class TestHelpPageTipsSection:
    """Tests for Tips & Tricks section."""

    @pytest.fixture
    def settings_mock(self):
        """Mock settings for HelpPage."""
        mock = MagicMock()
        mock.global_hotkey = "ctrl+shift+s"
        mock.wake_word = "jarvis"
        return mock

    @pytest.fixture
    def page(self, qtbot, settings_mock):
        """Create a HelpPage instance for testing."""
        with patch("sombra.ui.pages.help_page.get_settings", return_value=settings_mock):
            from sombra.ui.pages.help_page import HelpPage
            page = HelpPage()
            qtbot.addWidget(page)
            return page

    def test_tips_section_exists(self, page):
        """Test Tips & Tricks section title exists."""
        subtitles = page.findChildren(SubtitleLabel)
        subtitle_texts = [s.text() for s in subtitles]
        assert "Tips & Tricks" in subtitle_texts

    def test_tips_card_exists(self, page):
        """Test tips card exists."""
        # There should be SimpleCardWidgets for tips
        cards = page.findChildren(SimpleCardWidget)
        assert len(cards) >= 2  # One for usage, one for tips


class TestHelpPageNavigation:
    """Tests for Help page navigation integration."""

    def test_help_page_imported_in_main_window(self):
        """Test HelpPage is imported in main_window module."""
        # Read main_window.py and check import
        with open("src/sombra/ui/main_window.py", "r") as f:
            content = f.read()

        assert "from .pages.help_page import HelpPage" in content

    def test_help_page_instantiated_in_main_window(self):
        """Test HelpPage is instantiated in MainWindow."""
        with open("src/sombra/ui/main_window.py", "r") as f:
            content = f.read()

        assert "self.help_page = HelpPage" in content

    def test_help_page_added_to_navigation(self):
        """Test HelpPage is added to sidebar navigation."""
        with open("src/sombra/ui/main_window.py", "r") as f:
            content = f.read()

        # Check that help_page is added with addSubInterface
        assert "self.help_page" in content
        assert "FluentIcon.HELP" in content

    def test_help_page_uses_bottom_position(self):
        """Test HelpPage is positioned at BOTTOM of navigation."""
        with open("src/sombra/ui/main_window.py", "r") as f:
            content = f.read()

        # Check that BOTTOM position is used
        assert "NavigationItemPosition.BOTTOM" in content


class TestHelpPageDifferentSettings:
    """Tests for Help page with different settings values."""

    def test_with_different_hotkey(self, qtbot):
        """Test page displays different configured hotkey."""
        mock = MagicMock()
        mock.global_hotkey = "alt+space"
        mock.wake_word = "sombra"

        with patch("sombra.ui.pages.help_page.get_settings", return_value=mock):
            from sombra.ui.pages.help_page import HelpPage
            page = HelpPage()
            qtbot.addWidget(page)

        # Find Push-to-Talk card and verify content
        cards = page.findChildren(SettingCard)
        for card in cards:
            if hasattr(card, 'titleLabel') and card.titleLabel.text() == "Push-to-Talk":
                if hasattr(card, 'contentLabel'):
                    content = card.contentLabel.text().upper()
                    assert "ALT" in content or "SPACE" in content
                break

    def test_with_different_wake_word(self, qtbot):
        """Test page displays different configured wake word."""
        mock = MagicMock()
        mock.global_hotkey = "ctrl+shift+s"
        mock.wake_word = "computer"

        with patch("sombra.ui.pages.help_page.get_settings", return_value=mock):
            from sombra.ui.pages.help_page import HelpPage
            page = HelpPage()
            qtbot.addWidget(page)

        # Find wake word card
        cards = page.findChildren(SettingCard)
        for card in cards:
            if hasattr(card, 'titleLabel') and "Say" in card.titleLabel.text():
                assert "Computer" in card.titleLabel.text()
                break


class TestHelpPageEdgeCases:
    """Edge case tests for HelpPage."""

    def test_with_empty_hotkey(self, qtbot):
        """Test page handles empty hotkey gracefully."""
        mock = MagicMock()
        mock.global_hotkey = ""
        mock.wake_word = "jarvis"

        with patch("sombra.ui.pages.help_page.get_settings", return_value=mock):
            from sombra.ui.pages.help_page import HelpPage
            # Should not raise an exception
            page = HelpPage()
            qtbot.addWidget(page)
            assert page is not None

    def test_with_empty_wake_word(self, qtbot):
        """Test page handles empty wake word gracefully."""
        mock = MagicMock()
        mock.global_hotkey = "ctrl+shift+s"
        mock.wake_word = ""

        with patch("sombra.ui.pages.help_page.get_settings", return_value=mock):
            from sombra.ui.pages.help_page import HelpPage
            # Should not raise an exception
            page = HelpPage()
            qtbot.addWidget(page)
            assert page is not None

    def test_page_is_scrollable(self, qtbot):
        """Test page content is scrollable."""
        mock = MagicMock()
        mock.global_hotkey = "ctrl+shift+s"
        mock.wake_word = "jarvis"

        with patch("sombra.ui.pages.help_page.get_settings", return_value=mock):
            from sombra.ui.pages.help_page import HelpPage
            page = HelpPage()
            qtbot.addWidget(page)

        # ScrollArea should be properly configured
        assert page.widgetResizable() is True
        assert page.widget() is not None

    def test_multiple_instantiation(self, qtbot):
        """Test multiple HelpPage instances can be created."""
        mock = MagicMock()
        mock.global_hotkey = "ctrl+shift+s"
        mock.wake_word = "jarvis"

        with patch("sombra.ui.pages.help_page.get_settings", return_value=mock):
            from sombra.ui.pages.help_page import HelpPage
            pages = []
            for _ in range(3):
                page = HelpPage()
                qtbot.addWidget(page)
                pages.append(page)

        assert len(pages) == 3
        for page in pages:
            assert page is not None
            assert page.objectName() == "helpPage"
