"""
The visual robot character.
Keeps the original cute drawing + animations, now driven by controller state.
"""

import math
from PySide6.QtCore import QPoint, Qt, QTimer, Signal
from PySide6.QtGui import QAction, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QMenu, QWidget

from kent.states import KentState


class ScreenPet(QWidget):
    """Transparent always-on-top robot."""

    # Signals the controller listens to
    request_toggle_mic = Signal()
    request_toggle_sleep = Signal()
    request_toggle_walk = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(180, 180)

        screen = self.screen().availableGeometry() if self.screen() else None
        if screen:
            self.move(screen.left() + 80, screen.bottom() - 205)

        self.state = KentState.IDLE
        self.frame = 0
        self.direction = 1
        self.dragging = False
        self.drag_offset = QPoint()
        self.gaze_x = 0
        self.gaze_y = 0
        self.cursor_near = False
        self.flight_origin_y = self.y()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(33)

    def set_state(self, state: KentState):
        self.state = state
        if state == KentState.WALKING:
            screen = self.screen().availableGeometry()
            self.move(self.x(), screen.bottom() - 205)
        self.update()

    def _animate(self):
        self.frame += 1

        if self.dragging:
            self.update()
            return

        if self.state == KentState.WALKING:
            screen = self.screen().availableGeometry()
            x = self.x() + self.direction * 2
            if x < screen.left() or x + self.width() > screen.right():
                self.direction *= -1
                x = max(screen.left(), min(x, screen.right() - self.width()))
            self.move(x, screen.bottom() - 205)

        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        bob = 0
        if self.state in (KentState.IDLE, KentState.WALKING, KentState.LISTENING,
                         KentState.THINKING, KentState.OBSERVING, KentState.RESPONDING):
            bob = round(3 * math.sin(self.frame / 7))

        y = bob

        # Shadow
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(0, 0, 0, 65))
        p.drawEllipse(49, 151, 82, 15)

        # Legs
        leg = 0
        if self.state == KentState.WALKING:
            leg = round(5 * math.sin(self.frame / 3))
        p.setBrush(QColor("#b9d9e8"))
        p.setPen(QPen(QColor("#537d9a"), 2))
        p.drawRoundedRect(61, 127 + y + leg, 21, 25, 9, 9)
        p.drawRoundedRect(98, 127 + y - leg, 21, 25, 9, 9)

        # Body + arms
        p.setBrush(QColor("#e9f5fb"))
        p.setPen(QPen(QColor("#78b4d2"), 2))
        p.drawRoundedRect(49, 76 + y, 82, 64, 23, 23)
        p.setBrush(QColor("#c9e5f2"))
        p.drawRoundedRect(35, 88 + y, 18, 43, 9, 9)
        p.drawRoundedRect(127, 88 + y, 18, 43, 9, 9)

        # Head + ears
        p.setBrush(QColor("#f4fbff"))
        p.setPen(QPen(QColor("#78b4d2"), 2))
        p.drawRoundedRect(43, 20 + y, 94, 75, 28, 28)
        p.setBrush(QColor("#cceafa"))
        p.drawEllipse(34, 42 + y, 19, 25)
        p.drawEllipse(127, 42 + y, 19, 25)
        p.setBrush(QColor("#36c9ff"))
        p.drawEllipse(40, 49 + y, 7, 11)
        p.drawEllipse(133, 49 + y, 7, 11)

        # Face
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#172b43"))
        p.drawRoundedRect(54, 31 + y, 72, 52, 19, 19)

        eye = QColor("#36d5ff")
        sleeping = self.state == KentState.SLEEPING
        blinking = not sleeping and self.frame % 150 in (0, 1, 2)

        if sleeping or blinking:
            p.setPen(QPen(eye, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawLine(68, 55 + y, 80, 55 + y)
            p.drawLine(100, 55 + y, 112, 55 + y)
        else:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(eye)
            p.drawEllipse(69 + self.gaze_x, 45 + y + self.gaze_y, 12, 17)
            p.drawEllipse(99 + self.gaze_x, 45 + y + self.gaze_y, 12, 17)

        # Cheek light
        p.setBrush(QColor("#36d5ff"))
        p.drawEllipse(85, 105 + y, 10, 10)

        # Listening indicator (small glow)
        if self.state == KentState.LISTENING:
            p.setBrush(QColor(54, 213, 255, 90))
            p.drawEllipse(20, 10 + y, 140, 140)

    # ── Mouse interaction ──────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_offset = event.globalPosition().toPoint() - self.pos()
        elif event.button() == Qt.MouseButton.RightButton:
            self._open_menu()

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        over = (43 <= pos.x() <= 137 and 20 <= pos.y() <= 95) or \
               (49 <= pos.x() <= 131 and 76 <= pos.y() <= 140)

        if over:
            self.gaze_x = max(-4, min(4, round((pos.x() - 90) / 10)))
            self.gaze_y = max(-3, min(3, round((pos.y() - 55) / 12)))
            self.cursor_near = True
        else:
            self.gaze_x = 0
            self.gaze_y = 0
            self.cursor_near = False

        if self.dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_offset)

        self.update()

    def leaveEvent(self, event):
        self.cursor_near = False
        self.gaze_x = 0
        self.gaze_y = 0
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False

    def _open_menu(self):
        menu = QMenu(self)

        mic = QAction("Microphone ON / OFF", self)
        mic.triggered.connect(self.request_toggle_mic.emit)
        menu.addAction(mic)

        sleep = QAction("Sleep / Wake", self)
        sleep.triggered.connect(self.request_toggle_sleep.emit)
        menu.addAction(sleep)

        walk = QAction("Walk / Stop Walking", self)
        walk.triggered.connect(self.request_toggle_walk.emit)
        menu.addAction(walk)

        menu.exec(self.mapToGlobal(self.rect().center()))
