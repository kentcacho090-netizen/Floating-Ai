"""
Wake-word detection (local).

Current implementation uses a simple keyword check on short STT snippets
for reliability out-of-the-box. Structure is ready to swap in openwakeword
or Porcupine later without changing the rest of the system.
"""

from PySide6.QtCore import QObject, Signal, QThread
import speech_recognition as sr
import time


WAKE_PHRASES = ["hey kent", "hey can", "hey ken", "kent", "hey kent"]


class WakeWordWorker(QThread):
    """Background thread that listens for the wake phrase."""

    wake_detected = Signal()
    error = Signal(str)

    def __init__(self):
        super().__init__()
        self._running = False
        self._recognizer = sr.Recognizer()
        self._recognizer.energy_threshold = 300
        self._recognizer.dynamic_energy_threshold = True

    def run(self):
        self._running = True
        try:
            with sr.Microphone() as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=0.6)
                while self._running:
                    try:
                        audio = self._recognizer.listen(source, timeout=1.5, phrase_time_limit=3)
                        try:
                            text = self._recognizer.recognize_google(audio).lower().strip()
                            print(f"[wake] heard: {text}")
                            if any(phrase in text for phrase in WAKE_PHRASES):
                                self.wake_detected.emit()
                                # Small pause so we don't immediately re-trigger
                                time.sleep(1.2)
                        except sr.UnknownValueError:
                            pass
                        except sr.RequestError as e:
                            self.error.emit(f"Speech service error: {e}")
                            time.sleep(2)
                    except sr.WaitTimeoutError:
                        continue
                    except Exception as e:
                        print(f"[wake] loop error: {e}")
                        time.sleep(0.5)
        except Exception as e:
            self.error.emit(f"Microphone error: {e}")

    def stop(self):
        self._running = False
        self.wait(2000)
