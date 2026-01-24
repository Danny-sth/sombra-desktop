# Changelog

All notable changes to Sombra Desktop will be documented in this file.

## [Unreleased]

### Added
- Swarm panel with real-time task management
- Agent monitoring for CODER, DEPLOY, QA agents
- Live agent output streaming via SSE
- Task approval/rejection workflow
- Question handling for agent interactions

## [0.4.2] - 2025-01-19

### Changed
- More compact chat UI
- Show chat history sidebar by default

### Fixed
- Thinking updates now shown in status label

## [0.4.1] - 2025-01-18

### Fixed
- Session management for conversation switching

## [0.4.0] - 2025-01-17

### Changed
- Removed custom SciFi theme, use default qfluentwidgets
- Removed qt_material dependency
- Added window transparency

### Added
- Footer widget with connection indicator
- Agent status cards for Swarm Builder

## [0.3.7] - 2025-01-16

### Added
- ElevenLabs Scribe STT integration
- QA test scenarios
- Expandable log panel (removed LogsPage)

### Changed
- Improved module exports and lint cleanup

## [0.3.0] - 2025-01-15

### Added
- Wake word detection ("Jarvis") via Picovoice Porcupine
- Voice Activity Detection (Silero VAD)
- Auto-send on silence
- Global hotkey support
- Chat history with session management
- System tray integration
- Auto-update from GitHub Releases

### Changed
- Migrated to qfluentwidgets (Fluent Design)
- Multi-page layout (Home, Chat, Agents, Tasks, Devices, Settings, Logs)

## [0.2.0] - 2025-01-10

### Added
- Push-to-talk voice input
- Real-time streaming responses (SSE)
- Local Whisper STT integration
- Basic chat interface

## [0.1.0] - 2025-01-05

### Added
- Initial release
- Qt6 GUI with PySide6
- Basic Sombra API client
- Dark theme
