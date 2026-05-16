import sqlite3
from database.db import DB_PATH, get_proxies
from urllib.parse import urlparse

proxies = get_proxies(enabled_only=False)
for p in proxies:
    print(f"Testing proxy {p['proxy']}")
    raw = p["proxy"]
    ptype = p["proxy_type"]
    p_url = raw if "://" in raw else f"http://{raw}"
    parsed = urlparse(p_url)
    
    host = parsed.hostname or raw
    try:
        port = str(parsed.port) if parsed.port else ""
    except ValueError:
        port = "Invalid"
    user = parsed.username or ""
    pwd = parsed.password or ""
    print(f"host={host}, port={port}, user={user}, pwd={pwd}")
    
    total = p["success_count"] + p["fail_count"]
    status = "Untested"
    if total > 0:
        success_rate = p["success_count"] / total
        status = "Working" if success_rate > 0.5 else "Failing"
    print(f"status={status}")
