"""
Browser automation engine for Traffic Guru.

Each BrowserSession opens a Chrome instance (headless optional),
navigates to a URL, and performs auto-scroll with random delays.
"""

import itertools
import json
import os
import random
import threading
import time
from typing import Callable, Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException

try:
    from webdriver_manager.chrome import ChromeDriverManager
    _WDM_AVAILABLE = True
except ImportError:
    _WDM_AVAILABLE = False

from database import db
from utils.helpers import check_proxy


def _resolve_chromedriver_binary(installed_path: str) -> str:
    """
    webdriver-manager sometimes returns a non-executable file (e.g. THIRD_PARTY_NOTICES.chromedriver)
    inside the Chrome-for-Testing bundle. Return the real chromedriver binary next to it.
    """
    installed_path = os.path.abspath(installed_path)
    directory = os.path.dirname(installed_path)

    def _try(candidate: str) -> Optional[str]:
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
        return None

    for name in ("chromedriver", "chromedriver.exe"):
        hit = _try(os.path.join(directory, name))
        if hit:
            return hit

    parent = os.path.dirname(directory)
    for name in ("chromedriver", "chromedriver.exe"):
        hit = _try(os.path.join(parent, name))
        if hit:
            return hit

    if os.path.isdir(directory):
        for entry in sorted(os.listdir(directory)):
            sub = os.path.join(directory, entry)
            if os.path.isdir(sub):
                for name in ("chromedriver", "chromedriver.exe"):
                    hit = _try(os.path.join(sub, name))
                    if hit:
                        return hit

    hit = _try(installed_path)
    if hit:
        return hit

    return installed_path


def _create_chrome_service() -> Optional[Service]:
    """Prefer explicit chromedriver from env, then webdriver-manager with a resolved binary path."""
    env_path = os.environ.get("CHROMEDRIVER_PATH", "").strip()
    if env_path and os.path.isfile(env_path) and os.access(env_path, os.X_OK):
        return Service(env_path)
    if _WDM_AVAILABLE:
        raw = ChromeDriverManager().install()
        exe = _resolve_chromedriver_binary(raw)
        return Service(exe)
    return None


# ──────────────────────────────────────────────
#  Session
# ──────────────────────────────────────────────

class BrowserSession(threading.Thread):
    """
    A single browser session running in its own thread.
    """

    def __init__(
        self,
        url: str,
        settings: dict,
        proxy: Optional[dict] = None,
        log_cb: Optional[Callable[[str], None]] = None,
        done_cb: Optional[Callable[["BrowserSession"], None]] = None,
    ):
        super().__init__(daemon=True)
        self.url = url
        self.settings = settings
        self.proxy = proxy
        self.log_cb = log_cb
        self.done_cb = done_cb
        self.driver: Optional[webdriver.Chrome] = None
        self._stop_event = threading.Event()
        self._paused = threading.Event()
        self._paused.set()  # not paused by default
        self.status = "pending"
        self.session_id: Optional[int] = None

    def log(self, msg: str):
        if self.log_cb:
            self.log_cb(msg)

    def stop(self):
        self._stop_event.set()
        self._paused.set()

    def pause(self):
        self._paused.clear()

    def resume(self):
        self._paused.set()

    def _build_options(self) -> ChromeOptions:
        opts = ChromeOptions()
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-infobars")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_argument("--disable-notifications")
        opts.add_argument("--disable-popup-blocking")
        opts.add_argument("--disable-save-password-bubble")
        opts.add_argument("--no-first-run")
        opts.add_argument("--no-default-browser-check")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--no-sandbox")
        
        # Better WebRTC Leak Protection & Language/Timezone spoofing prep
        prefs = {
            "webrtc.ip_handling_policy": "disable_non_proxied_udp",
            "webrtc.multiple_routes_enabled": False,
            "webrtc.nonproxied_udp_enabled": False,
            "profile.default_content_setting_values.notifications": 2,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
        }

        device_profile = (self.settings.get("device_profile") or "desktop").lower()
        if device_profile == "mix":
            device_profile = "mixed"

        if device_profile == "mixed":
            device_profile = random.choice(["desktop", "mobile", "tablet"])

        desktop_uas = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        ]
        mobile_uas = [
            "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
        ]
        tablet_uas = [
            "Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 14; SM-X900) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        ]

        proxy_host = None
        proxy_port = None
        proxy_user = None
        proxy_pwd = None
        proxy_type = None
        needs_auth_proxy = False
        self._needs_auth_proxy = False

        if self.proxy:
            raw = (self.proxy.get("proxy") or "").strip()
            proxy_type = (self.proxy.get("proxy_type") or "http").lower()

            if "://" in raw:
                from urllib.parse import urlparse
                parsed = urlparse(raw)
                proxy_host = parsed.hostname
                proxy_port = str(parsed.port or (443 if parsed.scheme == "https" else 80))
                proxy_user = parsed.username
                proxy_pwd = parsed.password
            else:
                if "@" in raw:
                    user_part, host_part = raw.split("@", 1)
                    user_parts = user_part.split(":", 1)
                    host_parts = host_part.split(":", 1)
                    proxy_user = user_parts[0] if len(user_parts) > 0 else None
                    proxy_pwd = user_parts[1] if len(user_parts) > 1 else None
                    proxy_host = host_parts[0] if len(host_parts) > 0 else None
                    proxy_port = host_parts[1] if len(host_parts) > 1 else "80"
                else:
                    # Support:
                    # - host:port
                    # - host:port:username:password
                    # (documented in core/proxy_manager.py and UI placeholder)
                    parts = raw.split(":")
                    if len(parts) >= 4:
                        proxy_host = parts[0]
                        proxy_port = parts[1]
                        proxy_user = parts[2]
                        proxy_pwd = ":".join(parts[3:]) if len(parts) > 3 else ""
                    else:
                        proxy_host = parts[0] if len(parts) > 0 else None
                        proxy_port = parts[1] if len(parts) > 1 else "80"

            needs_auth_proxy = bool(proxy_user and proxy_pwd)
            self._needs_auth_proxy = needs_auth_proxy

        if self.settings.get("headless") == "1":
            # --headless=new is required for extensions to work in headless mode
            opts.add_argument("--headless=new")
            # Sometimes Chrome still detects headless, let's add extra masks
            opts.add_argument("--disable-gpu")
        
        if self.settings.get("incognito") == "1" and not needs_auth_proxy:
            opts.add_argument("--incognito")

        # Performance: Block images to save bandwidth
        if self.settings.get("block_images") == "1":
            prefs["profile.managed_default_content_settings.images"] = 2

        opts.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        opts.add_experimental_option("useAutomationExtension", False)
        opts.add_experimental_option("prefs", prefs)

        if device_profile == "desktop":
            opts.add_argument(f"--user-agent={random.choice(desktop_uas)}")
            if self.settings.get("headless") != "1":
                w = random.randint(1200, 1700)
                h = random.randint(780, 1000)
                opts.add_argument(f"--window-size={w},{h}")
            else:
                opts.add_argument("--window-size=1920,1080")
        elif device_profile == "mobile":
            ua = random.choice(mobile_uas)
            opts.add_experimental_option(
                "mobileEmulation",
                {
                    "deviceMetrics": {
                        "width": random.choice([360, 375, 390, 412]),
                        "height": random.choice([740, 780, 820, 915]),
                        "pixelRatio": random.choice([2.75, 3.0, 3.5]),
                    },
                    "userAgent": ua,
                },
            )
        elif device_profile == "tablet":
            ua = random.choice(tablet_uas)
            opts.add_experimental_option(
                "mobileEmulation",
                {
                    "deviceMetrics": {
                        "width": random.choice([768, 820, 834]),
                        "height": random.choice([1024, 1080, 1194]),
                        "pixelRatio": random.choice([2.0, 2.5]),
                    },
                    "userAgent": ua,
                },
            )
        else:
            opts.add_argument(f"--user-agent={random.choice(desktop_uas)}")
            if self.settings.get("headless") != "1":
                w = random.randint(1200, 1700)
                h = random.randint(780, 1000)
                opts.add_argument(f"--window-size={w},{h}")
            else:
                opts.add_argument("--window-size=1920,1080")

        # Proxy Configuration
        if proxy_host and proxy_port and proxy_type:
            if needs_auth_proxy:
                ext_dir = self._create_proxy_extension(proxy_type, proxy_host, proxy_port, proxy_user, proxy_pwd)
                opts.add_argument(f"--disable-extensions-except={ext_dir}")
                opts.add_argument(f"--load-extension={ext_dir}")
                self._proxy_ext_dir = ext_dir
            else:
                chrome_proxy_type = "http" if proxy_type == "https" else proxy_type
                proxy_url = f"{chrome_proxy_type}://{proxy_host}:{proxy_port}"
                opts.add_argument(f"--proxy-server={proxy_url}")
                if proxy_type.startswith("socks"):
                    opts.add_argument("--proxy-bypass-list=<-loopback>")
            if proxy_type.startswith("socks"):
                opts.add_argument("--proxy-bypass-list=<-loopback>")

        return opts

    def _create_proxy_extension(self, scheme, host, port, user, password) -> str:
        import tempfile

        chrome_scheme = "http"
        s = (scheme or "http").lower()
        if s == "https":
            chrome_scheme = "http"
        elif "socks5" in s:
            chrome_scheme = "socks5"
        elif "socks4" in s:
            chrome_scheme = "socks4"

        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "incognito": "spanning",
            "permissions": [
                "proxy",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"],
                "persistent": true
            },
            "minimum_chrome_version":"22.0.0"
        }
        """
        background_js = """
        var config = {
                mode: "fixed_servers",
                rules: {
                  singleProxy: {
                    scheme: "%s",
                    host: "%s",
                    port: parseInt(%s)
                  },
                  bypassList: ["localhost", "127.0.0.1"]
                }
              };
        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }
        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """ % (chrome_scheme, host, port, user, password)

        ext_dir = tempfile.mkdtemp(prefix="proxy_ext_")
        with open(os.path.join(ext_dir, "manifest.json"), "w") as f:
            f.write(manifest_json)
        with open(os.path.join(ext_dir, "background.js"), "w") as f:
            f.write(background_js)
        return ext_dir

    def _create_driver(self) -> webdriver.Chrome:
        opts = self._build_options()
        # Selenium 4.6+ Selenium Manager often works without WDM; WDM can return a wrong file on macOS bundles.
        try:
            driver = webdriver.Chrome(options=opts)
            time.sleep(1)
            return driver
        except (WebDriverException, OSError):
            service = _create_chrome_service()
            if service is not None:
                driver = webdriver.Chrome(service=service, options=opts)
                # Small delay to let extensions/proxy initialize
                time.sleep(1)
                return driver
            raise

    def _scroll(self):
        """Scroll the page from top to bottom with random pauses."""
        scroll_speed = self.settings.get("scroll_speed", "medium")
        speed_map = {"slow": (200, 400), "medium": (100, 250), "fast": (50, 150)}
        lo, hi = speed_map.get(scroll_speed, (100, 250))

        try:
            total_height = self.driver.execute_script(
                "return document.body.scrollHeight"
            )
        except Exception:
            total_height = 3000

        current = 0
        step = random.randint(lo, hi)
        while current < total_height and not self._stop_event.is_set():
            self._paused.wait()
            try:
                self.driver.execute_script(f"window.scrollBy(0, {step});")
                current += step
            except Exception:
                break
            pause = random.uniform(0.3, 1.2)
            time.sleep(pause)

            # Random mouse movement
            if self.settings.get("random_mouse") == "1":
                self._random_mouse_move()

        # Scroll back to top
        if not self._stop_event.is_set():
            try:
                self.driver.execute_script("window.scrollTo(0, 0);")
            except Exception:
                pass

    def _random_mouse_move(self):
        try:
            actions = ActionChains(self.driver)
            x = random.randint(100, 900)
            y = random.randint(100, 600)
            actions.move_by_offset(x, y)
            actions.perform()
        except Exception:
            pass

    def _click_random_internal_link(self):
        try:
            links = self.driver.find_elements(By.TAG_NAME, "a")
            current_domain = self.url.split("/")[2]
            internal = [
                l for l in links
                if l.get_attribute("href")
                and current_domain in (l.get_attribute("href") or "")
                and l.is_displayed()
            ]
            if internal:
                link = random.choice(internal[:10])
                link.click()
                time.sleep(random.uniform(2, 4))
                self.driver.back()
        except Exception:
            pass

    def run(self):
        proxy_str = self.proxy.get("proxy") if self.proxy else "none"
        self.session_id = db.add_session(self.url, proxy_str or "none")
        self.status = "running"
        
        country_info = ""
        verified_ip = None
        verified_country = None
        if self.proxy:
            self.log(f"[*] Verifying proxy: {proxy_str}...")
            success, ip, country = check_proxy(self.proxy["proxy"], self.proxy.get("proxy_type", "http"))
            if success:
                verified_ip = ip
                verified_country = country
                country_info = f" ({country})"
                self.log(f"[+] Proxy Verified: {ip}{country_info}")
            else:
                self.log(f"[!] Proxy Verification Failed: {ip}. Traffic might leak!")
                # Optional: self.stop(); return if you want to be super safe
            
        self.log(f"[+] Opening: {self.url}  proxy={proxy_str}{country_info}")

        try:
            self.driver = self._create_driver()

            self.driver.set_page_load_timeout(60)
            if getattr(self, "_needs_auth_proxy", False):
                time.sleep(2)

            if self.proxy and verified_ip:
                self.log("[*] Checking browser IP/country…")
                try:
                    self.driver.get("http://ip-api.com/json/?fields=status,query,country")
                    body_text = self.driver.find_element(By.TAG_NAME, "body").text.strip()
                    if body_text.startswith("{"):
                        data = json.loads(body_text)
                    else:
                        data = json.loads(body_text.splitlines()[-1])
                    detected_ip = (data.get("query") or "").strip()
                    detected_country = (data.get("country") or "Unknown").strip()
                    self.log(f"[*] Browser IP: {detected_ip} ({detected_country})")
                    if self.settings.get("require_proxy") == "1" and detected_ip and detected_ip != verified_ip.strip():
                        raise WebDriverException(f"Proxy not applied (expected {verified_ip}, got {detected_ip})")
                except Exception as e:
                    self.log(f"[!] Browser proxy check failed: {e}")
                    if self.settings.get("require_proxy") == "1":
                        raise

            self.log(f"[*] Navigating to {self.url}…")
            self.driver.get(self.url)
            
            # Wait for content to be visible (Fixes Blank Page)
            try:
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                
                # Wait for ANY element to appear to confirm the page is rendering
                # We wait up to 30 seconds for slow proxies
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Extra check: Is the page actually visible?
                self.log("[✓] Connection established. Page is rendering.")
                time.sleep(5) # Give it 5 seconds to load the actual content
            except:
                self.log("[!] Page loading slowly or proxy is slow. Continuing...")

            if self._stop_event.is_set():
                raise InterruptedError("Stopped before scroll")

            load_wait = random.uniform(2, 4)
            time.sleep(load_wait)

            self._scroll()

            if (
                self.settings.get("click_links") == "1"
                and not self._stop_event.is_set()
            ):
                self._click_random_internal_link()

            self.status = "completed"
            self.log(f"[✓] Done: {self.url}")
            db.finish_session(self.session_id, "completed")
            if self.proxy:
                db.record_proxy_result(self.proxy["proxy"], True, verified_country)

        except InterruptedError:
            self.status = "stopped"
            self.log(f"[■] Stopped: {self.url}")
            if self.session_id:
                db.finish_session(self.session_id, "stopped")
        except WebDriverException as e:
            self.status = "error"
            msg = str(e).splitlines()[0]
            self.log(f"[✗] Error: {self.url} — {msg}")
            if self.session_id:
                db.finish_session(self.session_id, "error")
            if self.proxy:
                db.record_proxy_result(self.proxy["proxy"], False)
        except Exception as e:
            self.status = "error"
            self.log(f"[✗] Exception: {self.url} — {e}")
            if self.session_id:
                db.finish_session(self.session_id, "error")
        finally:
            try:
                if self.driver:
                    self.driver.quit()
            except Exception:
                pass
            if hasattr(self, "_proxy_ext_dir") and os.path.isdir(self._proxy_ext_dir):
                try:
                    import shutil
                    shutil.rmtree(self._proxy_ext_dir, ignore_errors=True)
                except Exception:
                    pass
            if self.done_cb:
                self.done_cb(self)


# ──────────────────────────────────────────────
#  Automation Engine
# ──────────────────────────────────────────────

class AutomationEngine:
    """
    Manages a pool of BrowserSession threads.
    Respects max_browsers concurrency limit.
    """

    def __init__(
        self,
        log_cb: Optional[Callable[[str], None]] = None,
        state_changed_cb: Optional[Callable[[], None]] = None,
    ):
        self.log_cb = log_cb
        self.state_changed_cb = state_changed_cb
        self._lock = threading.Lock()
        self._active: list[BrowserSession] = []
        self._queue: list[tuple[str, Optional[dict]]] = []
        self._running = False
        self._paused = False
        self._dispatcher: Optional[threading.Thread] = None

    def _notify_state(self):
        if self.state_changed_cb:
            self.state_changed_cb()

    def log(self, msg: str):
        if self.log_cb:
            self.log_cb(msg)

    def start(self, urls: list[str], proxies: list[dict], settings: dict):
        if self._running:
            return
        self._running = True
        self._paused = False
        use_proxy = settings.get("use_proxy") == "1"
        rotate_proxy = settings.get("rotate_proxy") == "1"

        if proxies and not use_proxy:
            use_proxy = True
            self.log("[Engine] Proxies detected — enabling proxy usage for this run.")

        if use_proxy and proxies:
            proxy_cycle = itertools.cycle(proxies)
            fixed_proxy = proxies[0]
        else:
            proxy_cycle = None
            fixed_proxy = None

        self._queue = []
        for url in urls:
            proxy = None
            if use_proxy and proxies:
                proxy = next(proxy_cycle) if rotate_proxy else fixed_proxy
            self._queue.append((url, proxy))

        self._settings = settings
        self._dispatcher = threading.Thread(target=self._dispatch_loop, daemon=True)
        self._dispatcher.start()
        self.log(f"[Engine] Automation started — {len(urls)} URL(s) queued.")
        self._notify_state()

    def _dispatch_loop(self):
        delay_min = float(self._settings.get("delay_min", 3))
        delay_max = float(self._settings.get("delay_max", 8))
        max_browsers = int(self._settings.get("max_browsers", 5))

        while self._queue and self._running:
            if self._paused:
                time.sleep(0.5)
                continue

            with self._lock:
                active_count = len([s for s in self._active if s.is_alive()])

            if active_count >= max_browsers:
                time.sleep(0.5)
                continue

            with self._lock:
                if not self._queue:
                    break
                url, proxy = self._queue.pop(0)

            session = BrowserSession(
                url=url,
                settings=self._settings,
                proxy=proxy,
                log_cb=self.log_cb,
                done_cb=self._session_done,
            )
            with self._lock:
                self._active.append(session)
            session.start()

            delay = random.uniform(delay_min, delay_max)
            time.sleep(delay)

        self.log("[Engine] All URLs dispatched. Waiting for sessions to finish…")

    def _session_done(self, session: BrowserSession):
        with self._lock:
            if session in self._active:
                self._active.remove(session)
        if not self._active and not self._queue:
            self._running = False
            self.log("[Engine] All sessions completed.")
            self._notify_state()

    def stop(self):
        self._running = False
        self._queue.clear()
        with self._lock:
            for s in list(self._active):
                s.stop()
        self.log("[Engine] Automation stopped.")
        self._notify_state()

    def pause(self):
        self._paused = True
        with self._lock:
            for s in self._active:
                s.pause()
        self.log("[Engine] Automation paused.")
        self._notify_state()

    def resume(self):
        self._paused = False
        with self._lock:
            for s in self._active:
                s.resume()
        self.log("[Engine] Automation resumed.")
        self._notify_state()

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def is_paused(self) -> bool:
        return self._paused

    def active_count(self) -> int:
        with self._lock:
            return len([s for s in self._active if s.is_alive()])

    def queue_count(self) -> int:
        return len(self._queue)
