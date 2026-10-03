"""
KENT — AI Desktop Companion
Entry point.
"""

import sys
from PySide6.QtWidgets import QApplication

from kent.controller import KentController


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    controller = KentController()
    controller.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
