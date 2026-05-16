"""Automation Settings tab."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox,
    QComboBox, QCheckBox, QPushButton, QGroupBox, QFormLayout, QScrollArea,
    QFrame, QSizePolicy,
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
        scroll.setObjectName("settings_scroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setMinimumHeight(450)

        container = QWidget()
        scroll.setWidget(container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(32)

        # ── Header ──
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)
        
        logo_row = QHBoxLayout()
        logo_row.setSpacing(12)
        
        settings_icon = QLabel("⚙️")
        settings_icon.setStyleSheet("font-size: 28px;")
        logo_row.addWidget(settings_icon)
        
        page_title = QLabel("System Configuration")
        page_title.setFont(QFont("", 26, QFont.Weight.Bold))
        page_title.setStyleSheet("color: #ffffff; letter-spacing: -0.5px;")
        logo_row.addWidget(page_title)
        logo_row.addStretch()
        header_layout.addLayout(logo_row)

        page_sub = QLabel("Fine-tune the automation engine, timing, and human emulation behavior.")
        page_sub.setStyleSheet("color: #8b949e; font-size: 15px; font-weight: 500;")
        page_sub.setWordWrap(True)
        header_layout.addWidget(page_sub)
        layout.addLayout(header_layout)

        # ── Group: Performance & Concurrency ──
        perf_group = QGroupBox("Performance & Concurrency")
        perf_layout = QFormLayout(perf_group)
        perf_layout.setContentsMargins(24, 28, 24, 24)
        perf_layout.setSpacing(20)
        perf_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.max_browsers = QSpinBox()
        self.max_browsers.setRange(1, 50)
        self.max_browsers.setSuffix(" tabs")
        self.max_browsers.setMinimumHeight(40)
        self.max_browsers.setMinimumWidth(120)

        self.headless = QCheckBox("Run browsers in stealth mode (Headless)")
        self.incognito = QCheckBox("Private Browsing (Incognito Mode)")
        self.block_images = QCheckBox("Block Images (Save Bandwidth)")

        perf_layout.addRow("Max Parallel Instances:", self.max_browsers)
        perf_layout.addRow(self.headless)
        perf_layout.addRow(self.incognito)
        perf_layout.addRow(self.block_images)
        layout.addWidget(perf_group)

        # ── Group: Human Emulation ──
        emul_group = QGroupBox("Human Emulation")
        emul_layout = QFormLayout(emul_group)
        emul_layout.setContentsMargins(24, 28, 24, 24)
        emul_layout.setSpacing(20)

        self.scroll_speed = QComboBox()
        self.scroll_speed.addItems(["slow", "medium", "fast"])
        self.scroll_speed.setMinimumHeight(40)
        self.scroll_speed.setMinimumWidth(120)

        self.random_mouse = QCheckBox("Simulate erratic mouse movements")
        self.click_links = QCheckBox("Deep Navigation: Interact with internal links")
        
        for chk in [self.random_mouse, self.click_links]:
            chk.setStyleSheet("font-size: 14px; padding: 4px;")

        emul_layout.addRow("Scrolling Pace:", self.scroll_speed)
        emul_layout.addRow(self.random_mouse)
        emul_layout.addRow(self.click_links)
        layout.addWidget(emul_group)

        # ── Group: Session Dynamics ──
        dyn_group = QGroupBox("Session Dynamics")
        dyn_layout = QFormLayout(dyn_group)
        dyn_layout.setContentsMargins(24, 28, 24, 24)
        dyn_layout.setSpacing(20)

        self.delay_min = QDoubleSpinBox()
        self.delay_min.setRange(0, 300)
        self.delay_min.setSuffix(" sec")
        self.delay_min.setDecimals(1)
        self.delay_min.setMinimumHeight(40)
        
        self.delay_max = QDoubleSpinBox()
        self.delay_max.setRange(0, 300)
        self.delay_max.setSuffix(" sec")
        self.delay_max.setDecimals(1)
        self.delay_max.setMinimumHeight(40)

        self.views_per_url = QSpinBox()
        self.views_per_url.setRange(1, 5000)
        self.views_per_url.setSuffix(" views")
        self.views_per_url.setMinimumHeight(40)

        dyn_layout.addRow("Minimum Delay:", self.delay_min)
        dyn_layout.addRow("Maximum Delay:", self.delay_max)
        dyn_layout.addRow("Cycle Frequency:", self.views_per_url)
        layout.addWidget(dyn_group)

        # ── Footer ──
        footer = QHBoxLayout()
        footer.addStretch()
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #3fb950; font-weight: 700; font-size: 14px; margin-right: 12px;")
        footer.addWidget(self.status_label)
        
        self.btn_save = QPushButton("  💾  Save & Apply Configuration  ")
        self.btn_save.setObjectName("btn_primary")
        self.btn_save.setMinimumHeight(48)
        self.btn_save.setMinimumWidth(240)
        self.btn_save.setFont(QFont("", 12, QFont.Weight.Bold))
        self.btn_save.clicked.connect(self._save_settings)
        footer.addWidget(self.btn_save)
        
        layout.addLayout(footer)
        layout.addStretch()

    def _create_setting_row(self, title_text: str, desc_text: str, widget: QWidget, is_last: bool = False) -> QFrame:
        row = QFrame()
        row.setObjectName("setting_row_no_border" if is_last else "setting_row")
        
        layout = QHBoxLayout(row)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        title = QLabel(title_text)
        title.setObjectName("setting_title")
        text_layout.addWidget(title)
        
        if desc_text:
            desc = QLabel(desc_text)
            desc.setObjectName("setting_desc")
            desc.setWordWrap(True)
            text_layout.addWidget(desc)
            
        layout.addLayout(text_layout)
        layout.addStretch()
        layout.addWidget(widget, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        return row

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
        self.incognito.setChecked(s.get("incognito", "1") == "1")
        self.block_images.setChecked(s.get("block_images", "0") == "1")

    def _save_settings(self):
        db.set_setting("delay_min", self.delay_min.value())
        db.set_setting("delay_max", self.delay_max.value())
        db.set_setting("scroll_speed", self.scroll_speed.currentText())
        db.set_setting("random_mouse", "1" if self.random_mouse.isChecked() else "0")
        db.set_setting("click_links", "1" if self.click_links.isChecked() else "0")
        db.set_setting("max_browsers", self.max_browsers.value())
        db.set_setting("headless", "1" if self.headless.isChecked() else "0")
        db.set_setting("views_per_url", self.views_per_url.value())
        db.set_setting("incognito", "1" if self.incognito.isChecked() else "0")
        db.set_setting("block_images", "1" if self.block_images.isChecked() else "0")
        self.status_label.setText("✓ Settings saved")
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(2000, lambda: self.status_label.setText(""))

    def get_settings(self) -> dict:
        self._save_settings()
        return db.get_all_settings()
