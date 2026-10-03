"""
Conversation-mode speech-to-text.
Activated only AFTER wake word is detected.
"""

from PySide6.QtCore import QObject, Signal, QThread
import speech_recognition as sr


class SpeechToTextWorker(QThread):
    """Listens for one complete utterance and returns the text."""

    result = Signal(str)          # recognized text
    failed = Signal(str)          # error or empty
    finished_listening = Signal()

    def __init__(self, timeout: float = 7.0, phrase_limit: float = 12.0):
        super().__init__()
        self.timeout = timeout
        self.phrase_limit = phrase_limit
        self._recognizer = sr.Recognizer()

    def run(self):
        try:
            with sr.Microphone() as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=0.4)
                print("[stt] listening for command...")
                audio = self._recognizer.listen(
                    source,
                    timeout=self.timeout,
                    phrase_time_limit=self.phrase_limit,
                )
                try:
                    text = self._recognizer.recognize_google(audio).strip()
                    print(f"[stt] got: {text}")
                    if text:
                        self.result.emit(text)
                    else:
                        self.failed.emit("empty")
                except sr.UnknownValueError:
                    self.failed.emit("Could not understand audio")
                except sr.RequestError as e:
                    self.failed.emit(f"Speech service error: {e}")
        except sr.WaitTimeoutError:
            self.failed.emit("timeout")
        except Exception as e:
            self.failed.emit(str(e))
        finally:
            self.finished_listening.emit()
