import sqlite3
from database.db import DB_PATH, get_proxies
try:
    proxies = get_proxies(enabled_only=False)
    print("Proxies:", proxies)
except Exception as e:
    print("Error:", e)
