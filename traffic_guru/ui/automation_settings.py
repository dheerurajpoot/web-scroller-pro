"""Automation Settings tab."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox,
    QComboBox, QCheckBox, QPushButton, QGroupBox, QFormLayout, QScrollArea,
    QFrame
)
from PyQt6.QtGui import QFont

from database import db


class AutomationSettingsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._load_settings()

    def _build_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        scroll.setWidget(container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        # ── Delay Settings ──
        delay_group = QGroupBox("Timing & Delay")
        delay_form = QFormLayout(delay_group)
        delay_form.setSpacing(12)
        delay_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.delay_min = QDoubleSpinBox()
        self.delay_min.setRange(0, 300)
        self.delay_min.setSuffix("  seconds")
        self.delay_min.setDecimals(1)
        self.delay_min.setToolTip("Minimum delay between opening URLs")
        delay_form.addRow("Min delay between URLs:", self.delay_min)

        self.delay_max = QDoubleSpinBox()
        self.delay_max.setRange(0, 300)
        self.delay_max.setSuffix("  seconds")
        self.delay_max.setDecimals(1)
        self.delay_max.setToolTip("Maximum delay between opening URLs")
        delay_form.addRow("Max delay between URLs:", self.delay_max)

        layout.addWidget(delay_group)

        # ── Views ──
        views_group = QGroupBox("Views Per URL")
        views_form = QFormLayout(views_group)
        views_form.setSpacing(12)

        self.views_per_url = QSpinBox()
        self.views_per_url.setRange(1, 1000)
        self.views_per_url.setSuffix("  views")
        views_form.addRow("Number of views per URL:", self.views_per_url)

        layout.addWidget(views_group)

        # ── Scroll Settings ──
        scroll_group = QGroupBox("Scroll Behavior")
        scroll_form = QFormLayout(scroll_group)
        scroll_form.setSpacing(12)

        self.scroll_speed = QComboBox()
        self.scroll_speed.addItems(["slow", "medium", "fast"])
        scroll_form.addRow("Scroll speed:", self.scroll_speed)

        self.random_mouse = QCheckBox("Enable random mouse movements")
        scroll_form.addRow("", self.random_mouse)

        self.click_links = QCheckBox("Click random internal links during session")
        scroll_form.addRow("", self.click_links)

        layout.addWidget(scroll_group)

        # ── Browser Settings ──
        browser_group = QGroupBox("Browser Settings")
        browser_form = QFormLayout(browser_group)
        browser_form.setSpacing(12)

        self.max_browsers = QSpinBox()
        self.max_browsers.setRange(1, 20)
        self.max_browsers.setSuffix("  concurrent")
        self.max_browsers.setToolTip("Maximum number of browser windows open at once")
        browser_form.addRow("Max concurrent browsers:", self.max_browsers)

        self.headless = QCheckBox("Run browsers in headless mode (no visible window)")
        browser_form.addRow("", self.headless)

        layout.addWidget(browser_group)

        # ── Save button ──
        save_row = QHBoxLayout()
        save_row.addStretch()
        self.btn_save = QPushButton("Save Settings")
        self.btn_save.setObjectName("btn_primary")
        self.btn_save.setFixedWidth(160)
        self.btn_save.clicked.connect(self._save_settings)
        save_row.addWidget(self.btn_save)
        layout.addLayout(save_row)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #3fb950;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.status_label)

        layout.addStretch()

    def _load_settings(self):
        s = db.get_all_settings()
        self.delay_min.setValue(float(s.get("delay_min", 3)))
        self.delay_max.setValue(float(s.get("delay_max", 8)))
        self.scroll_speed.setCurrentText(s.get("scroll_speed", "medium"))
        self.random_mouse.setChecked(s.get("random_mouse", "1") == "1")
        self.click_links.setChecked(s.get("click_links", "0") == "1")
        self.max_browsers.setValue(int(s.get("max_browsers", 5)))
        self.headless.setChecked(s.get("headless", "0") == "1")
        self.views_per_url.setValue(int(s.get("views_per_url", 1)))

    def _save_settings(self):
        db.set_setting("delay_min", self.delay_min.value())
        db.set_setting("delay_max", self.delay_max.value())
        db.set_setting("scroll_speed", self.scroll_speed.currentText())
        db.set_setting("random_mouse", "1" if self.random_mouse.isChecked() else "0")
        db.set_setting("click_links", "1" if self.click_links.isChecked() else "0")
        db.set_setting("max_browsers", self.max_browsers.value())
        db.set_setting("headless", "1" if self.headless.isChecked() else "0")
        db.set_setting("views_per_url", self.views_per_url.value())
        self.status_label.setText("✓ Settings saved")
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(2000, lambda: self.status_label.setText(""))

    def get_settings(self) -> dict:
        self._save_settings()
        return db.get_all_settings()
