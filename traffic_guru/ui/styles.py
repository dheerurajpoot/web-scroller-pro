"""Global dark stylesheet for Traffic Guru."""

APP_STYLE = """
/* 
 * Professional Dark Theme for Traffic Guru
 * Inspired by modern IDEs and developer tools
 */

QWidget {
    color: #e6edf3;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #0d1117;
}

QDialog, QMessageBox {
    background-color: #161b22;
    border: 1px solid #30363d;
}

QLabel {
    background-color: transparent;
}

/* ── App Header ── */
QFrame#app_header {
    background-color: #010409;
    border-bottom: 1px solid #30363d;
}

QFrame#header_controls {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
}

/* ── Buttons ── */
QPushButton {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #30363d;
    border-color: #8b949e;
}

QPushButton:pressed {
    background-color: #161b22;
}

QPushButton#btn_primary {
    background-color: #238636;
    color: #ffffff;
    border: 1px solid #2ea043;
}

QPushButton#btn_primary:hover {
    background-color: #2ea043;
}

QPushButton#btn_start {
    background-color: #238636;
    color: #ffffff;
    border: 1px solid #2ea043;
}

QPushButton#btn_stop {
    background-color: #da3633;
    color: #ffffff;
    border: 1px solid #f85149;
}

QPushButton#btn_stop:hover {
    background-color: #f85149;
}

/* ── Inputs ── */
QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 10px;
    color: #e6edf3;
}

QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border-color: #388bfd;
    outline: none;
}

/* ── Tabs ── */
QTabWidget::pane {
    border: 1px solid #30363d;
    border-radius: 8px;
    background-color: #0d1117;
    top: -1px;
}

QTabBar::tab {
    background: transparent;
    color: #8b949e;
    padding: 10px 20px;
    border-bottom: 2px solid transparent;
    font-weight: 600;
}

QTabBar::tab:selected {
    color: #e6edf3;
    border-bottom: 2px solid #f78166;
}

QTabBar::tab:hover:!selected {
    color: #c9d1d9;
    background-color: #161b22;
}

/* ── Tables ── */
QTableWidget {
    background-color: #0d1117;
    gridline-color: #30363d;
    border: 1px solid #30363d;
    border-radius: 8px;
    outline: none;
}

QTableWidget::item {
    padding: 8px;
}

QTableWidget::item:selected {
    background-color: #161b22;
    color: #58a6ff;
}

QHeaderView::section {
    background-color: #161b22;
    color: #8b949e;
    padding: 10px;
    border: none;
    border-bottom: 1px solid #30363d;
    font-weight: 600;
}

/* ── Stat Cards ── */
QFrame#stat_card {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
}

QFrame#stat_card:hover {
    border-color: #388bfd;
    background-color: #1c2128;
}

/* ── Group Boxes ── */
QGroupBox {
    border: 1px solid #30363d;
    border-radius: 12px;
    margin-top: 24px;
    padding-top: 20px;
    font-weight: 700;
    color: #8b949e;
    background-color: #161b22;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 20px;
    padding: 4px 12px;
    color: #e6edf3;
    background-color: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
}

/* ── Form Labels ── */
QFormLayout {
    spacing: 20px;
}

QLabel[text^="Max"], QLabel[text^="Min"], QLabel[text^="Scroll"], QLabel[text^="Cycle"] {
    font-weight: 600;
    color: #8b949e;
    font-size: 14px;
}

/* ── Scrollbars ── */
QScrollBar:vertical {
    border: none;
    background: #0d1117;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #30363d;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #484f58;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}
"""
