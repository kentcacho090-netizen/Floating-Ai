"""
Global mouse tracker — works anywhere on the desktop, not just over the robot.
"""

from PySide6.QtCore import QObject, Signal, QTimer
from pynput import mouse


class GlobalMouseTracker(QObject):
    """Emits the latest global mouse position."""

    position_changed = Signal(int, int)  # x, y in virtual desktop coordinates

    def __init__(self, parent=None):
        super().__init__(parent)
        self._x = 0
        self._y = 0
        self._listener = None

        # Poll from the pynput thread into Qt safely
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._emit_latest)
        self._timer.start(50)  # 20 Hz is plenty

        self._start_listener()

    def _start_listener(self):
        def on_move(x, y):
            self._x = int(x)
            self._y = int(y)

        self._listener = mouse.Listener(on_move=on_move)
        self._listener.daemon = True
        self._listener.start()

    def _emit_latest(self):
        self.position_changed.emit(self._x, self._y)

    @property
    def position(self) -> tuple[int, int]:
        return self._x, self._y

    def stop(self):
        if self._listener:
            self._listener.stop()
