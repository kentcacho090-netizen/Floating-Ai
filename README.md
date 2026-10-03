# KENT — AI Desktop Companion

A small floating AI robot that lives on your Windows desktop.

He can hear you, see where your mouse is pointing, look at your screen when you ask, and reply **only in his chatbox** (no speaking).

## Features (current)

- Transparent, always-on-top desktop robot
- Walk / Sleep / Idle animations
- Dynamic chatbox (grows for longer answers)
- Global mouse tracking (works anywhere on screen)
- On-demand screen capture focused on your cursor
- Wake-word style voice input → conversation mode
- Real Gemini vision + chat (provider-agnostic design)
- Conversation memory
- Simple right-click menu: Microphone · Sleep/Wake · Walk/Stop

## Quick Start

1. Clone the repo
2. Create a virtual environment (recommended)
3. Install dependencies:

```powershell
py -m pip install -r requirements.txt
```

4. Copy `.env.example` → `.env` and put your Gemini API key:

```
GEMINI_API_KEY=your_real_key_here
```

5. Run:

```powershell
py main.py
```

### Microphone
Right-click the robot → **Microphone ON**

Then say:

> "Hey Kent"

He wakes up and shows "Yeah?" / "I'm listening."

Then ask your real question:

> "What is this?"
> "What's wrong here?"
> "Explain this"

He will look at the area around your mouse + the screenshot and answer in the chatbox.

## Architecture

```
kent/
├── controller.py      # central brain + state machine
├── ui/
│   ├── pet.py         # the visual robot
│   └── chatbox.py     # dynamic speech bubble
├── perception/
│   ├── mouse.py       # global mouse tracker
│   └── screen.py      # screenshot + cursor crop
├── voice/
│   ├── wake.py        # wake-word detection
│   └── stt.py         # speech-to-text
└── ai/
    ├── provider.py    # abstract AI interface
    └── gemini.py      # Gemini implementation
```

## Important Notes

- **No TTS** — Kent never speaks. Text only.
- Screen images are captured only when you ask a visual question and are discarded after the AI call.
- Wake word detection is designed to be local; full STT activates only after wake.
- API key is loaded only from environment / `.env`.

## Roadmap

- Better local wake-word model (openwakeword / Porcupine)
- Local STT option (faster-whisper)
- Multi-monitor improvements
- Conversation history summarization
- Settings panel
- More expressive animations

This is an active prototype. The foundation is now solid for a real desktop AI companion.
