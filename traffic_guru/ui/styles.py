"""Global dark stylesheet for Traffic Guru."""

APP_STYLE = """
/*
 * Do NOT set background-color on the generic QWidget selector — it applies to
 * QLabel, QCheckBox label areas, and table cell hosts, causing tight “black
 * patches” behind text on macOS. Colour only real surfaces below.
 */
QWidget {
    color: #c9d1d9;
    font-size: 13px;
}

QMainWindow {
    background-color: #0d1117;
}

QDialog, QMessageBox {
    background-color: #0d1117;
}

QLabel {
    background-color: transparent;
    border: none;
}

QSplitter {
    background-color: transparent;
}

/* Table cell widgets (checkbox / action rows) must stay transparent */
QWidget#table_toggle_cell,
QWidget#table_actions_cell {
    background-color: transparent;
    border: none;
}

/* ── App chrome / header ── */
QFrame#app_header {
    background-color: #010409;
    border-bottom: 1px solid #21262d;
}
QFrame#header_controls {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
}
QFrame#header_controls QPushButton {
    border-radius: 8px;
    min-height: 36px;
    padding: 8px 14px;
    font-size: 12px;
}

/* ── Dashboard stat cards (fixed row, no scroll) ── */
QFrame#stat_card {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
}
QFrame#stat_card QLabel {
    background-color: transparent;
}
QFrame#stat_card:hover {
    border-color: #484f58;
    background-color: #1c2128;
}

/* ── Log console toolbar ── */
QFrame#log_toolbar {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
}
QFrame#log_toolbar QCheckBox {
    font-size: 13px;
    font-weight: 500;
    spacing: 10px;
    background-color: transparent;
}
QPushButton#btn_log_clear {
    background-color: #21262d;
    color: #e6edf3;
    border: 1px solid #484f58;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 12px;
}
QPushButton#btn_log_clear:hover {
    background-color: #30363d;
    border-color: #8b949e;
}

/* ── Settings / proxies page chrome ── */
QLabel#page_title {
    color: #e6edf3;
}
QLabel#page_subtitle {
    color: #8b949e;
    font-size: 12px;
    margin-bottom: 4px;
}
QScrollArea#settings_scroll {
    background: transparent;
    border: none;
}
QFrame#proxy_options_bar {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
}
QFrame#proxy_options_bar QCheckBox {
    font-size: 13px;
    font-weight: 500;
}
QLabel#proxy_count_label {
    font-size: 13px;
    font-weight: 600;
    color: #e6edf3;
}
QTabWidget#proxy_inner_tabs::pane {
    border: 1px solid #30363d;
    border-radius: 8px;
    background-color: #0d1117;
    padding: 8px;
    top: -1px;
}
QTabWidget#proxy_inner_tabs QTabBar::tab {
    padding: 9px 20px;
    min-width: 100px;
}

/* ── Table row action buttons ── */
QPushButton#btn_table_secondary {
    background-color: #21262d;
    color: #e6edf3;
    border: 1px solid #484f58;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: 600;
    min-height: 36px;
}
QPushButton#btn_table_secondary:hover {
    background-color: #30363d;
    border-color: #8b949e;
    color: #ffffff;
}
QPushButton#btn_table_danger {
    background-color: #da3633;
    color: #ffffff;
    border: 1px solid #f85149;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: 600;
    min-height: 36px;
}
QPushButton#btn_table_danger:hover {
    background-color: #f85149;
    border-color: #ff7b72;
}

/* ── Main tab bar (URLs / Dashboard / …) ── */
QTabWidget::pane {
    border: 1px solid #30363d;
    border-radius: 10px;
    background-color: #161b22;
    top: -1px;
    padding: 12px 8px 8px 8px;
}
QTabBar {
    background: transparent;
}
QTabBar::tab {
    background: #21262d;
    color: #8b949e;
    padding: 10px 28px;
    min-height: 22px;
    border: 1px solid #30363d;
    border-bottom: none;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    margin-right: 6px;
    font-size: 13px;
    font-weight: 600;
}
QTabBar::tab:selected {
    background: #161b22;
    color: #e6edf3;
    border-color: #30363d;
    border-bottom-color: #161b22;
    border-top: 3px solid #388bfd;
    margin-bottom: -1px;
    padding-top: 7px;
    padding-bottom: 11px;
}
QTabBar::tab:hover:!selected {
    background: #30363d;
    color: #e6edf3;
    border-color: #484f58;
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
QTableWidget::item {
    padding: 8px 10px;
    border: none;
}
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
    padding: 10px 12px;
    font-weight: 700;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.6px;
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
    background-color: transparent;
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
    margin-top: 16px;
    padding: 18px 14px 14px 14px;
    font-weight: 600;
    color: #8b949e;
    background-color: transparent;
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
    background-color: #010409;
    color: #c9d1d9;
    border-bottom: 1px solid #21262d;
    padding: 4px 8px;
    font-size: 13px;
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

/* ── Legacy card frame (if used elsewhere) ── */
QFrame#card {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
}

/* ── Settings specific styles ── */
QFrame#setting_row {
    border-bottom: 1px solid #21262d;
}
QFrame#setting_row_no_border {
    border: none;
}
QLabel#setting_group_title {
    color: #e6edf3;
    font-size: 15px;
    font-weight: 600;
    margin-bottom: 4px;
}
QLabel#setting_title {
    color: #e6edf3;
    font-size: 13px;
    font-weight: 600;
}
QLabel#setting_desc {
    color: #8b949e;
    font-size: 12px;
}
"""
