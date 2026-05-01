"""Live log console widget."""

import time
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit,
    QPushButton, QCheckBox, QLabel
)
from PyQt6.QtGui import QFont, QTextCharFormat, QColor, QTextCursor


class LogConsole(QWidget):
    MAX_LINES = 2000

    def __init__(self, parent=None):
        super().__init__(parent)
        self._auto_scroll = True
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        label = QLabel("Live Log Console")
        label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        label.setStyleSheet("color: #e6edf3;")
        toolbar.addWidget(label)
        toolbar.addStretch()

        self.auto_scroll_chk = QCheckBox("Auto-scroll")
        self.auto_scroll_chk.setChecked(True)
        self.auto_scroll_chk.stateChanged.connect(
            lambda v: setattr(self, "_auto_scroll", bool(v))
        )
        toolbar.addWidget(self.auto_scroll_chk)

        btn_clear = QPushButton("Clear")
        btn_clear.setFixedHeight(28)
        btn_clear.setStyleSheet("padding: 2px 12px; font-size: 12px;")
        btn_clear.clicked.connect(self._clear)
        toolbar.addWidget(btn_clear)

        layout.addLayout(toolbar)

        # Log area
        self.log_area = QPlainTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFont(QFont("Consolas", 11))
        self.log_area.setStyleSheet(
            "background-color: #0d1117; color: #c9d1d9; "
            "border: 1px solid #30363d; border-radius: 6px; "
            "padding: 8px;"
        )
        self.log_area.setMaximumBlockCount(self.MAX_LINES)
        layout.addWidget(self.log_area)

    def append(self, msg: str):
        """Thread-safe log append (call from main thread via signal)."""
        ts = time.strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"

        # Colour coding
        if "[✓]" in msg or "Done" in msg or "complet" in msg.lower():
            color = "#3fb950"
        elif "[✗]" in msg or "Error" in msg or "error" in msg.lower():
            color = "#f85149"
        elif "[■]" in msg or "Stop" in msg:
            color = "#d29922"
        elif "[Engine]" in msg:
            color = "#a371f7"
        elif "[Sitemap]" in msg:
            color = "#79c0ff"
        elif "[Proxy]" in msg:
            color = "#56d364"
        elif "[+]" in msg:
            color = "#1f6feb"
        else:
            color = "#c9d1d9"

        cursor = self.log_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cursor.setCharFormat(fmt)
        cursor.insertText(line + "\n")

        if self._auto_scroll:
            self.log_area.setTextCursor(cursor)
            self.log_area.ensureCursorVisible()

    def _clear(self):
        self.log_area.clear()
