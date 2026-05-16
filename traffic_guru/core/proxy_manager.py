"""
Proxy rotation manager.
Supports http, https, socks4, socks5 proxies.

Proxy string formats accepted:
  host:port
  host:port:user:pass
  protocol://host:port
  protocol://user:pass@host:port
"""

import itertools
import threading
from typing import Optional

from database import db


class ProxyManager:
    def __init__(self):
        self._lock = threading.Lock()
        self._proxies: list[dict] = []
        self._cycle = None
        self.reload()

    def reload(self):
        with self._lock:
            self._proxies = db.get_proxies(enabled_only=True)
            if self._proxies:
                self._cycle = itertools.cycle(self._proxies)
            else:
                self._cycle = None

    def next_proxy(self) -> Optional[dict]:
        """Return the next proxy dict or None if no proxies configured."""
        with self._lock:
            if not self._cycle:
                return None
            return next(self._cycle)

    def build_selenium_proxy(self, proxy_dict: dict) -> Optional[dict]:
        """
        Build a Selenium-compatible proxy options dict.
        Returns e.g. {"httpProxy": "host:port", "proxyType": "MANUAL"}
        """
        if not proxy_dict:
            return None

        raw = proxy_dict["proxy"].strip()
        ptype = proxy_dict.get("proxy_type", "http").lower()

        # Normalise raw string
        if "://" not in raw:
            raw = f"{ptype}://{raw}"

        from urllib.parse import urlparse
        p = urlparse(raw)
        host = p.hostname
        port = p.port or 8080
        netloc = f"{host}:{port}"

        if ptype in ("socks4", "socks5"):
            return {
                "proxyType": "MANUAL",
                "socksProxy": netloc,
                "socksVersion": 5 if ptype == "socks5" else 4,
            }
        else:
            return {
                "proxyType": "MANUAL",
                "httpProxy": netloc,
                "sslProxy": netloc,
            }

    @staticmethod
    def parse_proxy_line(line: str) -> Optional[tuple[str, str]]:
        """
        Parse a single line from a proxy list file/text.
        Returns (proxy_string, type) or None if invalid.
        """
        line = line.strip()
        if not line or line.startswith("#"):
            return None

        # Already has scheme
        for scheme in ("socks5://", "socks4://", "https://", "http://"):
            if line.lower().startswith(scheme):
                ptype = scheme.rstrip("://").lower()
                addr = line[len(scheme):]
                return addr, ptype

        # user:pass@host:port or host:port:user:pass
        parts = line.split(":")
        if len(parts) == 4:
            # ip:port:user:pass -> user:pass@ip:port
            return f"{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}", "http"
        elif len(parts) == 2:
            return line, "http"

        return line, "http"
