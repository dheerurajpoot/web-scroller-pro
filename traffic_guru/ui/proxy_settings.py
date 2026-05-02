"""Proxy Settings tab."""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMessageBox, QFileDialog, QGroupBox, QCheckBox,
    QTextEdit, QTabWidget, QSizePolicy, QFrame,
)
from PyQt6.QtGui import QFont

from database import db
from core.proxy_manager import ProxyManager


class ProxySettingsTab(QWidget):
    log_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.proxy_manager = ProxyManager()
        self._build_ui()
        self._refresh_table()
        self._load_proxy_settings()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        page_title = QLabel("Proxy settings")
        page_title.setObjectName("page_title")
        page_title.setFont(QFont("", 20, QFont.Weight.Bold))
        layout.addWidget(page_title)

        page_sub = QLabel(
            "Route sessions through HTTP, HTTPS, or SOCKS proxies. Enable rotation for multi-proxy setups."
        )
        page_sub.setObjectName("page_subtitle")
        page_sub.setWordWrap(True)
        layout.addWidget(page_sub)

        # Enable proxy toggle — card strip
        opt_bar = QFrame()
        opt_bar.setObjectName("proxy_options_bar")
        top_row = QHBoxLayout(opt_bar)
        top_row.setContentsMargins(16, 12, 16, 12)
        top_row.setSpacing(24)

        self.use_proxy_chk = QCheckBox("Enable proxy rotation")
        self.use_proxy_chk.stateChanged.connect(
            lambda v: db.set_setting("use_proxy", "1" if v else "0")
        )
        top_row.addWidget(self.use_proxy_chk)

        self.rotate_proxy_chk = QCheckBox("Rotate proxy per session")
        self.rotate_proxy_chk.stateChanged.connect(
            lambda v: db.set_setting("rotate_proxy", "1" if v else "0")
        )
        top_row.addWidget(self.rotate_proxy_chk)
        top_row.addStretch()
        layout.addWidget(opt_bar)

        # Tabs: single add | bulk add
        inner_tabs = QTabWidget()
        inner_tabs.setObjectName("proxy_inner_tabs")

        # Single add (grid avoids label/field overlap on narrow widths)
        single_tab = QWidget()
        single_grid = QGridLayout(single_tab)
        single_grid.setContentsMargins(12, 12, 12, 12)
        single_grid.setHorizontalSpacing(10)
        single_grid.setVerticalSpacing(10)
        single_grid.setColumnStretch(1, 1)

        single_grid.addWidget(QLabel("Proxy"), 0, 0)
        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("host:port  or  protocol://user:pass@host:port")
        self.proxy_input.setMinimumHeight(34)
        self.proxy_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        single_grid.addWidget(self.proxy_input, 0, 1, 1, 2)

        single_grid.addWidget(QLabel("Type"), 1, 0)
        self.proxy_type = QComboBox()
        self.proxy_type.addItems(["http", "https", "socks4", "socks5"])
        self.proxy_type.setMinimumHeight(34)
        single_grid.addWidget(self.proxy_type, 1, 1)

        btn_add_single = QPushButton("Add")
        btn_add_single.setObjectName("btn_primary")
        btn_add_single.setMinimumWidth(100)
        btn_add_single.clicked.connect(self._add_single)
        single_grid.addWidget(btn_add_single, 1, 2)

        inner_tabs.addTab(single_tab, "Add Single")

        # Bulk add
        bulk_tab = QWidget()
        bulk_layout = QVBoxLayout(bulk_tab)
        bulk_layout.setContentsMargins(12, 12, 12, 12)
        bulk_layout.setSpacing(8)

        bulk_layout.addWidget(QLabel("Paste proxy list (one per line):"))
        self.bulk_input = QTextEdit()
        self.bulk_input.setPlaceholderText(
            "192.168.1.1:8080\nsocks5://user:pass@10.0.0.1:1080\n…"
        )
        self.bulk_input.setFixedHeight(140)
        bulk_layout.addWidget(self.bulk_input)

        bulk_row = QHBoxLayout()
        btn_add_bulk = QPushButton("Import from Text")
        btn_add_bulk.setObjectName("btn_primary")
        btn_add_bulk.clicked.connect(self._add_bulk)
        bulk_row.addWidget(btn_add_bulk)

        btn_import_file = QPushButton("Import from File")
        btn_import_file.clicked.connect(self._import_file)
        bulk_row.addWidget(btn_import_file)
        bulk_row.addStretch()
        bulk_layout.addLayout(bulk_row)

        inner_tabs.addTab(bulk_tab, "Bulk Import")
        layout.addWidget(inner_tabs)

        # Proxy table
        tbl_header = QHBoxLayout()
        self.count_label = QLabel("Proxies: 0")
        self.count_label.setObjectName("proxy_count_label")
        tbl_header.addWidget(self.count_label)
        tbl_header.addStretch()

        btn_test_all = QPushButton("Test Selected")
        btn_test_all.clicked.connect(self._test_selected)
        tbl_header.addWidget(btn_test_all)

        btn_clear = QPushButton("Clear All")
        btn_clear.setObjectName("btn_danger")
        btn_clear.clicked.connect(self._clear_all)
        tbl_header.addWidget(btn_clear)

        layout.addLayout(tbl_header)

        self.proxy_table = QTableWidget(0, 5)
        self.proxy_table.setHorizontalHeaderLabels(["", "Proxy", "Type", "Success", "Fail"])
        self.proxy_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.proxy_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.proxy_table.setColumnWidth(0, 36)
        self.proxy_table.setAlternatingRowColors(True)
        self.proxy_table.verticalHeader().setVisible(False)
        self.proxy_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.proxy_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.proxy_table.setMinimumHeight(200)
        self.proxy_table.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self.proxy_table, stretch=1)

    def _load_proxy_settings(self):
        s = db.get_all_settings()
        self.use_proxy_chk.setChecked(s.get("use_proxy", "0") == "1")
        self.rotate_proxy_chk.setChecked(s.get("rotate_proxy", "1") == "1")

    def _refresh_table(self):
        proxies = db.get_proxies(enabled_only=False)
        self.proxy_table.setRowCount(0)
        for p in proxies:
            row = self.proxy_table.rowCount()
            self.proxy_table.insertRow(row)

            chk = QCheckBox()
            chk.setChecked(bool(p["enabled"]))
            chk.stateChanged.connect(lambda v, pid=p["id"]: db.toggle_proxy(pid, bool(v)))
            cell = QWidget()
            cell.setObjectName("table_toggle_cell")
            cell.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            cl = QHBoxLayout(cell)
            cl.setContentsMargins(6, 4, 6, 4)
            cl.addWidget(chk)
            cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.proxy_table.setCellWidget(row, 0, cell)

            self.proxy_table.setItem(row, 1, QTableWidgetItem(p["proxy"]))
            self.proxy_table.setItem(row, 2, QTableWidgetItem(p["proxy_type"]))
            self.proxy_table.setItem(row, 3, QTableWidgetItem(str(p["success_count"])))
            self.proxy_table.setItem(row, 4, QTableWidgetItem(str(p["fail_count"])))

        self.count_label.setText(f"Proxies: {len(proxies)}")
        self.proxy_manager.reload()

    def _add_single(self):
        raw = self.proxy_input.text().strip()
        ptype = self.proxy_type.currentText()
        if not raw:
            return
        if db.add_proxy(raw, ptype):
            self.log_signal.emit(f"[Proxy] Added: {raw}")
            self.proxy_input.clear()
        else:
            self.log_signal.emit(f"[Proxy] Already exists: {raw}")
        self._refresh_table()

    def _add_bulk(self):
        text = self.bulk_input.toPlainText()
        count = 0
        for line in text.splitlines():
            result = ProxyManager.parse_proxy_line(line)
            if result:
                proxy_str, ptype = result
                if db.add_proxy(proxy_str, ptype):
                    count += 1
        self.bulk_input.clear()
        self.log_signal.emit(f"[Proxy] Imported {count} proxy(ies) from text")
        self._refresh_table()

    def _import_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Proxy List", "", "Text Files (*.txt);;All Files (*)"
        )
        if not path:
            return
        count = 0
        with open(path) as f:
            for line in f:
                result = ProxyManager.parse_proxy_line(line)
                if result:
                    proxy_str, ptype = result
                    if db.add_proxy(proxy_str, ptype):
                        count += 1
        self.log_signal.emit(f"[Proxy] Imported {count} proxy(ies) from file")
        self._refresh_table()

    def _test_selected(self):
        import threading, requests
        rows = self.proxy_table.selectionModel().selectedRows()
        if not rows:
            return
        row = rows[0].row()
        item = self.proxy_table.item(row, 1)
        if not item:
            return
        proxy_str = item.text()
        ptype = self.proxy_table.item(row, 2).text()

        self.log_signal.emit(f"[Proxy] Testing: {proxy_str}…")

        def test():
            try:
                proxies = {
                    "http": f"{ptype}://{proxy_str}",
                    "https": f"{ptype}://{proxy_str}",
                }
                r = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=10)
                self.log_signal.emit(f"[Proxy] ✓ {proxy_str} — IP: {r.json().get('origin')}")
                db.record_proxy_result(proxy_str, True)
            except Exception as e:
                self.log_signal.emit(f"[Proxy] ✗ {proxy_str} — {e}")
                db.record_proxy_result(proxy_str, False)
            self._refresh_table()

        threading.Thread(target=test, daemon=True).start()

    def _clear_all(self):
        confirm = QMessageBox.question(
            self, "Clear Proxies", "Delete all proxies?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            conn = db.get_connection()
            conn.execute("DELETE FROM proxies")
            conn.commit()
            conn.close()
            self._refresh_table()
            self.log_signal.emit("[Proxy] All proxies cleared")

    def get_enabled_proxies(self) -> list[dict]:
        return db.get_proxies(enabled_only=True)
