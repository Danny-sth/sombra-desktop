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

### Chat
```
POST /api/chat
Body: {"query": "text", "session_id": "unique-id"}
```

### Thinking Stream (SSE)
```
GET /api/thinking/stream/{sessionId}
Returns: Server-Sent Events with real-time thinking updates
```

### Client Logs (WebSocket)
```
WS /api/logs/stream - клиент отправляет логи в реалтайме (WRITE)
WS /api/logs/watch - читать логи в реалтайме (READ)
GET /api/logs/watch/sse - SSE альтернатива для чтения логов
GET /api/logs/clients - подключённые клиенты
GET /api/logs/buffer - последние логи от всех клиентов
GET /api/logs/buffer/{client_id} - логи конкретного клиента
```

### System
```
GET /api/system/version - Build info
GET /health - Health check
```

## Configuration

Edit `.env` file:
```env
SOMBRA_API_URL=http://90.156.230.49:8080
SOMBRA_SESSION_ID=owner
STT_URL=http://100.87.46.63:5000/transcribe
THEME=dark
GLOBAL_HOTKEY=ctrl+shift+s
```

## Running

```bash
cd /home/danny/Documents/projects/sombra-desktop
source .venv/bin/activate
python -m sombra
```

## Architecture

- **PySide6** - Qt GUI framework
- **PySide6-Fluent-Widgets** - Fluent Design UI components
- **httpx + httpx-sse** - Async HTTP with SSE streaming
- **websockets** - Real-time log streaming to server
- **sounddevice** - Audio capture (requires PortAudio)
- **pynput** - Global hotkeys (requires Xlib on Linux)
- **silero-vad** - Voice Activity Detection
- **pvporcupine** - Wake word detection

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
