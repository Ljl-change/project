from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from app.controllers.app_controller import AppController
from app.ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    AppController(window)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
