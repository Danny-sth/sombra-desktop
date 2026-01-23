"""Unit tests for UI components with Sombra branding.

Tests verify:
- StatusCard styling with Sombra colors
- ConnectionStatusCard state changes and colors
- RecordingStatusCard Sombra pink highlight
- ChatBubble Sombra-branded styling
- ThinkingBubble and StreamingBubble styles
- Card hover states and shadows
- Button hover states
"""


from sombra.themes.colors import (
    BORDER_RADIUS,
    DARK_PALETTE,
    SOMBRA_PRIMARY,
    SOMBRA_PRIMARY_LIGHT,
    TRANSPARENCY,
)
from sombra.ui.components.chat_bubble import (
    ChatBubble,
    StreamingBubble,
    ThinkingBubble,
)
from sombra.ui.components.status_card import (
    ConnectionStatusCard,
    RecordingStatusCard,
    StatusCard,
    WakeWordStatusCard,
)
from sombra.ui.styles.theme import SciFiTheme

# RGB values for testing
_PRIMARY_RGB = "233, 69, 96"
_SUCCESS_RGB = "78, 204, 163"
_WARNING_RGB = "249, 168, 37"
_ERROR_RGB = "255, 107, 107"


class TestStatusCardCreation:
    """Tests for StatusCard widget creation."""

    def test_status_card_creation(self, qtbot):
        """Test StatusCard creates successfully."""
        card = StatusCard("Test Title", "Test Value")
        qtbot.addWidget(card)
        assert card is not None

    def test_status_card_has_title(self, qtbot):
        """Test StatusCard displays title."""
        card = StatusCard("Test Title", "Test Value")
        qtbot.addWidget(card)
        assert card._title == "Test Title"
        assert card._title_label.text() == "Test Title"

    def test_status_card_has_value(self, qtbot):
        """Test StatusCard displays value."""
        card = StatusCard("Test Title", "Test Value")
        qtbot.addWidget(card)
        assert card._value == "Test Value"
        assert card._value_label.text() == "Test Value"

    def test_status_card_set_value(self, qtbot):
        """Test StatusCard set_value method."""
        card = StatusCard("Test Title", "Initial Value")
        qtbot.addWidget(card)

        card.set_value("New Value")

        assert card._value == "New Value"
        assert card._value_label.text() == "New Value"


class TestStatusCardStyling:
    """Tests for StatusCard Sombra styling."""

    def test_status_card_has_stylesheet(self, qtbot):
        """Test StatusCard has stylesheet applied."""
        card = StatusCard("Test Title", "Test Value")
        qtbot.addWidget(card)

        stylesheet = card.styleSheet()
        assert stylesheet != ""

    def test_status_card_uses_card_bg(self, qtbot):
        """Test StatusCard uses CARD_BG transparency."""
        card = StatusCard("Test Title", "Test Value")
        qtbot.addWidget(card)

        stylesheet = card.styleSheet()
        assert TRANSPARENCY["card_bg"] in stylesheet

    def test_status_card_uses_sombra_pink_border(self, qtbot):
        """Test StatusCard uses Sombra pink border."""
        card = StatusCard("Test Title", "Test Value")
        qtbot.addWidget(card)

        stylesheet = card.styleSheet()
        assert _PRIMARY_RGB in stylesheet

    def test_status_card_has_border_radius(self, qtbot):
        """Test StatusCard has border radius."""
        card = StatusCard("Test Title", "Test Value")
        qtbot.addWidget(card)

        stylesheet = card.styleSheet()
        assert BORDER_RADIUS["lg"] in stylesheet

    def test_status_card_has_hover_state(self, qtbot):
        """Test StatusCard has hover state."""
        card = StatusCard("Test Title", "Test Value")
        qtbot.addWidget(card)

        stylesheet = card.styleSheet()
        assert ":hover" in stylesheet

    def test_status_card_hover_uses_card_bg_hover(self, qtbot):
        """Test StatusCard hover uses CARD_BG_HOVER."""
        card = StatusCard("Test Title", "Test Value")
        qtbot.addWidget(card)

        stylesheet = card.styleSheet()
        assert TRANSPARENCY["card_bg_hover"] in stylesheet


class TestConnectionStatusCard:
    """Tests for ConnectionStatusCard widget."""

    def test_connection_status_card_creation(self, qtbot):
        """Test ConnectionStatusCard creates successfully."""
        card = ConnectionStatusCard()
        qtbot.addWidget(card)
        assert card is not None

    def test_connection_status_initial_state(self, qtbot):
        """Test ConnectionStatusCard starts with 'Connecting...' status."""
        card = ConnectionStatusCard()
        qtbot.addWidget(card)
        assert card._status == "Connecting..."

    def test_connection_status_set_connected(self, qtbot):
        """Test ConnectionStatusCard set_status to connected."""
        card = ConnectionStatusCard()
        qtbot.addWidget(card)

        card.set_status("Connected")

        assert card._status == "Connected"
        assert card._status_label.text() == "Connected"

    def test_connection_status_connected_uses_success_color(self, qtbot):
        """Test connected state uses success/green color."""
        card = ConnectionStatusCard()
        qtbot.addWidget(card)

        card.set_status("Connected")

        stylesheet = card.styleSheet()
        assert _SUCCESS_RGB in stylesheet

    def test_connection_status_set_error(self, qtbot):
        """Test ConnectionStatusCard set_status to error."""
        card = ConnectionStatusCard()
        qtbot.addWidget(card)

        card.set_status("Error: Connection failed")

        assert "Error" in card._status
        stylesheet = card.styleSheet()
        # Error uses Sombra pink
        assert _PRIMARY_RGB in stylesheet

    def test_connection_status_set_disconnected(self, qtbot):
        """Test ConnectionStatusCard set_status to disconnected."""
        card = ConnectionStatusCard()
        qtbot.addWidget(card)

        card.set_status("Disconnected")

        assert card._status == "Disconnected"

    def test_connection_status_color_constants(self, qtbot):
        """Test ConnectionStatusCard has correct color constants."""
        card = ConnectionStatusCard()
        qtbot.addWidget(card)

        assert card.COLOR_CONNECTED.name() == DARK_PALETTE["success"]
        assert card.COLOR_DISCONNECTED.name() == SOMBRA_PRIMARY
        assert card.COLOR_CONNECTING.name() == DARK_PALETTE["warning"]


class TestRecordingStatusCard:
    """Tests for RecordingStatusCard widget."""

    def test_recording_status_card_creation(self, qtbot):
        """Test RecordingStatusCard creates successfully."""
        card = RecordingStatusCard()
        qtbot.addWidget(card)
        assert card is not None

    def test_recording_status_initial_state(self, qtbot):
        """Test RecordingStatusCard starts in idle state."""
        card = RecordingStatusCard()
        qtbot.addWidget(card)
        assert card._is_recording is False
        assert card._status_label.text() == "Idle"

    def test_recording_status_set_recording_true(self, qtbot):
        """Test RecordingStatusCard set_recording to True."""
        card = RecordingStatusCard()
        qtbot.addWidget(card)

        card.set_recording(True)

        assert card._is_recording is True
        assert card._status_label.text() == "Recording..."

    def test_recording_status_recording_uses_sombra_pink(self, qtbot):
        """Test recording state uses Sombra pink highlight."""
        card = RecordingStatusCard()
        qtbot.addWidget(card)

        card.set_recording(True)

        stylesheet = card.styleSheet()
        assert _PRIMARY_RGB in stylesheet

    def test_recording_status_recording_label_color(self, qtbot):
        """Test recording state label uses Sombra pink."""
        card = RecordingStatusCard()
        qtbot.addWidget(card)

        card.set_recording(True)

        label_style = card._status_label.styleSheet()
        assert SOMBRA_PRIMARY in label_style

    def test_recording_status_set_recording_false(self, qtbot):
        """Test RecordingStatusCard set_recording to False."""
        card = RecordingStatusCard()
        qtbot.addWidget(card)

        card.set_recording(True)
        card.set_recording(False)

        assert card._is_recording is False
        assert card._status_label.text() == "Idle"


class TestWakeWordStatusCard:
    """Tests for WakeWordStatusCard widget."""

    def test_wakeword_status_card_creation(self, qtbot):
        """Test WakeWordStatusCard creates successfully."""
        card = WakeWordStatusCard()
        qtbot.addWidget(card)
        assert card is not None

    def test_wakeword_status_initial_state(self, qtbot):
        """Test WakeWordStatusCard starts in off state."""
        card = WakeWordStatusCard()
        qtbot.addWidget(card)
        assert card._is_listening is False
        assert card._status_label.text() == "Wake Word: Off"

    def test_wakeword_status_set_listening_true(self, qtbot):
        """Test WakeWordStatusCard set_listening to True."""
        card = WakeWordStatusCard()
        qtbot.addWidget(card)

        card.set_listening(True)

        assert card._is_listening is True
        assert card._status_label.text() == "Wake Word: Listening"

    def test_wakeword_status_listening_uses_success_color(self, qtbot):
        """Test listening state uses success/green color."""
        card = WakeWordStatusCard()
        qtbot.addWidget(card)

        card.set_listening(True)

        stylesheet = card.styleSheet()
        assert _SUCCESS_RGB in stylesheet


class TestChatBubbleCreation:
    """Tests for ChatBubble widget creation."""

    def test_chat_bubble_creation_user(self, qtbot):
        """Test ChatBubble creates for user message."""
        bubble = ChatBubble("Hello", is_user=True)
        qtbot.addWidget(bubble)
        assert bubble is not None
        assert bubble._is_user is True

    def test_chat_bubble_creation_sombra(self, qtbot):
        """Test ChatBubble creates for Sombra message."""
        bubble = ChatBubble("Hello", is_user=False)
        qtbot.addWidget(bubble)
        assert bubble is not None
        assert bubble._is_user is False

    def test_chat_bubble_has_content(self, qtbot):
        """Test ChatBubble stores content."""
        bubble = ChatBubble("Test content", is_user=True)
        qtbot.addWidget(bubble)
        assert bubble._content == "Test content"

    def test_chat_bubble_set_content(self, qtbot):
        """Test ChatBubble set_content method."""
        bubble = ChatBubble("Initial", is_user=True)
        qtbot.addWidget(bubble)

        bubble.set_content("Updated content")

        assert bubble._content == "Updated content"


class TestChatBubbleStyling:
    """Tests for ChatBubble Sombra styling."""

    def test_user_bubble_has_user_style(self, qtbot):
        """Test user bubble has USER_BUBBLE style."""
        bubble = ChatBubble("Hello", is_user=True)
        qtbot.addWidget(bubble)

        stylesheet = bubble.styleSheet()
        # User style should have PRIMARY_LIGHT_RGB
        assert SciFiTheme.PRIMARY_LIGHT_RGB in stylesheet

    def test_sombra_bubble_has_sombra_style(self, qtbot):
        """Test Sombra bubble has SOMBRA_BUBBLE style."""
        bubble = ChatBubble("Hello", is_user=False)
        qtbot.addWidget(bubble)

        stylesheet = bubble.styleSheet()
        # Sombra style should have PRIMARY_RGB
        assert SciFiTheme.PRIMARY_RGB in stylesheet

    def test_user_bubble_role_label_color(self, qtbot):
        """Test user bubble role label uses lighter pink."""
        bubble = ChatBubble("Hello", is_user=True)
        qtbot.addWidget(bubble)

        label_style = bubble._role_label.styleSheet()
        assert SOMBRA_PRIMARY_LIGHT in label_style

    def test_sombra_bubble_role_label_color(self, qtbot):
        """Test Sombra bubble role label uses primary pink."""
        bubble = ChatBubble("Hello", is_user=False)
        qtbot.addWidget(bubble)

        label_style = bubble._role_label.styleSheet()
        assert SOMBRA_PRIMARY in label_style

    def test_chat_bubble_has_hover_state(self, qtbot):
        """Test ChatBubble has hover state."""
        bubble = ChatBubble("Hello", is_user=True)
        qtbot.addWidget(bubble)

        stylesheet = bubble.styleSheet()
        assert ":hover" in stylesheet

    def test_chat_bubble_content_browser_selection_color(self, qtbot):
        """Test ChatBubble content browser uses Sombra selection color."""
        bubble = ChatBubble("Hello", is_user=True)
        qtbot.addWidget(bubble)

        browser_style = bubble._content_browser.styleSheet()
        assert _PRIMARY_RGB in browser_style

    def test_sombra_bubble_has_play_button(self, qtbot):
        """Test Sombra bubble has play button for TTS."""
        bubble = ChatBubble("Hello", is_user=False)
        qtbot.addWidget(bubble)

        assert hasattr(bubble, '_play_button')
        assert bubble._play_button is not None

    def test_user_bubble_no_play_button(self, qtbot):
        """Test user bubble does not have play button."""
        bubble = ChatBubble("Hello", is_user=True)
        qtbot.addWidget(bubble)

        assert not hasattr(bubble, '_play_button')


class TestChatBubblePlayButton:
    """Tests for ChatBubble play button styling."""

    def test_play_button_has_border_radius(self, qtbot):
        """Test play button has border radius."""
        bubble = ChatBubble("Hello", is_user=False)
        qtbot.addWidget(bubble)

        play_style = bubble._play_button.styleSheet()
        assert "border-radius:" in play_style

    def test_play_button_hover_uses_sombra_pink(self, qtbot):
        """Test play button hover uses Sombra pink."""
        bubble = ChatBubble("Hello", is_user=False)
        qtbot.addWidget(bubble)

        play_style = bubble._play_button.styleSheet()
        assert _PRIMARY_RGB in play_style


class TestThinkingBubble:
    """Tests for ThinkingBubble widget."""

    def test_thinking_bubble_creation(self, qtbot):
        """Test ThinkingBubble creates successfully."""
        bubble = ThinkingBubble()
        qtbot.addWidget(bubble)
        assert bubble is not None

    def test_thinking_bubble_with_text(self, qtbot):
        """Test ThinkingBubble with custom text."""
        bubble = ThinkingBubble("Processing...")
        qtbot.addWidget(bubble)
        assert bubble._text == "Processing..."
        assert bubble._label.text() == "Processing..."

    def test_thinking_bubble_default_text(self, qtbot):
        """Test ThinkingBubble default text."""
        bubble = ThinkingBubble()
        qtbot.addWidget(bubble)
        assert bubble._label.text() == "Thinking..."

    def test_thinking_bubble_set_text(self, qtbot):
        """Test ThinkingBubble set_text method."""
        bubble = ThinkingBubble()
        qtbot.addWidget(bubble)

        bubble.set_text("New text")

        assert bubble._text == "New text"
        assert bubble._label.text() == "New text"

    def test_thinking_bubble_uses_secondary_color(self, qtbot):
        """Test ThinkingBubble uses SECONDARY_RGB."""
        bubble = ThinkingBubble()
        qtbot.addWidget(bubble)

        stylesheet = bubble.styleSheet()
        assert SciFiTheme.SECONDARY_RGB in stylesheet

    def test_thinking_bubble_label_is_italic(self, qtbot):
        """Test ThinkingBubble label is styled italic."""
        bubble = ThinkingBubble()
        qtbot.addWidget(bubble)

        label_style = bubble._label.styleSheet()
        assert "italic" in label_style


class TestStreamingBubble:
    """Tests for StreamingBubble widget."""

    def test_streaming_bubble_creation(self, qtbot):
        """Test StreamingBubble creates successfully."""
        bubble = StreamingBubble()
        qtbot.addWidget(bubble)
        assert bubble is not None

    def test_streaming_bubble_start_streaming(self, qtbot):
        """Test StreamingBubble start_streaming method."""
        bubble = StreamingBubble()
        qtbot.addWidget(bubble)

        bubble.start_streaming()

        assert bubble._is_streaming is True
        assert bubble._content == ""

    def test_streaming_bubble_append_chunk(self, qtbot):
        """Test StreamingBubble append_chunk method."""
        bubble = StreamingBubble()
        qtbot.addWidget(bubble)

        bubble.start_streaming()
        bubble.append_chunk("Hello ")
        bubble.append_chunk("World")

        assert bubble._content == "Hello World"

    def test_streaming_bubble_end_streaming(self, qtbot):
        """Test StreamingBubble end_streaming method."""
        bubble = StreamingBubble()
        qtbot.addWidget(bubble)

        bubble.start_streaming()
        bubble.append_chunk("Test")
        bubble.end_streaming()

        assert bubble._is_streaming is False

    def test_streaming_bubble_clear(self, qtbot):
        """Test StreamingBubble clear method."""
        bubble = StreamingBubble()
        qtbot.addWidget(bubble)

        bubble.start_streaming()
        bubble.append_chunk("Test")
        bubble.clear()

        assert bubble._content == ""

    def test_streaming_bubble_get_content(self, qtbot):
        """Test StreamingBubble get_content method."""
        bubble = StreamingBubble()
        qtbot.addWidget(bubble)

        bubble.start_streaming()
        bubble.append_chunk("Test content")

        assert bubble.get_content() == "Test content"

    def test_streaming_bubble_uses_primary_color(self, qtbot):
        """Test StreamingBubble uses PRIMARY_RGB."""
        bubble = StreamingBubble()
        qtbot.addWidget(bubble)

        stylesheet = bubble.styleSheet()
        assert SciFiTheme.PRIMARY_RGB in stylesheet

    def test_streaming_bubble_role_label_color(self, qtbot):
        """Test StreamingBubble role label uses Sombra primary."""
        bubble = StreamingBubble()
        qtbot.addWidget(bubble)

        label_style = bubble._role_label.styleSheet()
        assert SOMBRA_PRIMARY in label_style


class TestCardShadowConsistency:
    """Tests for consistent shadow usage across cards."""

    def test_status_card_border_color_consistency(self, qtbot):
        """Test StatusCard uses consistent Sombra pink border."""
        card = StatusCard("Test", "Value")
        qtbot.addWidget(card)

        stylesheet = card.styleSheet()
        # Should use same RGB for border
        assert _PRIMARY_RGB in stylesheet

    def test_connection_card_border_changes_with_state(self, qtbot):
        """Test ConnectionStatusCard border changes with state."""
        card = ConnectionStatusCard()
        qtbot.addWidget(card)

        # Connecting state
        card.set_status("Connecting...")
        connecting_style = card.styleSheet()

        # Connected state
        card.set_status("Connected")
        connected_style = card.styleSheet()

        # Error state
        card.set_status("Error")
        error_style = card.styleSheet()

        # Each state should have different border color
        assert _WARNING_RGB in connecting_style
        assert _SUCCESS_RGB in connected_style
        assert _PRIMARY_RGB in error_style


class TestBubbleGradients:
    """Tests for chat bubble gradient backgrounds."""

    def test_sombra_bubble_has_gradient(self, qtbot):
        """Test Sombra bubble has gradient background."""
        bubble = ChatBubble("Hello", is_user=False)
        qtbot.addWidget(bubble)

        stylesheet = bubble.styleSheet()
        assert "qlineargradient" in stylesheet

    def test_user_bubble_has_gradient(self, qtbot):
        """Test user bubble has gradient background."""
        bubble = ChatBubble("Hello", is_user=True)
        qtbot.addWidget(bubble)

        stylesheet = bubble.styleSheet()
        assert "qlineargradient" in stylesheet

    def test_thinking_bubble_has_gradient(self, qtbot):
        """Test thinking bubble has gradient background."""
        bubble = ThinkingBubble()
        qtbot.addWidget(bubble)

        stylesheet = bubble.styleSheet()
        assert "qlineargradient" in stylesheet

    def test_streaming_bubble_has_gradient(self, qtbot):
        """Test streaming bubble has gradient background."""
        bubble = StreamingBubble()
        qtbot.addWidget(bubble)

        stylesheet = bubble.styleSheet()
        assert "qlineargradient" in stylesheet


class TestButtonHoverStates:
    """Tests for button hover states in chat bubbles."""

    def test_play_button_has_hover_state(self, qtbot):
        """Test play button has hover state styling."""
        bubble = ChatBubble("Hello", is_user=False)
        qtbot.addWidget(bubble)

        play_style = bubble._play_button.styleSheet()
        assert ":hover" in play_style

    def test_stop_button_has_hover_state(self, qtbot):
        """Test stop button has hover state styling."""
        bubble = ChatBubble("Hello", is_user=False)
        qtbot.addWidget(bubble)

        stop_style = bubble._stop_button.styleSheet()
        assert ":hover" in stop_style

    def test_button_hover_uses_transparent_pink(self, qtbot):
        """Test button hover uses transparent Sombra pink."""
        bubble = ChatBubble("Hello", is_user=False)
        qtbot.addWidget(bubble)

        play_style = bubble._play_button.styleSheet()
        # Should have rgba with PRIMARY_RGB for hover
        assert _PRIMARY_RGB in play_style
        assert "rgba" in play_style
