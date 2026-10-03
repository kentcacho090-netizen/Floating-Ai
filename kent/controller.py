"""
KentController — the central brain.
Owns state, coordinates voice, perception, AI, and UI.
"""

from typing import List, Optional
from PySide6.QtCore import QObject, QTimer, Slot

from kent.states import KentState
from kent.ui.pet import ScreenPet
from kent.ui.chatbox import ChatBox
from kent.perception.mouse import GlobalMouseTracker
from kent.perception.screen import capture_cursor_region
from kent.voice.wake import WakeWordWorker
from kent.voice.stt import SpeechToTextWorker
from kent.config import CONVERSATION_TIMEOUT
from kent.ai.brain import KentBrain


class KentController(QObject):
    def __init__(self):
        super().__init__()

        # UI
        self.pet = ScreenPet()
        self.chat = ChatBox()

        # Perception
        self.mouse = GlobalMouseTracker()
        self._latest_mouse = (0, 0)
        self.mouse.position_changed.connect(self._on_mouse_move)

        # Voice
        self.mic_enabled = False
        self.wake_worker: Optional[WakeWordWorker] = None
        self.stt_worker: Optional[SpeechToTextWorker] = None

        # AI — local-first brain
        self.brain = KentBrain()
        self.history: List[dict] = []

        # State
        self.state = KentState.IDLE
        self._conversation_timer = QTimer(self)
        self._conversation_timer.setSingleShot(True)
        self._conversation_timer.timeout.connect(self._return_to_wake_mode)

        # Wire pet menu
        self.pet.request_toggle_mic.connect(self.toggle_microphone)
        self.pet.request_toggle_sleep.connect(self.toggle_sleep)
        self.pet.request_toggle_walk.connect(self.toggle_walk)

        # Keep chatbox near the pet
        self._position_timer = QTimer(self)
        self._position_timer.timeout.connect(self._reposition_chat)
        self._position_timer.start(100)

    def start(self):
        self.pet.show()
        self.chat.hide()
        self._set_state(KentState.IDLE)

        if self.brain.is_ready():
            status = self.brain.status_message()
            self.chat.show_message(
                f"Hi! I'm Kent.\nBrain: {status}\nRight-click → Microphone ON",
                7000,
            )
            print(f"[kent] Ready — {status}")
        else:
            self.chat.show_message(
                "Hi! I'm Kent.\nNo AI engine found.\nInstall Ollama or add GEMINI_API_KEY",
                9000,
            )
            print("[kent] No AI engine available at startup")

    # ── State machine ──────────────────────────────────────────────────

    def _set_state(self, state: KentState):
        self.state = state
        self.pet.set_state(state)
        print(f"[kent] state → {state.name}")

    # ── Menu actions ───────────────────────────────────────────────────

    @Slot()
    def toggle_microphone(self):
        if self.mic_enabled:
            self._stop_voice()
            self.mic_enabled = False
            self.chat.show_message("Microphone OFF", 3000)
            self._set_state(KentState.IDLE)
        else:
            self.mic_enabled = True
            self._start_wake_mode()
            self.chat.show_message("Microphone ON — say 'Hey Kent'", 4000)

    @Slot()
    def toggle_sleep(self):
        if self.state == KentState.SLEEPING:
            self._set_state(KentState.IDLE)
            self.chat.show_message("I'm awake.", 2500)
            if self.mic_enabled:
                self._start_wake_mode()
        else:
            self._stop_voice()
            self._set_state(KentState.SLEEPING)
            self.chat.show_message("Zzz...", 2500)

    @Slot()
    def toggle_walk(self):
        if self.state == KentState.WALKING:
            self._set_state(KentState.IDLE)
        else:
            if self.state != KentState.SLEEPING:
                self._set_state(KentState.WALKING)

    # ── Voice pipeline ─────────────────────────────────────────────────

    def _start_wake_mode(self):
        self._stop_stt()
        if self.wake_worker and self.wake_worker.isRunning():
            return
        self.wake_worker = WakeWordWorker()
        self.wake_worker.wake_detected.connect(self._on_wake)
        self.wake_worker.error.connect(self._on_voice_error)
        self.wake_worker.start()
        print("[kent] wake mode active")

    def _stop_voice(self):
        self._stop_wake()
        self._stop_stt()
        self._conversation_timer.stop()

    def _stop_wake(self):
        if self.wake_worker:
            self.wake_worker.stop()
            self.wake_worker = None

    def _stop_stt(self):
        if self.stt_worker and self.stt_worker.isRunning():
            self.stt_worker.terminate()
            self.stt_worker.wait(1000)
        self.stt_worker = None

    @Slot()
    def _on_wake(self):
        print("[kent] WAKE DETECTED")
        self._stop_wake()
        self._set_state(KentState.WAKING)
        self.chat.show_status("Yeah? I'm listening...")
        self._set_state(KentState.LISTENING)

        self.stt_worker = SpeechToTextWorker()
        self.stt_worker.result.connect(self._on_user_speech)
        self.stt_worker.failed.connect(self._on_stt_failed)
        self.stt_worker.finished_listening.connect(self._on_stt_finished)
        self.stt_worker.start()

        self._conversation_timer.start(CONVERSATION_TIMEOUT * 1000)

    @Slot(str)
    def _on_user_speech(self, text: str):
        self._conversation_timer.stop()
        self.chat.show_status("Thinking...")
        self._set_state(KentState.THINKING)
        self._process_question(text)

    @Slot(str)
    def _on_stt_failed(self, reason: str):
        print(f"[kent] STT failed: {reason}")
        if reason == "timeout":
            self.chat.show_message("I didn't catch that. Say 'Hey Kent' again.", 4000)
        else:
            self.chat.show_message("Sorry, I couldn't hear you clearly.", 4000)
        self._return_to_wake_mode()

    @Slot()
    def _on_stt_finished(self):
        pass

    def _return_to_wake_mode(self):
        self._stop_stt()
        if self.mic_enabled and self.state != KentState.SLEEPING:
            self._set_state(KentState.IDLE)
            self._start_wake_mode()
            self.chat.clear()

    @Slot(str)
    def _on_voice_error(self, msg: str):
        self.chat.show_message(f"Mic error: {msg}", 5000)
        self._set_state(KentState.ERROR)

    # ── Question processing + AI ───────────────────────────────────────

    def _process_question(self, question: str):
        if not self.brain.is_ready():
            self.chat.show_message(
                "No AI engine available.\nInstall Ollama or add GEMINI_API_KEY",
                7000,
            )
            self._return_to_wake_mode()
            return

        visual_keywords = [
            "this", "that", "here", "what is", "what's", "explain",
            "look", "see", "screen", "error", "code", "diagram",
            "picture", "image", "graph", "equation", "problem",
        ]
        q_lower = question.lower()
        needs_vision = any(k in q_lower for k in visual_keywords)

        images = []
        if needs_vision:
            self._set_state(KentState.OBSERVING)
            self.chat.show_status("Looking at your screen...")
            mx, my = self._latest_mouse
            img = capture_cursor_region(mx, my)
            if img:
                images.append(img)
                print(f"[kent] captured crop around ({mx}, {my})")

        messages = []
        messages.extend(self.history[-10:])
        messages.append({"role": "user", "content": question})

        try:
            reply = self.brain.chat(messages, images=images if images else None)
        except Exception as e:
            print(f"[kent] AI error: {e}")
            self.chat.show_message("Sorry, I had trouble thinking just now.", 5000)
            self._set_state(KentState.ERROR)
            QTimer.singleShot(2000, self._return_to_wake_mode)
            return

        self.history.append({"role": "user", "content": question})
        self.history.append({"role": "assistant", "content": reply})
        if len(self.history) > 20:
            self.history = self.history[-16:]

        self._set_state(KentState.RESPONDING)
        self.chat.show_message(reply, duration_ms=max(8000, len(reply) * 50))

        self._set_state(KentState.IDLE)
        self._conversation_timer.start(CONVERSATION_TIMEOUT * 1000)

        if self.mic_enabled:
            self.stt_worker = SpeechToTextWorker(timeout=10.0)
            self.stt_worker.result.connect(self._on_user_speech)
            self.stt_worker.failed.connect(
                lambda r: self._return_to_wake_mode() if r == "timeout" else self._on_stt_failed(r)
            )
            self.stt_worker.start()

    # ── Helpers ────────────────────────────────────────────────────────

    @Slot(int, int)
    def _on_mouse_move(self, x: int, y: int):
        self._latest_mouse = (x, y)

    def _reposition_chat(self):
        if self.chat.isVisible():
            px, py = self.pet.x(), self.pet.y()
            self.chat.move(px - 40, py - self.chat.height() - 12)
