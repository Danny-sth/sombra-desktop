# Sombra Desktop

Voice-enabled AI assistant desktop application for Sombra.

## Features

- Push-to-talk voice input
- Local Whisper STT integration
- Real-time streaming responses (SSE)
- Modern Material-like dark/light themes
- Global hotkey support
- System tray integration

## Installation

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install
pip install -e .
```

## Configuration

Copy `.env.example` to `.env` and configure:

```env
SOMBRA_API_URL=http://localhost:8080
SOMBRA_SESSION_ID=owner
STT_URL=http://100.87.46.63:5000/transcribe
THEME=dark
GLOBAL_HOTKEY=ctrl+shift+s
```

## Usage

```bash
python -m sombra
```

## Requirements

- Python 3.10+
- PySide6
- PortAudio (for audio capture)
- Xlib (for global hotkeys on Linux)
