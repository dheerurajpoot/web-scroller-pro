"""
Sitemap discovery and URL extraction.

Order of detection:
  1. robots.txt → Sitemap: directive
  2. Common sitemap paths  (/sitemap.xml, /sitemap_index.xml, /post-sitemap.xml, …)
  3. HTML <link> tag with rel="sitemap"

Handles:
  - Sitemap index files (nested sitemaps)
  - Regular sitemaps (<url><loc>…)
  - Google News / image / video sitemaps (same <loc> extraction)
"""

import re
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}
TIMEOUT = 15
MAX_URLS = 2000

COMMON_SITEMAP_PATHS = [
    "/sitemap.xml",
    "/sitemap_index.xml",
    "/sitemap-index.xml",
    "/post-sitemap.xml",
    "/page-sitemap.xml",
    "/category-sitemap.xml",
    "/wp-sitemap.xml",
    "/news-sitemap.xml",
    "/sitemap/",
    "/sitemap1.xml",
]


def _base(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


def _get(url: str, session: requests.Session, timeout=TIMEOUT):
    resp = session.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
    resp.raise_for_status()
    return resp


def discover_sitemap_urls(website_url: str, log_cb=None) -> list[str]:
    """
    Given a website URL, return a list of post/page URLs found via sitemap.
    log_cb(msg) will be called with progress messages if supplied.
    """
    def log(msg):
        if log_cb:
            log_cb(msg)

    base = _base(website_url)
    session = requests.Session()
    sitemap_urls: list[str] = []

    # 1. Try robots.txt
    try:
        robots = _get(f"{base}/robots.txt", session).text
        for line in robots.splitlines():
            if line.lower().startswith("sitemap:"):
                sm = line.split(":", 1)[1].strip()
                if sm not in sitemap_urls:
                    sitemap_urls.append(sm)
                    log(f"Found sitemap in robots.txt: {sm}")
    except Exception as e:
        log(f"robots.txt not available: {e}")

    # 2. Try common paths
    for path in COMMON_SITEMAP_PATHS:
        url = base + path
        if url not in sitemap_urls:
            try:
                r = session.head(url, headers=HEADERS, timeout=8, allow_redirects=True)
                if r.status_code == 200:
                    sitemap_urls.append(url)
                    log(f"Found sitemap at: {url}")
            except Exception:
                pass

    # 3. HTML <link rel="sitemap">
    try:
        html = _get(website_url, session).text
        soup = BeautifulSoup(html, "lxml")
        tag = soup.find("link", rel=re.compile("sitemap", re.I))
        if tag and tag.get("href"):
            sm = urljoin(website_url, tag["href"])
            if sm not in sitemap_urls:
                sitemap_urls.append(sm)
                log(f"Found sitemap in HTML: {sm}")
    except Exception as e:
        log(f"HTML parse skipped: {e}")

    if not sitemap_urls:
        log("No sitemap found for this website.")
        return []

    # Parse all discovered sitemaps
    all_page_urls: list[str] = []
    visited_sitemaps: set[str] = set()

    def parse_sitemap(sm_url: str, depth=0):
        if sm_url in visited_sitemaps or len(all_page_urls) >= MAX_URLS:
            return
        visited_sitemaps.add(sm_url)
        log(f"Parsing sitemap: {sm_url}")
        try:
            resp = _get(sm_url, session)
            content = resp.text
            soup = BeautifulSoup(content, "xml")

            # Sitemap index
            index_locs = soup.find_all("sitemap")
            if index_locs:
                for tag in index_locs:
                    loc = tag.find("loc")
                    if loc:
                        child_url = loc.get_text(strip=True)
                        parse_sitemap(child_url, depth + 1)
                        if len(all_page_urls) >= MAX_URLS:
                            return
            else:
                # Regular sitemap
                for url_tag in soup.find_all("url"):
                    loc = url_tag.find("loc")
                    if loc:
                        page_url = loc.get_text(strip=True)
                        if page_url not in all_page_urls:
                            all_page_urls.append(page_url)

        except Exception as e:
            log(f"Error parsing {sm_url}: {e}")

    for sm in sitemap_urls:
        parse_sitemap(sm)
        if len(all_page_urls) >= MAX_URLS:
            break

    log(f"Discovered {len(all_page_urls)} URLs.")
    return all_page_urls[:MAX_URLS]
