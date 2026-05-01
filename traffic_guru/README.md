# Traffic Guru — Professional Web Traffic Automation

## Overview
Traffic Guru is a cross-platform (Windows & macOS) Python desktop application that automates web traffic generation by visiting URLs discovered from website sitemaps.

## Requirements
- Python 3.10+
- Google Chrome installed
- pip

## Installation

```bash
cd traffic_guru
pip install -r requirements.txt
```

## Running the App

```bash
python main.py
```

## First Launch — License Activation
On first launch the activation dialog appears.  
Generate a key using the admin tool:

```bash
python generate_license.py
```

Copy the printed key and paste it into the activation dialog.

## Features
- **URL Manager** — add/edit/delete/import/export websites; auto-detect blog post URLs via sitemap
- **Automation Engine** — concurrent browser sessions with auto-scroll, random mouse movement, and internal link clicking
- **Proxy Support** — HTTP/HTTPS/SOCKS4/SOCKS5, bulk import, per-session rotation
- **Settings** — configurable delays, scroll speed, views per URL, concurrent browser limit, headless mode
- **Dashboard** — real-time stats: active/completed/error sessions, queue depth
- **Live Log Console** — colour-coded log output with auto-scroll
- **License System** — machine-bound key activation with encrypted local storage

## Building a Standalone Executable

### Windows
```bash
pip install pyinstaller
pyinstaller --noconfirm --onedir --windowed --name "TrafficGuru" main.py
```

### macOS
```bash
pip install pyinstaller
pyinstaller --noconfirm --onedir --windowed --name "TrafficGuru" main.py
```

The dist/TrafficGuru folder contains the runnable app.

## Project Structure
```
traffic_guru/
├── main.py                  # Entry point
├── generate_license.py      # Admin: generate license keys
├── requirements.txt
├── database/
│   └── db.py                # SQLite layer (websites, proxies, sessions, settings)
├── core/
│   ├── sitemap_parser.py    # Sitemap discovery & URL extraction
│   ├── browser_automation.py# Selenium automation engine
│   └── proxy_manager.py     # Proxy rotation helpers
├── license/
│   └── license_manager.py   # HMAC key validation + encrypted activation storage
├── ui/
│   ├── styles.py            # Global dark stylesheet
│   ├── main_window.py       # Application shell + control buttons
│   ├── url_manager.py       # URL & sitemap tab
│   ├── automation_settings.py# Settings tab
│   ├── proxy_settings.py    # Proxy management tab
│   ├── dashboard.py         # Real-time stats dashboard
│   ├── log_console.py       # Colour-coded log console
│   └── license_dialog.py    # Activation dialog
└── utils/
    └── helpers.py           # URL normalisation helpers
```
