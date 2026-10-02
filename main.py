import math
import sys

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QAction, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QApplication, QMenu, QWidget


class ScreenPet(QWidget):
    """A tiny transparent desktop pet. Right-click for its behavior menu."""

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(180, 180)

        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.left() + 80, screen.bottom() - 205)

        self.mode = "walk"
        self.frame = 0
        self.direction = 1
        self.dragging = False
        self.drag_offset = QPoint()
        self.setMouseTracking(True)
        self.cursor_near_pet = False
        self.gaze_x = 0
        self.gaze_y = 0
        self.message = "Hi! I'm your screen pet."
        self.message_ticks = 180
        self.flight_origin_y = self.y()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(33)

    def say(self, message):
        self.message = message
        self.message_ticks = 180
        self.update()

    def set_mode(self, mode):
        self.mode = mode
        if mode == "fly":
            self.flight_origin_y = self.y()
        elif mode == "walk":
            screen = QApplication.primaryScreen().availableGeometry()
            self.move(self.x(), screen.bottom() - 205)
        self.say({
            "walk": "Let's take a walk!",
            "fly": "Wheee! I'm flying!",
            "sleep": "Zzz... wake me when needed.",
        }[mode])

    def animate(self):
        self.frame += 1
        screen = QApplication.primaryScreen().availableGeometry()

        if not self.dragging and self.mode in ("walk", "fly"):
            speed = 2 if self.mode == "walk" else 3
            x = self.x() + self.direction * speed
            if x < screen.left() or x + self.width() > screen.right():
                self.direction *= -1
                x = max(screen.left(), min(x, screen.right() - self.width()))
            y = self.y()
            if self.mode == "fly":
                y = self.flight_origin_y - 55 + round(12 * math.sin(self.frame / 12))
                y = max(screen.top(), min(y, screen.bottom() - self.height()))
            self.move(x, y)

        if self.message_ticks > 0:
            self.message_ticks -= 1
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        bob = round(3 * math.sin(self.frame / 7)) if self.mode in ("walk", "fly") else 0
        y = bob

        # Shadow
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(0, 0, 0, 65))
        p.drawEllipse(49, 151, 82, 15)

        # Legs
        leg = round(5 * math.sin(self.frame / 3)) if self.mode == "walk" else 0
        p.setBrush(QColor("#b9d9e8"))
        p.setPen(QPen(QColor("#537d9a"), 2))
        p.drawRoundedRect(61, 127 + y + leg, 21, 25, 9, 9)
        p.drawRoundedRect(98, 127 + y - leg, 21, 25, 9, 9)

        # Body and arms
        p.setBrush(QColor("#e9f5fb"))
        p.setPen(QPen(QColor("#78b4d2"), 2))
        p.drawRoundedRect(49, 76 + y, 82, 64, 23, 23)
        p.setBrush(QColor("#c9e5f2"))
        p.drawRoundedRect(35, 88 + y, 18, 43, 9, 9)
        p.drawRoundedRect(127, 88 + y, 18, 43, 9, 9)

        # Head and ears
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
        blinking = self.mode != "sleep" and self.frame % 150 in (0, 1, 2)
        if self.mode == "sleep" or blinking:
            p.setPen(QPen(eye, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawLine(68, 55 + y, 80, 55 + y)
            p.drawLine(100, 55 + y, 112, 55 + y)
        else:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(eye)
            p.drawEllipse(69 + self.gaze_x, 45 + y + self.gaze_y, 12, 17)
            p.drawEllipse(99 + self.gaze_x, 45 + y + self.gaze_y, 12, 17)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#36d5ff"))
        p.drawEllipse(85, 105 + y, 10, 10)
        if self.mode == "fly":
            p.setBrush(QColor(54, 213, 255, 120))
            p.drawEllipse(62, 143 + y, 16, 13)
            p.drawEllipse(103, 143 + y, 16, 13)

        # Speech bubble
        if self.message_ticks > 0:
            p.setFont(QFont("Segoe UI", 9))
            p.setPen(QPen(QColor("#74cfff"), 1.5))
            p.setBrush(QColor(17, 34, 55, 238))
            p.drawRoundedRect(5, 1, 170, 32, 10, 10)
            p.setPen(QColor("#eaf8ff"))
            message = self.message if len(self.message) <= 28 else self.message[:25] + "..."
            p.drawText(13, 21, message)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_offset = event.globalPosition().toPoint() - self.pos()
            self.say("You can drag me around!")
        elif event.button() == Qt.MouseButton.RightButton:
            self.open_menu()

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        over_head = 43 <= pos.x() <= 137 and 20 <= pos.y() <= 95
        over_body = 49 <= pos.x() <= 131 and 76 <= pos.y() <= 140
        over_pet = over_head or over_body

        if over_pet:
            self.gaze_x = max(-4, min(4, round((pos.x() - 90) / 10)))
            self.gaze_y = max(-3, min(3, round((pos.y() - 55) / 12)))
            if not self.cursor_near_pet:
                self.say("Hey! I see you!")
        else:
            self.gaze_x = 0
            self.gaze_y = 0

        self.cursor_near_pet = over_pet
        if self.dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_offset)
        self.update()

    def leaveEvent(self, event):
        self.cursor_near_pet = False
        self.gaze_x = 0
        self.gaze_y = 0
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False

    def open_menu(self):
        menu = QMenu(self)
        for label, mode in (
            ("Walk around", "walk"),
            ("Fly around", "fly"),
            ("Sleep", "sleep"),
        ):
            action = QAction(label, self)
            action.triggered.connect(lambda checked=False, m=mode: self.set_mode(m))
            menu.addAction(action)

        menu.addSeparator()
        hello = QAction("Say hello", self)
        hello.triggered.connect(lambda: self.say("Hello! What shall we solve?"))
        menu.addAction(hello)
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)
        menu.exec(self.mapToGlobal(self.rect().center()))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = ScreenPet()
    pet.show()
    sys.exit(app.exec())
