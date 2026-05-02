"""Live log console widget."""

import time
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit,
    QPushButton, QCheckBox, QLabel, QSizePolicy, QFrame,
)
from PyQt6.QtGui import QFont, QCursor, QTextCharFormat, QColor, QTextCursor


class LogConsole(QWidget):
    MAX_LINES = 2000

    def __init__(self, parent=None):
        super().__init__(parent)
        self._auto_scroll = True
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(10)

        # Toolbar — title left; controls grouped on the right (no overlap with stretch)
        bar = QFrame()
        bar.setObjectName("log_toolbar")
        toolbar = QHBoxLayout(bar)
        toolbar.setContentsMargins(12, 10, 12, 10)
        toolbar.setSpacing(16)

        label = QLabel("Live log")
        label.setFont(QFont("", 13, QFont.Weight.Bold))
        label.setStyleSheet("color: #e6edf3;")
        toolbar.addWidget(label)

        toolbar.addStretch(1)

        self.auto_scroll_chk = QCheckBox("Auto-scroll")
        self.auto_scroll_chk.setMinimumWidth(130)
        self.auto_scroll_chk.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.auto_scroll_chk.setChecked(True)
        self.auto_scroll_chk.stateChanged.connect(
            lambda v: setattr(self, "_auto_scroll", bool(v))
        )
        toolbar.addWidget(self.auto_scroll_chk, alignment=Qt.AlignmentFlag.AlignVCenter)

        btn_clear = QPushButton("Clear log")
        btn_clear.setObjectName("btn_log_clear")
        btn_clear.setMinimumSize(100, 34)
        btn_clear.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_clear.clicked.connect(self._clear)
        toolbar.addWidget(btn_clear, alignment=Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(bar)

        # Log area
        self.log_area = QPlainTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFont(QFont("SF Mono", 11))
        if not self.log_area.font().exactMatch():
            self.log_area.setFont(QFont("Consolas", 11))
        self.log_area.setStyleSheet(
            "background-color: #010409; color: #c9d1d9; "
            "border: 1px solid #30363d; border-radius: 8px; "
            "padding: 10px;"
        )
        self.log_area.setMaximumBlockCount(self.MAX_LINES)
        self.log_area.setMinimumHeight(120)
        self.log_area.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self.log_area, stretch=1)

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
