"""License activation dialog shown on first launch."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QSpacerItem, QSizePolicy
)
from PyQt6.QtGui import QFont

from license import license_manager


class LicenseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Traffic Guru — License Activation")
        self.setFixedSize(520, 400)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Logo / title
        title = QLabel("Traffic Guru")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #1f6feb; letter-spacing: -1px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Professional Web Traffic Automation")
        subtitle.setStyleSheet("color: #8b949e; font-size: 13px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("color: #30363d;")
        layout.addWidget(divider)

        # Instructions
        info = QLabel(
            "Enter your license key to activate Traffic Guru.\n"
            "Format: TGURU-XXXX-XXXX-XXXX-XXXX-XXXXXXXX"
        )
        info.setStyleSheet("color: #8b949e; font-size: 12px;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setWordWrap(True)
        layout.addWidget(info)

        # Key input
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("TGURU-XXXX-XXXX-XXXX-XXXX-XXXXXXXX")
        self.key_input.setStyleSheet(
            "font-size: 14px; font-family: 'Courier New', monospace; "
            "padding: 10px; letter-spacing: 1px; text-align: center;"
        )
        self.key_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.key_input)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_activate = QPushButton("Activate")
        self.btn_activate.setObjectName("btn_primary")
        self.btn_activate.setFixedHeight(38)
        self.btn_activate.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.btn_activate.clicked.connect(self._activate)
        btn_row.addWidget(self.btn_activate)

        btn_exit = QPushButton("Exit")
        btn_exit.setFixedHeight(38)
        btn_exit.clicked.connect(self.reject)
        btn_row.addWidget(btn_exit)

        layout.addLayout(btn_row)

        # Machine ID hint
        mid = license_manager.get_machine_id()
        mid_label = QLabel(f"Machine ID: {mid}")
        mid_label.setStyleSheet("color: #484f58; font-size: 11px; font-family: monospace;")
        mid_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(mid_label)

        self.key_input.returnPressed.connect(self._activate)

    def _activate(self):
        key = self.key_input.text().strip()
        if not key:
            self._set_status("Please enter a license key.", error=True)
            return

        self.btn_activate.setEnabled(False)
        self.btn_activate.setText("Activating…")

        success, msg = license_manager.activate(key)

        self.btn_activate.setEnabled(True)
        self.btn_activate.setText("Activate")

        if success:
            self._set_status(msg, error=False)
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(1200, self.accept)
        else:
            self._set_status(msg, error=True)

    def _set_status(self, msg: str, error: bool):
        color = "#f85149" if error else "#3fb950"
        self.status_label.setStyleSheet(f"color: {color}; font-size: 12px;")
        self.status_label.setText(msg)
