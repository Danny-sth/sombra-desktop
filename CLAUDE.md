# Sombra Desktop - Project Documentation

## Infrastructure

### Sombra Cloud Server (VPS)
- **Host:** 90.156.230.49
- **SSH:** `ssh root@90.156.230.49`
- **Password:** `iUS*gYXa-+3h-R`
- **Sombra API:** http://90.156.230.49:8080
- **Services:**
  - sombra.service (Python/FastAPI, port 8080)
  - sombra-postgres (Docker, port 5432)

### Local Whisper STT
- **URL:** http://100.87.46.63:5000/transcribe
- **Method:** POST multipart/form-data with audio file

## API Endpoints

### Sombra Backend (VPS - port 8080)

#### Chat
```
POST /api/chat
Body: {"query": "text", "session_id": "unique-id"}
Response: {"response": "...", "session_id": "..."}
```

#### Thinking Stream (SSE)
```
GET /api/thinking/stream/{sessionId}
Returns: Server-Sent Events with real-time thinking updates
```

#### Client Logs (WebSocket)
```
WS /api/logs/stream - клиент отправляет логи в реалтайме (WRITE)
WS /api/logs/watch - читать логи в реалтайме (READ)
GET /api/logs/watch/sse - SSE альтернатива для чтения логов
GET /api/logs/clients - подключённые клиенты
GET /api/logs/buffer - последние логи от всех клиентов
GET /api/logs/buffer/{client_id} - логи конкретного клиента
```

#### System
```
GET /api/system/version - Build info
GET /health - Health check
```

### Swarm Server (PC - port 8082)

#### Task Management
```
POST /swarm/start
Body: {"description": "task", "mode": "development|qa", "qa_context": {...}}
Response: {"task_id": "...", "status": "..."}

POST /swarm/approve/{task_id}
POST /swarm/reject/{task_id}
Body: {"feedback": "optional feedback"}

POST /swarm/stop/{task_id}
POST /swarm/answer/{task_id}
Body: {"question_id": "...", "answer": "..."}
```

#### Status Monitoring (SSE)
```
GET /swarm/status/stream/{task_id}
Returns: Server-Sent Events with task status updates

GET /swarm/output/stream/{task_id}
Returns: Server-Sent Events with agent output
```

#### Current State
```
GET /swarm/status/{task_id}
GET /swarm/current - Current task info
```

## Configuration

Edit `.env` file:
```env
# Sombra Backend (Cloud VPS)
SOMBRA_API_URL=http://90.156.230.49:8080
SOMBRA_SESSION_ID=owner

# Swarm Server (runs on PC with Claude Code CLI)
SWARM_API_URL=http://localhost:8082

# STT Service (ElevenLabs Scribe)
ELEVENLABS_API_KEY=sk_xxx...
STT_URL=http://100.87.46.63:5000/transcribe

# Wake Word Settings (Picovoice Porcupine)
WAKE_WORD_ENABLED=true
PORCUPINE_ACCESS_KEY=xxx...

# UI Settings
THEME=dark
GLOBAL_HOTKEY=ctrl+shift+s
AUTO_SEND_ON_SILENCE=true

# Audio Settings (optional)
# AUDIO_DEVICE_ID=0
# AUDIO_SAMPLE_RATE=16000

# System Tray (optional)
# MINIMIZE_TO_TRAY=true
# START_MINIMIZED=false
```

## Running

```bash
cd /home/danny/Documents/projects/sombra-desktop
source .venv/bin/activate
python -m sombra
```

## Architecture

### Core Technologies
- **PySide6** - Qt6 GUI framework
- **qfluentwidgets** - Microsoft Fluent Design UI components
- **httpx + httpx-sse** - Async HTTP client with SSE streaming support
- **websockets** - Real-time log streaming to server
- **sounddevice** - Audio capture (requires PortAudio)
- **pynput** - Global hotkey registration (requires Xlib on Linux)
- **silero-vad** - Voice Activity Detection (PyTorch-based)
- **pvporcupine** - Wake word detection ("Jarvis")

### Services Architecture

```
┌─────────────────────────────────────────────────┐
│            Sombra Desktop (Qt6 GUI)             │
├─────────────────────────────────────────────────┤
│  Pages:                                         │
│  • Home     - Welcome & status dashboard        │
│  • Chat     - Conversation with Sombra          │
│  • Agents   - Swarm agent monitoring            │
│  • Tasks    - Task history & management         │
│  • Devices  - Audio device selection            │
│  • Settings - Configuration                     │
│  • Logs     - Real-time log viewer              │
├─────────────────────────────────────────────────┤
│  Services:                                      │
│  • SombraService   → Sombra Backend (VPS:8080)  │
│  • SwarmService    → Swarm Server (PC:8082)     │
│  • WhisperService  → STT (ElevenLabs/Whisper)   │
│  • WakeWordService → Porcupine                  │
│  • AudioService    → sounddevice                │
│  • UpdateService   → GitHub Releases            │
│  • HotkeyService   → Global hotkeys             │
└─────────────────────────────────────────────────┘
         ↓ HTTP/SSE          ↓ HTTP/SSE
┌────────────────────┐  ┌──────────────────────┐
│  Sombra Backend    │  │   Swarm Server       │
│  (FastAPI/VPS)     │  │   (FastAPI/PC)       │
│  Port 8080         │  │   Port 8082          │
│  • Chat API        │  │   • Task orchestr.   │
│  • Thinking SSE    │  │   • Agent control    │
│  • Logs WS         │  │   • Status SSE       │
└────────────────────┘  └──────────────────────┘
```

### Swarm Agent Architecture

Desktop client monitors 3 core Swarm agents:
- **CODER** 💻 - Writes code, tests, commits (no push)
- **DEPLOY** 🚀 - CI/CD: review, push, monitor CI, deploy
- **QA** 🧪 - Quality Assurance: write autotests, run against deployed app

Workflow:
1. User creates task via Desktop client → Swarm Server
2. Swarm orchestrates agents via Saga pattern
3. Desktop streams real-time status & output (SSE)
4. User approves/rejects changes via Desktop UI

## Logging

Логи пишутся:
- **Консоль** - для отладки
- **Файл** - `%LOCALAPPDATA%/Sombra/logs/` (Win) или `~/.local/share/sombra/logs/` (Linux)
- **Сервер** - WebSocket стрим на `ws://90.156.230.49:8080/api/logs/stream`

## Auto-Update

Приложение автоматически проверяет GitHub Releases при запуске:
1. Проверка через 3 сек после старта
2. Если есть новая версия — скачивает zip
3. Распаковывает и перезапускается

Релизы: https://github.com/Danny-sth/sombra-desktop/releases

## Features

### Voice Input
- **Push-to-talk** - Hold button or use hotkey (Ctrl+Shift+S)
- **Wake word detection** - Say "Jarvis" to activate
- **Auto-send on silence** - Automatically sends when you stop talking
- **VAD** - Voice Activity Detection filters out silence

### Chat Interface
- **Chat history** - Browse past conversations
- **Session management** - Create new chats or continue existing ones
- **Real-time streaming** - See responses as they're generated
- **Thinking updates** - Monitor Sombra's thought process

### Swarm Task Management
- **Task creation** - Start Development or QA tasks
- **Agent monitoring** - Track CODER, DEPLOY, QA agents in real-time
- **Live output streaming** - See agent work as it happens
- **Approval workflow** - Review and approve/reject changes
- **Question handling** - Answer agent questions interactively

### Auto-Update
- Checks GitHub Releases on startup
- Downloads and installs updates automatically
- Seamless restart to new version

## Deployment Rules

⚠️ **ВАЖНО: Деплой ТОЛЬКО через CI/CD!**

НЕ деплоить вручную через scp/ssh! Над проектом работает команда.

- **Sombra Server**: коммит в репо → CI/CD задеплоит
- **Sombra Desktop**: GitHub Release → auto-update

Если нужно срочно — спроси у хозяина.

## Known Issues & Limitations

- **Swarm agent roles in UI** - Currently shows old roles (BUILDER/REVIEWER/TESTER), needs update to CODER/DEPLOY/QA
- **Wake word sensitivity** - May trigger on similar sounds
- **Large PyTorch dependency** - Build size ~1.5-2GB due to Silero VAD

## Post-Task Hooks

### ОБЯЗАТЕЛЬНО: Отчёт о работе для Telegram

После завершения ЛЮБОЙ задачи ВСЕГДА пиши отчёт.

⚠️ **ВАЖНО**: Отчёт отправляется в **Telegram** — форматируй соответственно!

**Формат отчёта:**

```
📋 ОТЧЁТ

🎯 Задача: [краткое описание]

✅ Сделано:
• пункт 1
• пункт 2

📁 Файлы: file1.py, file2.py
(или "без изменений")

🏁 Статус: готово ✓
```

**Правила форматирования для Telegram:**

1. **Эмодзи** — используй для визуального разделения секций
2. **Краткость** — Telegram не любит простыни текста
3. **Списки** — через `•` или `-`, НЕ через markdown `*`
4. **Без code blocks для отчёта** — они плохо читаются в Telegram
5. **Статусы**:
   - ✓ готово
   - ⏳ частично (+ что осталось)
   - ⛔ заблокировано (+ причина)
