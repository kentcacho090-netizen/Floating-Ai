# KENT — AI Desktop Companion

A small floating AI robot that lives on your Windows desktop.

He can hear you, see where your mouse is pointing, look at your screen when you ask, and reply **only in his chatbox** (no speaking).

**Local-first by default** (Ollama) with optional Gemini cloud fallback.

## Quick Start

### 1. Preferred — Local (free & private)

1. Install [Ollama](https://ollama.com)
2. Pull a model:
   ```powershell
   ollama pull llama3.2
   ```
   (For vision / screen understanding use `ollama pull llava`)
3. Run Kent:
   ```powershell
   py main.py
   ```

### 2. Optional — Cloud (Gemini)

Copy `.env.example` → `.env` and add your key:

```
GEMINI_API_KEY=your_key_here
```

Kent will automatically use Gemini if Ollama is not available.

## Features

- Transparent, always-on-top desktop robot
- Walk / Sleep / Idle animations
- Dynamic chatbox
- Global mouse tracking
- On-demand screen capture focused on your cursor
- Wake-word voice input → conversation mode
- **Local-first AI** (Ollama) + Gemini fallback
- Conversation memory
- Simple right-click menu: Microphone · Sleep/Wake · Walk/Stop

## How to talk to Kent

1. Right-click → **Microphone ON**
2. Say **“Hey Kent”**
3. Ask your question (you can point at something on screen)
4. He answers in the chatbox

## Architecture (local-first)

```
Kent
├── UI (robot + chatbox)
├── Perception (mouse + screen crop)
├── Voice (wake + STT)
└── Intelligence
     ├── OllamaEngine   ← primary (local)
     └── GeminiEngine   ← optional fallback
```

## Notes

- No TTS — Kent never speaks out loud.
- Screen images are captured only when needed and discarded after use.
- If both Ollama and Gemini are available, Ollama is preferred.
