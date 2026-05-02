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
        scroll.setMinimumHeight(380)
        scroll.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        container = QWidget()
        scroll.setWidget(container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(scroll)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        page_title = QLabel("Automation settings")
        page_title.setObjectName("page_title")
        page_title.setFont(QFont("", 20, QFont.Weight.Bold))
        header_layout.addWidget(page_title)

        page_sub = QLabel("Timing, scrolling, and browser behaviour for traffic sessions.")
        page_sub.setObjectName("page_subtitle")
        page_sub.setWordWrap(True)
        header_layout.addWidget(page_sub)
        layout.addLayout(header_layout)

        # ── Delay Settings Card ──
        delay_label = QLabel("Timing & Delay")
        delay_label.setObjectName("setting_group_title")
        layout.addWidget(delay_label)
        
        delay_card = QFrame()
        delay_card.setObjectName("card")
        delay_card_layout = QVBoxLayout(delay_card)
        delay_card_layout.setContentsMargins(0, 0, 0, 0)
        delay_card_layout.setSpacing(0)

        self.delay_min = QDoubleSpinBox()
        self.delay_min.setRange(0, 300)
        self.delay_min.setSuffix(" sec")
        self.delay_min.setDecimals(1)
        self.delay_min.setMinimumHeight(32)
        self.delay_min.setMinimumWidth(100)
        
        self.delay_max = QDoubleSpinBox()
        self.delay_max.setRange(0, 300)
        self.delay_max.setSuffix(" sec")
        self.delay_max.setDecimals(1)
        self.delay_max.setMinimumHeight(32)
        self.delay_max.setMinimumWidth(100)

        delay_card_layout.addWidget(self._create_setting_row(
            "Minimum Delay", "Minimum delay between opening URLs.", self.delay_min
        ))
        delay_card_layout.addWidget(self._create_setting_row(
            "Maximum Delay", "Maximum delay between opening URLs.", self.delay_max, is_last=True
        ))
        layout.addWidget(delay_card)

        # ── Views Card ──
        views_label = QLabel("Page Views")
        views_label.setObjectName("setting_group_title")
        layout.addWidget(views_label)

        views_card = QFrame()
        views_card.setObjectName("card")
        views_card_layout = QVBoxLayout(views_card)
        views_card_layout.setContentsMargins(0, 0, 0, 0)
        views_card_layout.setSpacing(0)

        self.views_per_url = QSpinBox()
        self.views_per_url.setRange(1, 1000)
        self.views_per_url.setSuffix(" views")
        self.views_per_url.setMinimumHeight(32)
        self.views_per_url.setMinimumWidth(100)

        views_card_layout.addWidget(self._create_setting_row(
            "Views Per URL", "Number of times to view each URL.", self.views_per_url, is_last=True
        ))
        layout.addWidget(views_card)

        # ── Scroll Settings Card ──
        scroll_label = QLabel("Scroll Behavior")
        scroll_label.setObjectName("setting_group_title")
        layout.addWidget(scroll_label)

        scroll_card = QFrame()
        scroll_card.setObjectName("card")
        scroll_card_layout = QVBoxLayout(scroll_card)
        scroll_card_layout.setContentsMargins(0, 0, 0, 0)
        scroll_card_layout.setSpacing(0)

        self.scroll_speed = QComboBox()
        self.scroll_speed.addItems(["slow", "medium", "fast"])
        self.scroll_speed.setMinimumHeight(32)
        self.scroll_speed.setMinimumWidth(100)

        self.random_mouse = QCheckBox()
        self.click_links = QCheckBox()

        scroll_card_layout.addWidget(self._create_setting_row(
            "Scroll Speed", "Pacing of scrolling down the page.", self.scroll_speed
        ))
        scroll_card_layout.addWidget(self._create_setting_row(
            "Random Mouse Movements", "Simulate human-like random mouse movements.", self.random_mouse
        ))
        scroll_card_layout.addWidget(self._create_setting_row(
            "Click Internal Links", "Randomly navigate internal links during the session.", self.click_links, is_last=True
        ))
        layout.addWidget(scroll_card)

        # ── Browser Settings Card ──
        browser_label = QLabel("Browser Settings")
        browser_label.setObjectName("setting_group_title")
        layout.addWidget(browser_label)

        browser_card = QFrame()
        browser_card.setObjectName("card")
        browser_card_layout = QVBoxLayout(browser_card)
        browser_card_layout.setContentsMargins(0, 0, 0, 0)
        browser_card_layout.setSpacing(0)

        self.max_browsers = QSpinBox()
        self.max_browsers.setRange(1, 20)
        self.max_browsers.setMinimumHeight(32)
        self.max_browsers.setMinimumWidth(100)

        self.headless = QCheckBox()

        browser_card_layout.addWidget(self._create_setting_row(
            "Max Concurrent Browsers", "Maximum number of browser instances open at once.", self.max_browsers
        ))
        browser_card_layout.addWidget(self._create_setting_row(
            "Headless Mode", "Run browsers invisibly without opening windows.", self.headless, is_last=True
        ))
        layout.addWidget(browser_card)

        # ── Save button ──
        save_row = QHBoxLayout()
        save_row.addStretch()
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #3fb950; font-weight: 500; font-size: 13px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        save_row.addWidget(self.status_label)
        
        self.btn_save = QPushButton("Save settings")
        self.btn_save.setObjectName("btn_primary")
        self.btn_save.setMinimumHeight(36)
        self.btn_save.setMinimumWidth(140)
        self.btn_save.clicked.connect(self._save_settings)
        save_row.addWidget(self.btn_save)
        
        layout.addLayout(save_row)
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
