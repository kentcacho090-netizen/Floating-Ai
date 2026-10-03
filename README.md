# KENT — AI Desktop Companion

A small floating AI robot that lives on your Windows desktop.

He can hear you, see where your mouse is pointing, look at your screen when you ask, and reply **only in his chatbox** (no speaking).

## Download Ready-made EXE (easiest)

Go to the **Releases** page:

→ [https://github.com/kentcacho090-netizen/Floating-Ai/releases](https://github.com/kentcacho090-netizen/Floating-Ai/releases)

1. Download the latest `Kent-Windows.zip`
2. Extract it
3. Copy `.env.example` → `.env` and put your Gemini API key inside
4. Double-click `Kent.exe`

> First time Windows may show a SmartScreen warning (the app is not signed).  
> Click **More info** → **Run anyway**.

---

## Features

- Transparent, always-on-top desktop robot
- Walk / Sleep / Idle animations
- Dynamic chatbox (grows for longer answers)
- Global mouse tracking (works anywhere on screen)
- On-demand screen capture focused on your cursor
- Wake-word style voice input → conversation mode
- Real Gemini vision + chat
- Conversation memory
- Simple right-click menu: Microphone · Sleep/Wake · Walk/Stop

## Run from source

```powershell
git clone https://github.com/kentcacho090-netizen/Floating-Ai.git
cd Floating-Ai
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
copy .env.example .env
# edit .env and add your GEMINI_API_KEY
py main.py
```

## Build the EXE yourself

Just double-click `build.bat` (or run it from PowerShell).

The finished program will be in `dist\Kent\Kent.exe`.

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
- API key is loaded only from environment / `.env`.
- Automatic Windows builds are created by GitHub Actions on every push to `main`.

## Roadmap

- Better local wake-word model (openwakeword / Porcupine)
- Local STT option (faster-whisper)
- Multi-monitor improvements
- Conversation history summarization
- Settings panel
- More expressive animations
