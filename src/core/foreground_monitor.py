import logging
import threading
import time
from pathlib import Path

import psutil
import win32gui
import win32process

logger = logging.getLogger("app_sticky_memo")


def get_foreground_app():
    """Get the executable file name of the foreground app"""
    try:
        # Get handle of the foreground window
        hwnd = win32gui.GetForegroundWindow()
        if hwnd == 0:
            return None

        # Get process ID
        _, pid = win32process.GetWindowThreadProcessId(hwnd)

        # Get process info
        process = psutil.Process(pid)
        exe_name = process.name()

        # Exclude app-sticky-memo itself
        if exe_name in ["python.exe", "pythonw.exe", "app.py", "flet.exe"]:
            return None

        return exe_name
    except Exception:
        return None


def ensure_data_dir(data_dir):
    """Create data directory"""
    try:
        Path(data_dir).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def get_memo_file_path(app_name, data_dir):
    """Generate memo file path from app name"""
    safe_app_name = "".join(
        c for c in app_name if c.isalnum() or c in (" ", "-", "_")
    ).rstrip()
    safe_app_name = safe_app_name.replace(" ", "_")
    return Path(data_dir) / f"{safe_app_name}.md"


class ForegroundMonitor:
    """Foreground application monitor class"""

    def __init__(
        self,
        settings,
        shutdown_event,
        on_app_change_callback=None,
        on_ui_update_callback=None,
    ):
        """
        Initialize ForegroundMonitor

        Args:
            settings: Application settings
            shutdown_event: Shutdown event
            on_app_change_callback: Callback function on app change
            on_ui_update_callback: Callback function for UI update
        """
        self.settings = settings
        self.shutdown_event = shutdown_event
        self.on_app_change_callback = on_app_change_callback
        self.on_ui_update_callback = on_ui_update_callback
        self.monitor_thread = None
        self.last_app = None
        self.previous_non_sticky_app = None  # Remember previous non-Sticky Memo app
        logger.debug("ForegroundMonitor initialized")

    def start_monitoring(self):
        """Start monitoring"""
        if not self.shutdown_event.is_set():
            try:
                self.monitor_thread = threading.Thread(
                    target=self._monitor_loop, daemon=True
                )
                self.monitor_thread.start()
                logger.info("Started foreground app monitoring")
            except RuntimeError as e:
                logger.error(f"Error starting monitor thread: {e}")
        else:
            logger.info("Shutdown in progress, not starting monitor thread")

    def _monitor_loop(self):
        """Periodically monitor the foreground app"""
        while not self.shutdown_event.is_set():
            try:
                if self.shutdown_event.is_set():
                    break

                app_name = get_foreground_app()
                if (
                    app_name
                    and app_name != self.last_app
                    and not self.shutdown_event.is_set()
                ):
                    # Handle actual app change
                    self._handle_app_change(app_name)
                    self.previous_non_sticky_app = (
                        app_name  # Remember previous non-Sticky Memo app
                    )
                    self.last_app = app_name

                elif (
                    app_name is None
                    and self.last_app is not None
                    and not self.shutdown_event.is_set()
                ):
                    # When focus is on app-sticky-memo itself
                    # Do nothing (keep showing previous app's memo)
                    self.last_app = None

                if not self.shutdown_event.is_set():
                    time.sleep(0.5)  # Monitor every 0.5 seconds
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                if not self.shutdown_event.is_set():
                    time.sleep(1)
                else:
                    break
        logger.info("Foreground app monitoring stopped")

    def _handle_app_change(self, app_name):
        """Handle app change event"""
        logger.debug(f"App changed: {app_name}")

        # Update UI via callback
        if self.on_app_change_callback:
            self.on_app_change_callback(app_name)

        # Safely update UI
        if self.on_ui_update_callback:
            try:
                if not self.shutdown_event.is_set():
                    self.on_ui_update_callback()
            except Exception as update_ex:
                logger.error(f"UI update error: {update_ex}")
                if self.shutdown_event.is_set():
                    return
