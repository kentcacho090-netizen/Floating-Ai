# KENT — AI Desktop Companion

A small floating AI robot that lives on your Windows desktop.

He can hear you, see where your mouse is pointing, look at your screen when you ask, and reply **only in his chatbox** (no speaking).

**Local-first by default** (Ollama) with optional Gemini cloud fallback.

## Quick Start (Recommended)

### 1. Install Ollama
Download from [https://ollama.com](https://ollama.com) and install it.

### 2. Pull a model

```powershell
# Good general model
ollama pull llama3.2

# For screen vision (recommended)
ollama pull llava
```

### 3. Run Kent

```powershell
py -m pip install -r requirements.txt
py main.py
```

Kent will automatically use Ollama.  
If Ollama is not running, it will fall back to Gemini (if you have a key).

## Optional — Gemini Cloud

Copy `.env.example` → `.env` and add:

```
GEMINI_API_KEY=your_key_here
```

## How to use Kent

1. Right-click the robot → **Microphone ON**
2. Say **“Hey Kent”**
3. Ask anything (point at the screen if needed)
4. He answers in the chatbox

## Features

- Transparent always-on-top robot
- Walk / Sleep / Idle animations
- Dynamic chatbox
- Global mouse tracking
- On-demand screen capture around the cursor
- Wake-word voice input
- **Local-first AI** (Ollama) + Gemini fallback
- Automatic vision model switching when you ask about the screen
- Conversation memory

## Notes

- No text-to-speech — Kent only replies in the chatbox.
- Screen images are captured only when needed and then discarded.
- Ollama is preferred. Gemini is used only when local is unavailable or for stronger vision.
