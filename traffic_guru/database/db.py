import sqlite3
import os
from pathlib import Path


DB_PATH = Path(__file__).parent.parent / "data.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS websites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL UNIQUE,
            label TEXT DEFAULT '',
            enabled INTEGER DEFAULT 1,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS discovered_urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            website_id INTEGER,
            url TEXT NOT NULL,
            title TEXT DEFAULT '',
            visited INTEGER DEFAULT 0,
            visit_count INTEGER DEFAULT 0,
            last_visited TIMESTAMP,
            FOREIGN KEY (website_id) REFERENCES websites(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS proxies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proxy TEXT NOT NULL UNIQUE,
            proxy_type TEXT DEFAULT 'http',
            enabled INTEGER DEFAULT 1,
            country TEXT DEFAULT 'Unknown',
            success_count INTEGER DEFAULT 0,
            fail_count INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );

        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            proxy TEXT,
            status TEXT DEFAULT 'pending',
            started_at TIMESTAMP,
            finished_at TIMESTAMP
        );
    """)

    try:
        cur.execute("PRAGMA table_info(proxies)")
        cols = {r["name"] for r in cur.fetchall()}
        if "country" not in cols:
            cur.execute("ALTER TABLE proxies ADD COLUMN country TEXT DEFAULT 'Unknown'")
    except Exception:
        pass

    defaults = {
        "delay_min": "3",
        "delay_max": "8",
        "scroll_speed": "medium",
        "random_mouse": "1",
        "click_links": "0",
        "max_browsers": "5",
        "views_per_url": "1",
        "use_proxy": "0",
        "rotate_proxy": "1",
        "require_proxy": "1",
        "headless": "0",
        "block_images": "0",
        "incognito": "0",
        "device_profile": "desktop",
    }
    for k, v in defaults.items():
        cur.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v)
        )

    cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('require_proxy', '1')")
    cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('device_profile', 'desktop')")

    conn.commit()
    conn.close()


# ---------- Websites ----------

def add_website(url: str, label: str = "") -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO websites (url, label) VALUES (?, ?)", (url, label)
    )
    conn.commit()
    rowid = cur.lastrowid
    conn.close()
    return rowid


def get_websites():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM websites ORDER BY added_at DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def delete_website(website_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM websites WHERE id=?", (website_id,))
    conn.commit()
    conn.close()


def update_website(website_id: int, url: str, label: str):
    conn = get_connection()
    conn.execute(
        "UPDATE websites SET url=?, label=? WHERE id=?", (url, label, website_id)
    )
    conn.commit()
    conn.close()


def toggle_website(website_id: int, enabled: bool):
    conn = get_connection()
    conn.execute(
        "UPDATE websites SET enabled=? WHERE id=?", (int(enabled), website_id)
    )
    conn.commit()
    conn.close()


# ---------- Discovered URLs ----------

def save_discovered_urls(website_id: int, urls: list[str]):
    conn = get_connection()
    cur = conn.cursor()
    for url in urls:
        cur.execute(
            "INSERT OR IGNORE INTO discovered_urls (website_id, url) VALUES (?, ?)",
            (website_id, url),
        )
    conn.commit()
    conn.close()


def replace_discovered_urls(website_id: int, urls: list[str]):
    """Replace all discovered URLs for a site (used after sitemap import with a user-chosen subset)."""
    seen: set[str] = set()
    ordered: list[str] = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            ordered.append(u)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM discovered_urls WHERE website_id=?", (website_id,))
    for url in ordered:
        cur.execute(
            "INSERT INTO discovered_urls (website_id, url) VALUES (?, ?)",
            (website_id, url),
        )
    conn.commit()
    conn.close()


def get_discovered_urls(website_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM discovered_urls WHERE website_id=? ORDER BY id",
        (website_id,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_all_pending_urls(limit: int = 0):
    conn = get_connection()
    cur = conn.cursor()
    q = """
        SELECT d.id, d.url, w.url as website
        FROM discovered_urls d
        JOIN websites w ON w.id = d.website_id
        WHERE w.enabled = 1
        ORDER BY d.id
    """
    if limit:
        q += f" LIMIT {limit}"
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def mark_url_visited(url_id: int):
    conn = get_connection()
    conn.execute(
        """UPDATE discovered_urls
           SET visited=1, visit_count=visit_count+1, last_visited=CURRENT_TIMESTAMP
           WHERE id=?""",
        (url_id,),
    )
    conn.commit()
    conn.close()


def clear_discovered_urls(website_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM discovered_urls WHERE website_id=?", (website_id,))
    conn.commit()
    conn.close()


# ---------- Proxies ----------

def add_proxy(proxy: str, proxy_type: str = "http") -> bool:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT OR IGNORE INTO proxies (proxy, proxy_type) VALUES (?, ?)",
            (proxy.strip(), proxy_type),
        )
        conn.commit()
        inserted = cur.rowcount > 0
    except Exception:
        inserted = False
    finally:
        conn.close()
    return inserted


def get_proxies(enabled_only=True):
    conn = get_connection()
    cur = conn.cursor()
    q = "SELECT * FROM proxies"
    if enabled_only:
        q += " WHERE enabled=1"
    q += " ORDER BY id DESC"
    cur.execute(q)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def delete_proxy(proxy_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM proxies WHERE id=?", (proxy_id,))
    conn.commit()
    conn.close()


def toggle_proxy(proxy_id: int, enabled: bool):
    conn = get_connection()
    conn.execute(
        "UPDATE proxies SET enabled=? WHERE id=?", (int(enabled), proxy_id)
    )
    conn.commit()
    conn.close()


def record_proxy_result(proxy: str, success: bool, country: str = None):
    conn = get_connection()
    if success:
        if country:
            conn.execute(
                "UPDATE proxies SET success_count=success_count+1, country=? WHERE proxy=?",
                (country, proxy),
            )
        else:
            conn.execute(
                "UPDATE proxies SET success_count=success_count+1 WHERE proxy=?", (proxy,)
            )
    else:
        conn.execute(
            "UPDATE proxies SET fail_count=fail_count+1 WHERE proxy=?", (proxy,)
        )
    conn.commit()
    conn.close()


# ---------- Settings ----------

def get_setting(key: str, default=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key=?", (key,))
    row = cur.fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key: str, value):
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value))
    )
    conn.commit()
    conn.close()


def get_all_settings() -> dict:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT key, value FROM settings")
    result = {r["key"]: r["value"] for r in cur.fetchall()}
    conn.close()
    return result


# ---------- Sessions ----------

def add_session(url: str, proxy: str = "") -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO sessions (url, proxy, status, started_at) VALUES (?, ?, 'running', CURRENT_TIMESTAMP)",
        (url, proxy),
    )
    conn.commit()
    sid = cur.lastrowid
    conn.close()
    return sid


def finish_session(session_id: int, status: str = "completed"):
    conn = get_connection()
    conn.execute(
        "UPDATE sessions SET status=?, finished_at=CURRENT_TIMESTAMP WHERE id=?",
        (status, session_id),
    )
    conn.commit()
    conn.close()


def get_session_stats() -> dict:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT status, COUNT(*) as cnt FROM sessions GROUP BY status")
    stats = {r["status"]: r["cnt"] for r in cur.fetchall()}
    cur.execute("SELECT COUNT(DISTINCT url) as cnt FROM discovered_urls")
    row = cur.fetchone()
    stats["total_urls"] = row["cnt"] if row else 0
    conn.close()
    return stats
