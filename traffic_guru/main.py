#!/usr/bin/env python3
"""
Traffic Guru — Professional Web Traffic Automation
Entry point: python main.py
"""

import sys
import os

# Ensure the traffic_guru package directory is on the path so sibling imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from database.db import init_db
from license.license_manager import is_activated
from ui.styles import APP_STYLE
from ui.license_dialog import LicenseDialog
from ui.main_window import MainWindow


def main():
    # High-DPI support
    app = QApplication(sys.argv)
    app.setApplicationName("Traffic Guru")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Traffic Guru")
    app.setStyleSheet(APP_STYLE)

    # Initialise database
    init_db()

    # License check
    if not is_activated():
        dialog = LicenseDialog()
        result = dialog.exec()
        if result != LicenseDialog.DialogCode.Accepted:
            sys.exit(0)

    # Main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
