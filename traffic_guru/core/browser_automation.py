"""
Browser automation engine for Traffic Guru.

Each BrowserSession opens a Chrome instance (headless optional),
navigates to a URL, and performs auto-scroll with random delays.
"""

import itertools
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
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option("useAutomationExtension", False)

        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/123.0 Safari/537.36",
        ]
        opts.add_argument(f"--user-agent={random.choice(user_agents)}")

        if self.settings.get("headless") == "1":
            opts.add_argument("--headless=new")
            opts.add_argument("--window-size=1920,1080")

        # Proxy
        if self.proxy:
            raw = self.proxy.get("proxy", "")
            ptype = self.proxy.get("proxy_type", "http").lower()
            if "://" not in raw:
                raw = f"{ptype}://{raw}"
            opts.add_argument(f"--proxy-server={raw}")

        return opts

    def _create_driver(self) -> webdriver.Chrome:
        opts = self._build_options()
        # Selenium 4.6+ Selenium Manager often works without WDM; WDM can return a wrong file on macOS bundles.
        try:
            return webdriver.Chrome(options=opts)
        except (WebDriverException, OSError):
            service = _create_chrome_service()
            if service is not None:
                return webdriver.Chrome(service=service, options=opts)
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
        self.log(f"[+] Opening: {self.url}  proxy={proxy_str}")

        try:
            self.driver = self._create_driver()
            self.driver.set_page_load_timeout(30)
            self.driver.get(self.url)

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
                db.record_proxy_result(self.proxy["proxy"], True)

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
        proxy_cycle = itertools.cycle(proxies) if proxies else None

        use_proxy = settings.get("use_proxy") == "1"
        rotate_proxy = settings.get("rotate_proxy") == "1"

        self._queue = []
        for url in urls:
            proxy = None
            if use_proxy and proxy_cycle:
                proxy = next(proxy_cycle) if rotate_proxy else next(proxy_cycle)
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


