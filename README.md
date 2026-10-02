# Floating AI

An experimental Windows desktop pet: a small, transparent robot that stays above other windows, walks, flies, sleeps, and displays speech bubbles.

## Current features

- Borderless, transparent, always-on-top window
- Walk and fly movement
- Sleep mode
- Drag with the left mouse button
- Right-click menu for behavior and exit

## Requirements

- Windows 10/11
- Python 3.10+
- PySide6

## Run from PowerShell

Clone or download this repository, then open PowerShell in the project folder:

```powershell
py -m pip install -r requirements.txt
py main.py
```

Right-click the robot to change modes. Left-click and drag it to reposition it.

## Roadmap

- Sprite-based animations and more expressive faces
- Voice input and spoken replies
- AI chat and step-by-step problem solving
- Screen-region capture, activated only by the user
- Settings for pet appearance, movement, and behavior

This is an early prototype. AI and voice features are not implemented yet.
