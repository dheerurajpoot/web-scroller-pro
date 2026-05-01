"""Dashboard tab — real-time stats."""

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout,
    QSizePolicy, QGroupBox
)
from PyQt6.QtGui import QFont, QColor
from database import db


class StatCard(QFrame):
    def __init__(self, title: str, value: str = "0", color: str = "#1f6feb"):
        super().__init__()
        self.setObjectName("card")
        self.setMinimumWidth(160)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(110)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(6)

        self._val_label = QLabel(value)
        self._val_label.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        self._val_label.setStyleSheet(f"color: {color};")
        layout.addWidget(self._val_label)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #8b949e; font-size: 11px; text-transform: uppercase; letter-spacing: 1px;")
        layout.addWidget(title_label)

    def set_value(self, v):
        self._val_label.setText(str(v))


class DashboardTab(QWidget):
    def __init__(self, engine=None, parent=None):
        super().__init__(parent)
        self.engine = engine
        self._build_ui()

        self._timer = QTimer()
        self._timer.timeout.connect(self._refresh)
        self._timer.start(2000)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        header = QLabel("Dashboard")
        header.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header.setStyleSheet("color: #e6edf3;")
        layout.addWidget(header)

        # Stat cards row
        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)

        self.card_active = StatCard("Active Sessions", "0", "#1f6feb")
        self.card_completed = StatCard("Completed", "0", "#3fb950")
        self.card_errors = StatCard("Errors", "0", "#f85149")
        self.card_queued = StatCard("Queued", "0", "#d29922")
        self.card_total_urls = StatCard("Total URLs", "0", "#a371f7")

        for card in [self.card_active, self.card_completed, self.card_errors,
                     self.card_queued, self.card_total_urls]:
            cards_row.addWidget(card)

        layout.addLayout(cards_row)

        # Status indicator
        status_row = QHBoxLayout()
        self.status_indicator = QLabel("● Idle")
        self.status_indicator.setStyleSheet("color: #8b949e; font-size: 14px; font-weight: 600;")
        status_row.addWidget(self.status_indicator)
        status_row.addStretch()
        layout.addLayout(status_row)

        # Recent sessions group
        recent_group = QGroupBox("Recent Sessions")
        recent_layout = QVBoxLayout(recent_group)

        from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
        self.recent_table = QTableWidget(0, 4)
        self.recent_table.setHorizontalHeaderLabels(["URL", "Proxy", "Status", "Finished"])
        self.recent_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.recent_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.recent_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.recent_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.recent_table.verticalHeader().setVisible(False)
        self.recent_table.setAlternatingRowColors(True)
        self.recent_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        recent_layout.addWidget(self.recent_table)

        layout.addWidget(recent_group, stretch=1)

    def set_engine(self, engine):
        self.engine = engine

    def _refresh(self):
        stats = db.get_session_stats()
        self.card_completed.set_value(stats.get("completed", 0))
        self.card_errors.set_value(stats.get("error", 0))
        self.card_total_urls.set_value(stats.get("total_urls", 0))

        if self.engine:
            active = self.engine.active_count()
            queued = self.engine.queue_count()
            self.card_active.set_value(active)
            self.card_queued.set_value(queued)

            if self.engine.is_running and not self.engine.is_paused:
                self.status_indicator.setText("● Running")
                self.status_indicator.setStyleSheet("color: #3fb950; font-size: 14px; font-weight: 600;")
            elif self.engine.is_paused:
                self.status_indicator.setText("⏸ Paused")
                self.status_indicator.setStyleSheet("color: #d29922; font-size: 14px; font-weight: 600;")
            else:
                self.status_indicator.setText("● Idle")
                self.status_indicator.setStyleSheet("color: #8b949e; font-size: 14px; font-weight: 600;")

        self._load_recent_sessions()

    def _load_recent_sessions(self):
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT url, proxy, status, finished_at FROM sessions ORDER BY id DESC LIMIT 30"
        )
        rows = cur.fetchall()
        conn.close()

        self.recent_table.setRowCount(0)
        for r in rows:
            row = self.recent_table.rowCount()
            self.recent_table.insertRow(row)
            self.recent_table.setItem(row, 0, _trunc_item(r["url"] or "", 60))
            self.recent_table.setItem(row, 1, _trunc_item(r["proxy"] or "none", 30))

            status_item = _trunc_item(r["status"] or "", 20)
            color_map = {
                "completed": "#3fb950",
                "error": "#f85149",
                "stopped": "#d29922",
                "running": "#1f6feb",
            }
            c = color_map.get(r["status"], "#8b949e")
            status_item.setForeground(QColor(c))
            self.recent_table.setItem(row, 2, status_item)
            self.recent_table.setItem(row, 3, _trunc_item(r["finished_at"] or "—", 20))


def _trunc_item(text: str, max_len: int) -> "QTableWidgetItem":
    from PyQt6.QtWidgets import QTableWidgetItem
    if len(text) > max_len:
        text = text[:max_len - 1] + "…"
    return QTableWidgetItem(text)
