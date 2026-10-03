"""
Dynamic chat bubble that grows with content.
Shows Listening / Thinking / final answer.
"""

from PySide6.QtCore import Qt, QTimer, QRect, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QFontMetrics
from PySide6.QtWidgets import QWidget


class ChatBox(QWidget):
    """Floating speech bubble attached to the pet."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        self._text = ""
        self._visible_ticks = 0
        self._max_width = 320
        self._padding = 12
        self._font = QFont("Segoe UI", 10)

        self.hide()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(50)

    def show_message(self, text: str, duration_ms: int = 8000):
        self._text = text.strip()
        self._visible_ticks = max(1, duration_ms // 50)
        self._relayout()
        self.show()
        self.raise_()

    def show_status(self, text: str):
        """Show a short status that stays until replaced."""
        self._text = text
        self._visible_ticks = 99999  # stays until next message
        self._relayout()
        self.show()
        self.raise_()

    def clear(self):
        self._text = ""
        self._visible_ticks = 0
        self.hide()

    def _relayout(self):
        if not self._text:
            self.resize(1, 1)
            return

        fm = QFontMetrics(self._font)
        # Word-wrap calculation
        lines = []
        words = self._text.split()
        current = ""
        for w in words:
            test = (current + " " + w).strip()
            if fm.horizontalAdvance(test) <= self._max_width - 2 * self._padding:
                current = test
            else:
                if current:
                    lines.append(current)
                current = w
        if current:
            lines.append(current)

        if not lines:
            lines = [self._text]

        line_height = fm.height() + 2
        height = len(lines) * line_height + 2 * self._padding
        width = min(
            self._max_width,
            max(fm.horizontalAdvance(line) for line in lines) + 2 * self._padding + 8,
        )

        self.resize(width, height)
        self._lines = lines

    def _tick(self):
        if self._visible_ticks > 0:
            self._visible_ticks -= 1
            if self._visible_ticks <= 0:
                self.hide()

    def paintEvent(self, event):
        if not self._text:
            return

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        p.setPen(QPen(QColor("#74cfff"), 1.5))
        p.setBrush(QColor(17, 34, 55, 240))
        p.drawRoundedRect(1, 1, self.width() - 2, self.height() - 2, 12, 12)

        # Text
        p.setFont(self._font)
        p.setPen(QColor("#eaf8ff"))
        fm = QFontMetrics(self._font)
        y = self._padding + fm.ascent()
        for line in getattr(self, "_lines", [self._text]):
            p.drawText(self._padding, y, line)
            y += fm.height() + 2
