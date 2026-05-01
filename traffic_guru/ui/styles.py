"""Global dark stylesheet for Traffic Guru."""

APP_STYLE = """
QWidget {
    background-color: #0d1117;
    color: #c9d1d9;
    font-family: 'Segoe UI', 'Inter', 'SF Pro Display', Arial, sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #0d1117;
}

/* ── Tabs ── */
QTabWidget::pane {
    border: 1px solid #30363d;
    border-radius: 6px;
    background-color: #161b22;
}
QTabBar::tab {
    background: #161b22;
    color: #8b949e;
    padding: 10px 22px;
    border: 1px solid #30363d;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
    font-size: 13px;
    font-weight: 500;
}
QTabBar::tab:selected {
    background: #1f6feb;
    color: #ffffff;
    border-color: #1f6feb;
}
QTabBar::tab:hover:!selected {
    background: #21262d;
    color: #c9d1d9;
}

/* ── Buttons ── */
QPushButton {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 7px 16px;
    font-weight: 500;
    min-height: 30px;
}
QPushButton:hover {
    background-color: #30363d;
    border-color: #8b949e;
    color: #e6edf3;
}
QPushButton:pressed {
    background-color: #161b22;
}
QPushButton:disabled {
    background-color: #161b22;
    color: #484f58;
    border-color: #21262d;
}

QPushButton#btn_start {
    background-color: #238636;
    color: #ffffff;
    border-color: #2ea043;
    font-weight: 600;
}
QPushButton#btn_start:hover { background-color: #2ea043; }
QPushButton#btn_start:disabled { background-color: #1a3022; border-color: #1a3022; color: #484f58; }

QPushButton#btn_stop {
    background-color: #da3633;
    color: #ffffff;
    border-color: #f85149;
    font-weight: 600;
}
QPushButton#btn_stop:hover { background-color: #f85149; }
QPushButton#btn_stop:disabled { background-color: #3d1a1a; border-color: #3d1a1a; color: #484f58; }

QPushButton#btn_pause {
    background-color: #9e6a03;
    color: #ffffff;
    border-color: #d29922;
    font-weight: 600;
}
QPushButton#btn_pause:hover { background-color: #d29922; }
QPushButton#btn_resume {
    background-color: #1f6feb;
    color: #ffffff;
    border-color: #388bfd;
    font-weight: 600;
}
QPushButton#btn_resume:hover { background-color: #388bfd; }

QPushButton#btn_danger {
    background-color: #da3633;
    color: #ffffff;
    border-color: #f85149;
}
QPushButton#btn_danger:hover { background-color: #f85149; }

QPushButton#btn_primary {
    background-color: #1f6feb;
    color: #ffffff;
    border-color: #388bfd;
    font-weight: 600;
}
QPushButton#btn_primary:hover { background-color: #388bfd; }

/* ── Inputs ── */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #0d1117;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 10px;
    selection-background-color: #1f6feb;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #1f6feb;
}

QSpinBox, QDoubleSpinBox {
    background-color: #0d1117;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 5px 8px;
    min-height: 28px;
}
QSpinBox:focus, QDoubleSpinBox:focus { border-color: #1f6feb; }
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background-color: #21262d;
    border: none;
    width: 18px;
}
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #30363d;
}

QComboBox {
    background-color: #0d1117;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 5px 10px;
    min-height: 28px;
}
QComboBox:focus { border-color: #1f6feb; }
QComboBox::drop-down { border: none; width: 22px; }
QComboBox QAbstractItemView {
    background-color: #161b22;
    color: #c9d1d9;
    selection-background-color: #1f6feb;
    border: 1px solid #30363d;
}

/* ── Tables ── */
QTableWidget {
    background-color: #161b22;
    color: #c9d1d9;
    gridline-color: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    alternate-background-color: #0d1117;
}
QTableWidget::item { padding: 6px 10px; }
QTableWidget::item:selected {
    background-color: #1f6feb;
    color: #ffffff;
}
QHeaderView::section {
    background-color: #21262d;
    color: #8b949e;
    border: none;
    border-right: 1px solid #30363d;
    border-bottom: 1px solid #30363d;
    padding: 7px 10px;
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
}

/* ── Scroll bars ── */
QScrollBar:vertical {
    background: #161b22;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #30363d;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover { background: #484f58; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal {
    background: #161b22;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #30363d;
    border-radius: 4px;
    min-width: 20px;
}

/* ── Checkboxes ── */
QCheckBox {
    color: #c9d1d9;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #30363d;
    border-radius: 3px;
    background: #0d1117;
}
QCheckBox::indicator:checked {
    background-color: #1f6feb;
    border-color: #1f6feb;
    image: url(none);
}
QCheckBox::indicator:hover { border-color: #8b949e; }

/* ── Group Boxes ── */
QGroupBox {
    border: 1px solid #30363d;
    border-radius: 8px;
    margin-top: 14px;
    padding: 12px 10px 10px 10px;
    font-weight: 600;
    color: #8b949e;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    left: 12px;
    color: #8b949e;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ── Labels ── */
QLabel#label_stat {
    font-size: 28px;
    font-weight: 700;
    color: #e6edf3;
}
QLabel#label_stat_caption {
    font-size: 11px;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ── Sliders ── */
QSlider::groove:horizontal {
    height: 4px;
    background: #30363d;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #1f6feb;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::sub-page:horizontal { background: #1f6feb; border-radius: 2px; }

/* ── Splitter ── */
QSplitter::handle { background: #30363d; }

/* ── Status bar ── */
QStatusBar {
    background: #161b22;
    border-top: 1px solid #30363d;
    color: #8b949e;
    font-size: 12px;
}

/* ── Menu bar ── */
QMenuBar {
    background-color: #161b22;
    color: #c9d1d9;
    border-bottom: 1px solid #30363d;
}
QMenuBar::item:selected { background: #21262d; }
QMenu {
    background-color: #161b22;
    color: #c9d1d9;
    border: 1px solid #30363d;
}
QMenu::item:selected { background: #1f6feb; }

/* ── Tooltip ── */
QToolTip {
    background-color: #21262d;
    color: #e6edf3;
    border: 1px solid #30363d;
    padding: 5px;
    border-radius: 4px;
}

/* ── Progress bar ── */
QProgressBar {
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 4px;
    text-align: center;
    color: #c9d1d9;
    font-size: 11px;
}
QProgressBar::chunk {
    background: #1f6feb;
    border-radius: 3px;
}

/* ── Frame / Card ── */
QFrame#card {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
}
"""
