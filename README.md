# Sombra Desktop

Desktop client for Sombra AI Assistant with voice input, chat, and Swarm task management.

## Features

### Chat & Voice
- **Push-to-talk voice input** with VAD (Voice Activity Detection)
- **Wake word detection** ("Jarvis") via Picovoice Porcupine
- **ElevenLabs Scribe STT** integration (with local Whisper fallback)
- **Real-time streaming responses** (Server-Sent Events)
- **Chat history** with session management
- **Global hotkey** support (default: Ctrl+Shift+S)

### Swarm Agent Orchestration
- **Real-time task monitoring** - Track CODER, DEPLOY, QA agents
- **Live agent output streaming** via SSE
- **Task approval/rejection** workflow
- **Question handling** - Respond to agent questions in real-time
- **Development & QA modes**

### UI
- **Modern Fluent Design** with qfluentwidgets
- **Dark/Light themes**
- **System tray integration**
- **Auto-update** from GitHub Releases
- **Multi-page layout** - Home, Chat, Agents, Tasks, Devices, Settings, Logs

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/Danny-sth/sombra-desktop.git
cd sombra-desktop

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Configuration

Create `.env` file in project root:

```env
# Sombra Backend (Cloud VPS)
SOMBRA_API_URL=http://90.156.230.49:8080
SOMBRA_SESSION_ID=owner

# Swarm Server (runs on PC with Claude Code CLI)
SWARM_API_URL=http://localhost:8082

# STT Service (ElevenLabs Scribe)
ELEVENLABS_API_KEY=your-key-here
STT_URL=http://100.87.46.63:5000/transcribe

# Wake Word (Picovoice Porcupine)
WAKE_WORD_ENABLED=true
PORCUPINE_ACCESS_KEY=your-key-here

# UI Settings
THEME=dark
GLOBAL_HOTKEY=ctrl+shift+s
AUTO_SEND_ON_SILENCE=true
```

### Run

```bash
python -m sombra
```

Or use compiled executable from [Releases](https://github.com/Danny-sth/sombra-desktop/releases).

## Architecture

### Tech Stack
- **PySide6** - Qt6 GUI framework
- **qfluentwidgets** - Microsoft Fluent Design UI components
- **httpx + httpx-sse** - Async HTTP with SSE streaming
- **websockets** - Real-time log streaming to server
- **sounddevice** - Audio capture (requires PortAudio)
- **pynput** - Global hotkeys (requires Xlib on Linux)
- **silero-vad** - Voice Activity Detection
- **pvporcupine** - Wake word detection ("Jarvis")

### Services
- **SombraService** - Chat API client (`/api/chat`, `/api/thinking/stream`)
- **SwarmService** - Agent orchestration client (`/swarm/*`)
- **WhisperService** - STT with ElevenLabs Scribe or local Whisper
- **WakeWordService** - Wake word detection
- **AudioService** - Voice recording
- **UpdateService** - Auto-update from GitHub Releases
- **HotkeyService** - Global hotkey registration

## Platform Support

- **Windows** ✅ (Tested on Windows 11)
- **Linux** ✅ (Tested on Arch Linux)
- **macOS** ⚠️ (Not tested, should work)

## Development

See [BUILD.md](BUILD.md) for build instructions.

## Requirements

- Python 3.10+
- PySide6
- PortAudio (for audio capture)
- Xlib (for global hotkeys on Linux)
- Picovoice account (for wake word detection)
