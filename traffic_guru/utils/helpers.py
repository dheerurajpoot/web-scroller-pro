"""Miscellaneous helpers."""
import re
import requests
from urllib.parse import urlparse


def check_proxy(proxy_str: str, proxy_type: str = "http") -> tuple[bool, str, str]:
    """
    Check if a proxy is working and return (success, ip, country).
    proxy_str: host:port or user:pass@host:port or scheme://...
    """
    proxy_url = proxy_str
    if "://" not in proxy_url:
        proxy_url = f"{proxy_type}://{proxy_url}"
    
    # Normalise socks5h to socks5 for requests if needed, 
    # but requests handles socks5:// usually by trying to resolve locally.
    # socks5h:// tells it to resolve via proxy.
    if proxy_url.startswith("socks5://"):
        proxy_url = proxy_url.replace("socks5://", "socks5h://")

    proxies = {
        "http": proxy_url,
        "https": proxy_url,
    }

    try:
        # Use ip-api.com to get IP and country
        # We use a user-agent to look like a real browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        }
        response = requests.get(
            "http://ip-api.com/json/",
            proxies=proxies,
            headers=headers,
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                return True, data.get("query"), data.get("country")
            else:
                return False, data.get("message", "API Error"), "Unknown"
        return False, f"HTTP {response.status_code}", "Unknown"
    except Exception as e:
        return False, str(e), "Unknown"


def normalise_url(url: str) -> str:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url.rstrip("/")


def is_valid_url(url: str) -> bool:
    try:
        r = urlparse(url)
        return r.scheme in ("http", "https") and bool(r.netloc)
    except Exception:
        return False


def format_duration(seconds: float) -> str:
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h {m}m {s}s"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"
