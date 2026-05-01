"""Main application window for Traffic Guru."""

from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTabWidget, QSplitter, QStatusBar, QMenuBar,
    QMenu, QMessageBox, QSizePolicy, QFrame
)
from PyQt6.QtGui import QFont, QAction

from database import db
from core.browser_automation import AutomationEngine
from license import license_manager

from ui.url_manager import URLManagerTab
from ui.automation_settings import AutomationSettingsTab
from ui.proxy_settings import ProxySettingsTab
from ui.dashboard import DashboardTab
from ui.log_console import LogConsole


class MainWindow(QMainWindow):
    _log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Traffic Guru — Professional Traffic Automation")
        self.setMinimumSize(1200, 750)
        self.resize(1400, 860)

        self.engine = AutomationEngine(log_cb=self._emit_log)
        self._log_signal.connect(self._append_log)

        self._build_menu()
        self._build_ui()
        self._update_control_buttons()

    def _emit_log(self, msg: str):
        self._log_signal.emit(msg)

    def _append_log(self, msg: str):
        self.log_console.append(msg)

    # ──────────────────────────────────────────────
    #  Menu
    # ──────────────────────────────────────────────

    def _build_menu(self):
        mb = self.menuBar()

        # File
        file_menu = mb.addMenu("File")
        act_exit = QAction("Exit", self)
        act_exit.triggered.connect(self.close)
        file_menu.addAction(act_exit)

        # License
        license_menu = mb.addMenu("License")
        act_info = QAction("License Info", self)
        act_info.triggered.connect(self._show_license_info)
        license_menu.addAction(act_info)

        act_deactivate = QAction("Deactivate", self)
        act_deactivate.triggered.connect(self._deactivate_license)
        license_menu.addAction(act_deactivate)

        # Help
        help_menu = mb.addMenu("Help")
        act_about = QAction("About Traffic Guru", self)
        act_about.triggered.connect(self._show_about)
        help_menu.addAction(act_about)

    # ──────────────────────────────────────────────
    #  UI
    # ──────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Header bar
        header = self._build_header()
        root_layout.addWidget(header)

        # Main splitter: tabs | log console
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setChildrenCollapsible(False)

        # Tabs area
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        # URL Manager
        self.url_tab = URLManagerTab()
        self.url_tab.log_signal.connect(self._append_log)
        self.tabs.addTab(self.url_tab, "  URLs  ")

        # Dashboard
        self.dashboard_tab = DashboardTab(engine=self.engine)
        self.tabs.addTab(self.dashboard_tab, "  Dashboard  ")

        # Automation Settings
        self.settings_tab = AutomationSettingsTab()
        self.tabs.addTab(self.settings_tab, "  Settings  ")

        # Proxy Settings
        self.proxy_tab = ProxySettingsTab()
        self.proxy_tab.log_signal.connect(self._append_log)
        self.tabs.addTab(self.proxy_tab, "  Proxies  ")

        splitter.addWidget(self.tabs)

        # Log console
        self.log_console = LogConsole()
        self.log_console.setMinimumHeight(160)
        splitter.addWidget(self.log_console)
        splitter.setSizes([600, 220])

        root_layout.addWidget(splitter, stretch=1)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready — Traffic Guru v1.0")

    def _build_header(self) -> QWidget:
        header = QFrame()
        header.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            "stop:0 #161b22, stop:1 #0d1117); "
            "border-bottom: 1px solid #30363d;"
        )
        header.setFixedHeight(64)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(16)

        # Logo
        logo = QLabel("Traffic Guru")
        logo.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        logo.setStyleSheet("color: #1f6feb; letter-spacing: -0.5px;")
        layout.addWidget(logo)

        tagline = QLabel("Professional Traffic Automation")
        tagline.setStyleSheet("color: #484f58; font-size: 12px;")
        layout.addWidget(tagline)

        layout.addStretch()

        # Control buttons
        self.btn_start = QPushButton("▶  Start")
        self.btn_start.setObjectName("btn_start")
        self.btn_start.setFixedSize(120, 38)
        self.btn_start.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.btn_start.clicked.connect(self._start_automation)
        layout.addWidget(self.btn_start)

        self.btn_pause = QPushButton("⏸  Pause")
        self.btn_pause.setObjectName("btn_pause")
        self.btn_pause.setFixedSize(110, 38)
        self.btn_pause.setFont(QFont("Segoe UI", 11))
        self.btn_pause.clicked.connect(self._pause_automation)
        layout.addWidget(self.btn_pause)

        self.btn_resume = QPushButton("▶  Resume")
        self.btn_resume.setObjectName("btn_resume")
        self.btn_resume.setFixedSize(120, 38)
        self.btn_resume.setFont(QFont("Segoe UI", 11))
        self.btn_resume.clicked.connect(self._resume_automation)
        layout.addWidget(self.btn_resume)

        self.btn_stop = QPushButton("■  Stop")
        self.btn_stop.setObjectName("btn_stop")
        self.btn_stop.setFixedSize(110, 38)
        self.btn_stop.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.btn_stop.clicked.connect(self._stop_automation)
        layout.addWidget(self.btn_stop)

        return header

    # ──────────────────────────────────────────────
    #  Automation controls
    # ──────────────────────────────────────────────

    def _collect_urls(self) -> list[str]:
        """Collect all enabled discovered URLs (optionally repeated by views_per_url)."""
        settings = db.get_all_settings()
        views = int(settings.get("views_per_url", 1))
        websites = db.get_websites()
        all_urls = []
        for site in websites:
            if not site["enabled"]:
                continue
            discovered = db.get_discovered_urls(site["id"])
            if not discovered:
                # Use the website URL itself
                all_urls.append(site["url"])
            else:
                for d in discovered:
                    all_urls.append(d["url"])

        # Repeat for views
        if views > 1:
            all_urls = all_urls * views

        return all_urls

    def _start_automation(self):
        if self.engine.is_running:
            return

        urls = self._collect_urls()
        if not urls:
            QMessageBox.warning(
                self, "No URLs",
                "No URLs found. Please add websites and detect their sitemap URLs first."
            )
            return

        settings = db.get_all_settings()
        proxies = self.proxy_tab.get_enabled_proxies()

        self.engine.start(urls, proxies, settings)
        self._update_control_buttons()
        self.tabs.setCurrentWidget(self.dashboard_tab)
        self.status_bar.showMessage(f"Automation running — {len(urls)} URL(s) queued")

    def _pause_automation(self):
        self.engine.pause()
        self._update_control_buttons()
        self.status_bar.showMessage("Automation paused")

    def _resume_automation(self):
        self.engine.resume()
        self._update_control_buttons()
        self.status_bar.showMessage("Automation resumed")

    def _stop_automation(self):
        self.engine.stop()
        self._update_control_buttons()
        self.status_bar.showMessage("Automation stopped")

    def _update_control_buttons(self):
        running = self.engine.is_running
        paused = self.engine.is_paused

        self.btn_start.setEnabled(not running)
        self.btn_pause.setEnabled(running and not paused)
        self.btn_resume.setEnabled(running and paused)
        self.btn_stop.setEnabled(running)

    # ──────────────────────────────────────────────
    #  License / About
    # ──────────────────────────────────────────────

    def _show_license_info(self):
        mid = license_manager.get_machine_id()
        active = license_manager.is_activated()
        status = "✓ Activated" if active else "✗ Not Activated"
        QMessageBox.information(
            self, "License Information",
            f"Status: {status}\nMachine ID: {mid}"
        )

    def _deactivate_license(self):
        confirm = QMessageBox.question(
            self, "Deactivate",
            "Are you sure you want to deactivate your license?\n"
            "You will need to re-enter your license key on next launch.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            license_manager.deactivate()
            QMessageBox.information(self, "Deactivated", "License deactivated. The software will close.")
            self.close()

    def _show_about(self):
        QMessageBox.about(
            self, "About Traffic Guru",
            "<b>Traffic Guru v1.0</b><br>"
            "Professional Web Traffic Automation Software<br><br>"
            "Built with Python + PyQt6 + Selenium<br>"
            "<br>© 2024 Traffic Guru. All rights reserved."
        )
