# Traffic Guru — Professional Web Traffic Automation

## Overview

Traffic Guru is a cross-platform (Windows & macOS) Python desktop application that automates web traffic generation by visiting URLs discovered from website sitemaps.

## Requirements

- Python 3.10+
- Google Chrome installed
- pip (bundled with Python; used inside a virtual environment below)

On macOS, use **`python3`** (there is often no `python` on PATH).  
Homebrew Python is **PEP 668**–managed: installing packages with `python3 -m pip install …` into the system interpreter fails with `externally-managed-environment`. Use a **virtual environment** (recommended below).

## 🚀 Quick Start (Simple Commands)

Here are the only commands you really need to know:

1. **Setup everything** (One-time only):

    ```bash
    cd traffic_guru
    bash setup_venv.sh
    ```

2. **Generate your License Key**:

    ```bash
    # Make sure you are in the traffic_guru folder
    ./.venv/bin/python generate_license.py
    ```

3. **Run the App**:
    ```bash
    ./.venv/bin/python main.py
    ```

---

## Detailed Installation

### macOS / Linux (recommended)

One-shot setup (creates `traffic_guru/.venv` and installs `requirements.txt`):

```bash
cd traffic_guru
bash setup_venv.sh
```

Or manually:

```bash
cd traffic_guru
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Windows

```bat
cd traffic_guru
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Running the App

After activating the venv (`source .venv/bin/activate` on macOS/Linux, or `.venv\Scripts\activate` on Windows):

```bash
python main.py
```

Without activating (macOS / Linux):

```bash
./.venv/bin/python main.py
```

### Chrome / ChromeDriver

The app tries **Selenium’s built-in driver manager** first, then **webdriver-manager** with a corrected binary path (avoids macOS `Exec format error` when a wrong file inside the Chrome bundle is selected).  
If automation still fails to start Chrome, install a matching [Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/) driver and point to it:

```bash
export CHROMEDRIVER_PATH="/path/to/chromedriver"
python main.py
```

## First Launch — License Activation

On first launch the activation dialog appears.  
Generate a key using the admin tool:

```bash
python3 generate_license.py
```

Copy the printed key and paste it into the activation dialog.

After **Detect URLs from sitemap**, you are asked **how many URLs to import** (defaults to up to 100). That replaces the previous discovered list for that website.

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
python -m pip install pyinstaller
pyinstaller --noconfirm --onedir --windowed --name "TrafficGuru" main.py
```

### macOS

```bash
python3 -m pip install pyinstaller
pyinstaller --noconfirm --onedir --windowed --name "TrafficGuru" main.py
```

The dist/TrafficGuru folder contains the runnable app.

## Project Structure

```
traffic_guru/
├── main.py                  # Entry point
├── generate_license.py      # Admin: generate license keys
├── setup_venv.sh            # macOS/Linux: create .venv + install deps
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
