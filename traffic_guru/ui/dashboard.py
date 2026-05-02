"""Dashboard tab — real-time stats."""

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QSizePolicy, QGroupBox,
)
from PyQt6.QtGui import QFont, QColor
from database import db


class StatCard(QFrame):
    """Compact metric card: caption on top, large value — fixed height, no horizontal scroll."""

    def __init__(self, title: str, value: str = "0", accent: str = "#58a6ff"):
        super().__init__()
        self.setObjectName("stat_card")
        self._accent = accent
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(108)
        self.setMinimumWidth(96)
        self.setMaximumWidth(400)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setWordWrap(True)
        title_label.setStyleSheet(
            "color: #8b949e; font-size: 10px; font-weight: 700; "
            "text-transform: uppercase; letter-spacing: 0.85px;"
        )
        layout.addWidget(title_label)

        self._val_label = QLabel(value)
        self._val_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        self._val_label.setStyleSheet(f"color: {accent};")
        self._val_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        layout.addWidget(self._val_label)
        layout.addStretch()

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
        layout.setSpacing(18)

        header = QLabel("Dashboard")
        header.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header.setStyleSheet("color: #e6edf3;")
        layout.addWidget(header)

        sub = QLabel("Session overview and recent activity")
        sub.setStyleSheet("color: #8b949e; font-size: 12px; margin-top: -12px;")
        layout.addWidget(sub)

        # Stat cards — single fixed row, equal stretch (no scroll area)
        cards_row = QWidget()
        cards_layout = QHBoxLayout(cards_row)
        cards_layout.setContentsMargins(0, 4, 0, 0)
        cards_layout.setSpacing(12)

        self.card_active = StatCard("Active", "0", "#58a6ff")
        self.card_completed = StatCard("Completed", "0", "#3fb950")
        self.card_errors = StatCard("Errors", "0", "#f85149")
        self.card_queued = StatCard("Queued", "0", "#d29922")
        self.card_total_urls = StatCard("Total URLs", "0", "#a371f7")

        for card in (
            self.card_active,
            self.card_completed,
            self.card_errors,
            self.card_queued,
            self.card_total_urls,
        ):
            cards_layout.addWidget(card, stretch=1)

        layout.addWidget(cards_row)

        # Status pill
        status_row = QHBoxLayout()
        self.status_indicator = QLabel("●  Idle")
        self.status_indicator.setObjectName("dashboard_status")
        self.status_indicator.setStyleSheet(
            "color: #8b949e; font-size: 13px; font-weight: 600; "
            "padding: 6px 14px; background: #161b22; border: 1px solid #30363d; "
            "border-radius: 20px;"
        )
        status_row.addWidget(self.status_indicator)
        status_row.addStretch()
        layout.addLayout(status_row)

        # Recent sessions
        recent_group = QGroupBox("Recent sessions")
        recent_layout = QVBoxLayout(recent_group)
        recent_layout.setSpacing(10)

        from PyQt6.QtWidgets import (
            QTableWidget,
            QTableWidgetItem,
            QHeaderView,
            QAbstractItemView,
        )

        self.recent_table = QTableWidget(0, 4)
        self.recent_table.setHorizontalHeaderLabels(["URL", "Proxy", "Status", "Finished"])
        self.recent_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.recent_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.recent_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.recent_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.recent_table.verticalHeader().setVisible(False)
        self.recent_table.setAlternatingRowColors(True)
        self.recent_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.recent_table.setMinimumHeight(200)
        self.recent_table.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
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
                self.status_indicator.setText("●  Running")
                self.status_indicator.setStyleSheet(
                    "color: #3fb950; font-size: 13px; font-weight: 600; "
                    "padding: 6px 14px; background: #0d1f12; border: 1px solid #238636; "
                    "border-radius: 20px;"
                )
            elif self.engine.is_paused:
                self.status_indicator.setText("⏸  Paused")
                self.status_indicator.setStyleSheet(
                    "color: #d29922; font-size: 13px; font-weight: 600; "
                    "padding: 6px 14px; background: #1c1608; border: 1px solid #9e6a03; "
                    "border-radius: 20px;"
                )
            else:
                self.status_indicator.setText("●  Idle")
                self.status_indicator.setStyleSheet(
                    "color: #8b949e; font-size: 13px; font-weight: 600; "
                    "padding: 6px 14px; background: #161b22; border: 1px solid #30363d; "
                    "border-radius: 20px;"
                )

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
                "running": "#58a6ff",
            }
            c = color_map.get(r["status"], "#8b949e")
            status_item.setForeground(QColor(c))
            self.recent_table.setItem(row, 2, status_item)
            self.recent_table.setItem(row, 3, _trunc_item(r["finished_at"] or "—", 20))


def _trunc_item(text: str, max_len: int) -> "QTableWidgetItem":
    from PyQt6.QtWidgets import QTableWidgetItem

    if len(text) > max_len:
        text = text[: max_len - 1] + "…"
    return QTableWidgetItem(text)
