"""URL Manager tab — add/edit/delete websites and discover sitemap URLs."""

import threading
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMessageBox, QFileDialog, QCheckBox,
    QGroupBox, QSplitter, QProgressBar
)
from PyQt6.QtGui import QFont

from database import db
from core.sitemap_parser import discover_sitemap_urls
from utils.helpers import normalise_url, is_valid_url


class _Signals(QObject):
    log = pyqtSignal(str)
    discovery_done = pyqtSignal(int, int)   # website_id, count
    progress = pyqtSignal(str)


class URLManagerTab(QWidget):
    log_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._signals = _Signals()
        self._signals.log.connect(self.log_signal)
        self._signals.discovery_done.connect(self._on_discovery_done)
        self._signals.progress.connect(self._on_progress)
        self._build_ui()
        self.refresh_websites()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # ── Add website group ──
        add_group = QGroupBox("Add Website")
        add_layout = QHBoxLayout(add_group)
        add_layout.setSpacing(8)

        add_layout.addWidget(QLabel("URL:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        add_layout.addWidget(self.url_input, stretch=3)

        add_layout.addWidget(QLabel("Label:"))
        self.label_input = QLineEdit()
        self.label_input.setPlaceholderText("Optional label")
        add_layout.addWidget(self.label_input, stretch=1)

        self.btn_add = QPushButton("+ Add")
        self.btn_add.setObjectName("btn_primary")
        self.btn_add.clicked.connect(self._add_website)
        add_layout.addWidget(self.btn_add)

        layout.addWidget(add_group)

        # ── Splitter: websites table | discovered URLs table ──
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: websites
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        hdr_left = QHBoxLayout()
        hdr_left.addWidget(QLabel("Websites"))
        hdr_left.addStretch()

        self.btn_import = QPushButton("Import")
        self.btn_import.clicked.connect(self._import_urls)
        hdr_left.addWidget(self.btn_import)

        self.btn_export = QPushButton("Export")
        self.btn_export.clicked.connect(self._export_urls)
        hdr_left.addWidget(self.btn_export)

        left_layout.addLayout(hdr_left)

        self.websites_table = QTableWidget(0, 4)
        self.websites_table.setHorizontalHeaderLabels(["", "URL", "Label", "Actions"])
        self.websites_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.websites_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.websites_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.websites_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.websites_table.setColumnWidth(0, 36)
        self.websites_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.websites_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.websites_table.setAlternatingRowColors(True)
        self.websites_table.verticalHeader().setVisible(False)
        self.websites_table.itemSelectionChanged.connect(self._on_website_selected)
        left_layout.addWidget(self.websites_table)

        # Discover button
        discover_row = QHBoxLayout()
        self.btn_discover = QPushButton("Detect URLs from Sitemap")
        self.btn_discover.setObjectName("btn_primary")
        self.btn_discover.clicked.connect(self._discover_sitemap)
        discover_row.addWidget(self.btn_discover)

        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("color: #8b949e; font-size: 12px;")
        discover_row.addWidget(self.progress_label, stretch=1)
        left_layout.addLayout(discover_row)

        splitter.addWidget(left)

        # Right: discovered URLs
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)

        hdr_right = QHBoxLayout()
        self.discovered_label = QLabel("Discovered URLs  (select a website)")
        hdr_right.addWidget(self.discovered_label)
        hdr_right.addStretch()

        self.btn_clear_discovered = QPushButton("Clear")
        self.btn_clear_discovered.clicked.connect(self._clear_discovered)
        hdr_right.addWidget(self.btn_clear_discovered)

        right_layout.addLayout(hdr_right)

        self.discovered_table = QTableWidget(0, 3)
        self.discovered_table.setHorizontalHeaderLabels(["#", "URL", "Visits"])
        self.discovered_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.discovered_table.setAlternatingRowColors(True)
        self.discovered_table.verticalHeader().setVisible(False)
        self.discovered_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        right_layout.addWidget(self.discovered_table)

        splitter.addWidget(right)
        splitter.setSizes([400, 500])
        layout.addWidget(splitter, stretch=1)

        self._selected_website_id = None

    # ── Helpers ──

    def refresh_websites(self):
        websites = db.get_websites()
        self.websites_table.setRowCount(0)
        for site in websites:
            self._append_website_row(site)

    def _append_website_row(self, site: dict):
        row = self.websites_table.rowCount()
        self.websites_table.insertRow(row)

        # Enabled checkbox
        chk = QCheckBox()
        chk.setChecked(bool(site["enabled"]))
        chk.stateChanged.connect(lambda state, sid=site["id"]: db.toggle_website(sid, state == 2))
        cell = QWidget()
        cell_layout = QHBoxLayout(cell)
        cell_layout.addWidget(chk)
        cell_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cell_layout.setContentsMargins(0, 0, 0, 0)
        self.websites_table.setCellWidget(row, 0, cell)

        # URL
        url_item = QTableWidgetItem(site["url"])
        url_item.setData(Qt.ItemDataRole.UserRole, site["id"])
        self.websites_table.setItem(row, 1, url_item)

        # Label
        self.websites_table.setItem(row, 2, QTableWidgetItem(site["label"] or ""))

        # Actions
        action_widget = QWidget()
        action_layout = QHBoxLayout(action_widget)
        action_layout.setContentsMargins(4, 2, 4, 2)
        action_layout.setSpacing(4)

        btn_edit = QPushButton("Edit")
        btn_edit.setFixedHeight(24)
        btn_edit.setStyleSheet("padding: 2px 8px; font-size: 11px;")
        btn_edit.clicked.connect(lambda _, sid=site["id"]: self._edit_website(sid))
        action_layout.addWidget(btn_edit)

        btn_del = QPushButton("Delete")
        btn_del.setFixedHeight(24)
        btn_del.setObjectName("btn_danger")
        btn_del.setStyleSheet("padding: 2px 8px; font-size: 11px; background:#da3633; color:white; border:none; border-radius:4px;")
        btn_del.clicked.connect(lambda _, sid=site["id"]: self._delete_website(sid))
        action_layout.addWidget(btn_del)

        self.websites_table.setCellWidget(row, 3, action_widget)
        self.websites_table.setRowHeight(row, 38)

    def _add_website(self):
        url = normalise_url(self.url_input.text().strip())
        label = self.label_input.text().strip()
        if not is_valid_url(url):
            QMessageBox.warning(self, "Invalid URL", "Please enter a valid URL.")
            return
        db.add_website(url, label)
        self.url_input.clear()
        self.label_input.clear()
        self.refresh_websites()
        self.log_signal.emit(f"[URL] Added website: {url}")

    def _delete_website(self, website_id: int):
        confirm = QMessageBox.question(
            self, "Delete", "Delete this website and all its discovered URLs?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            db.delete_website(website_id)
            self.refresh_websites()
            self._selected_website_id = None
            self.discovered_table.setRowCount(0)

    def _edit_website(self, website_id: int):
        sites = db.get_websites()
        site = next((s for s in sites if s["id"] == website_id), None)
        if not site:
            return
        self.url_input.setText(site["url"])
        self.label_input.setText(site["label"] or "")
        db.delete_website(website_id)
        self.refresh_websites()

    def _on_website_selected(self):
        rows = self.websites_table.selectionModel().selectedRows()
        if not rows:
            return
        row = rows[0].row()
        item = self.websites_table.item(row, 1)
        if item:
            self._selected_website_id = item.data(Qt.ItemDataRole.UserRole)
            self._load_discovered_urls(self._selected_website_id)

    def _load_discovered_urls(self, website_id: int):
        urls = db.get_discovered_urls(website_id)
        self.discovered_table.setRowCount(0)
        self.discovered_label.setText(f"Discovered URLs  ({len(urls)} total)")
        for i, u in enumerate(urls):
            row = self.discovered_table.rowCount()
            self.discovered_table.insertRow(row)
            self.discovered_table.setItem(row, 0, QTableWidgetItem(str(i + 1)))
            item = QTableWidgetItem(u["url"])
            if u["visited"]:
                item.setForeground(Qt.GlobalColor.darkGray)
            self.discovered_table.setItem(row, 1, item)
            self.discovered_table.setItem(row, 2, QTableWidgetItem(str(u["visit_count"])))

    def _discover_sitemap(self):
        if not self._selected_website_id:
            QMessageBox.information(self, "Select Website", "Please select a website first.")
            return
        sites = db.get_websites()
        site = next((s for s in sites if s["id"] == self._selected_website_id), None)
        if not site:
            return

        self.btn_discover.setEnabled(False)
        self.progress_label.setText("Scanning sitemap…")
        self._signals.log.emit(f"[Sitemap] Scanning: {site['url']}")

        wid = self._selected_website_id
        url = site["url"]

        def run():
            def log_cb(msg):
                self._signals.log.emit(f"[Sitemap] {msg}")
                self._signals.progress.emit(msg[:60] + "…" if len(msg) > 60 else msg)

            found = discover_sitemap_urls(url, log_cb=log_cb)
            db.save_discovered_urls(wid, found)
            self._signals.discovery_done.emit(wid, len(found))

        threading.Thread(target=run, daemon=True).start()

    def _on_discovery_done(self, website_id: int, count: int):
        self.btn_discover.setEnabled(True)
        self.progress_label.setText(f"Found {count} URLs")
        if website_id == self._selected_website_id:
            self._load_discovered_urls(website_id)
        self.log_signal.emit(f"[Sitemap] Discovery complete: {count} URLs")

    def _on_progress(self, msg: str):
        self.progress_label.setText(msg)

    def _clear_discovered(self):
        if not self._selected_website_id:
            return
        db.clear_discovered_urls(self._selected_website_id)
        self.discovered_table.setRowCount(0)
        self.discovered_label.setText("Discovered URLs")

    def _import_urls(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import URLs", "", "Text Files (*.txt)")
        if not path:
            return
        count = 0
        with open(path) as f:
            for line in f:
                url = normalise_url(line.strip())
                if is_valid_url(url):
                    db.add_website(url)
                    count += 1
        self.refresh_websites()
        QMessageBox.information(self, "Import", f"Imported {count} URL(s).")

    def _export_urls(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export URLs", "urls.txt", "Text Files (*.txt)")
        if not path:
            return
        sites = db.get_websites()
        with open(path, "w") as f:
            for s in sites:
                f.write(s["url"] + "\n")
        QMessageBox.information(self, "Export", f"Exported {len(sites)} URL(s).")
