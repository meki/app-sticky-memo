import logging
import threading
import time
from pathlib import Path

import psutil
import win32gui
import win32process

logger = logging.getLogger("app_sticky_memo")


def get_foreground_app():
    """フォアグラウンドアプリの実行ファイル名を取得"""
    try:
        # フォアグラウンドウィンドウのハンドルを取得
        hwnd = win32gui.GetForegroundWindow()
        if hwnd == 0:
            return None

        # プロセスIDを取得
        _, pid = win32process.GetWindowThreadProcessId(hwnd)

        # プロセス情報を取得
        process = psutil.Process(pid)
        exe_name = process.name()

        # app-sticky-memo自体の場合は除外
        if exe_name in ["python.exe", "pythonw.exe", "app.py", "flet.exe"]:
            return None

        return exe_name
    except Exception:
        return None


def ensure_data_dir(data_dir):
    """データディレクトリを作成"""
    try:
        Path(data_dir).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def get_memo_file_path(app_name, data_dir):
    """アプリ名からメモファイルのパスを生成"""
    safe_app_name = "".join(
        c for c in app_name if c.isalnum() or c in (" ", "-", "_")
    ).rstrip()
    safe_app_name = safe_app_name.replace(" ", "_")
    return Path(data_dir) / f"{safe_app_name}.md"


class ForegroundMonitor:
    """フォアグラウンドアプリケーション監視クラス"""

    def __init__(
        self,
        settings,
        shutdown_event,
        on_app_change_callback=None,
        on_ui_update_callback=None,
    ):
        """
        ForegroundMonitorを初期化

        Args:
            settings: アプリケーション設定
            shutdown_event: 終了イベント
            on_app_change_callback: アプリ変更時のコールバック関数
            on_ui_update_callback: UI更新時のコールバック関数
        """
        self.settings = settings
        self.shutdown_event = shutdown_event
        self.on_app_change_callback = on_app_change_callback
        self.on_ui_update_callback = on_ui_update_callback
        self.monitor_thread = None
        self.last_app = None
        logger.debug("ForegroundMonitorを初期化しました")

    def start_monitoring(self):
        """監視を開始"""
        if not self.shutdown_event.is_set():
            try:
                self.monitor_thread = threading.Thread(
                    target=self._monitor_loop, daemon=True
                )
                self.monitor_thread.start()
                logger.info("フォアグラウンドアプリ監視を開始しました")
            except RuntimeError as e:
                logger.error(f"監視スレッドの開始でエラー: {e}")
        else:
            logger.info("アプリ終了中のため、監視スレッドを開始しません")

    def _monitor_loop(self):
        """フォアグラウンドアプリを定期的に監視"""
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
                    # アプリ変更時の処理
                    self._handle_app_change(app_name)
                    self.last_app = app_name

                elif (
                    app_name is None
                    and self.last_app is not None
                    and not self.shutdown_event.is_set()
                ):
                    # app-sticky-memo自体にフォーカスした場合
                    self._handle_app_focus_self()
                    self.last_app = None

                if not self.shutdown_event.is_set():
                    time.sleep(0.5)  # 0.5秒間隔で監視
            except Exception as e:
                logger.error(f"監視エラー: {e}")
                if not self.shutdown_event.is_set():
                    time.sleep(1)
                else:
                    break
        logger.info("フォアグラウンドアプリ監視を終了しました")

    def _handle_app_change(self, app_name):
        """アプリ変更時の処理"""
        logger.debug(f"アプリが変更されました: {app_name}")

        # コールバック関数でUI更新
        if self.on_app_change_callback:
            self.on_app_change_callback(app_name)

        # UI更新を安全に実行
        if self.on_ui_update_callback:
            try:
                if not self.shutdown_event.is_set():
                    self.on_ui_update_callback()
            except Exception as update_ex:
                logger.error(f"UI更新エラー: {update_ex}")
                if self.shutdown_event.is_set():
                    return

        # メモファイルを作成/更新
        self._create_memo_file(app_name)

    def _handle_app_focus_self(self):
        """App Sticky Memo自体にフォーカスした場合の処理"""
        logger.debug("App Sticky Memoにフォーカスしました")

        # コールバック関数でUI更新
        if self.on_app_change_callback:
            self.on_app_change_callback(None)

        # UI更新を安全に実行
        if self.on_ui_update_callback:
            try:
                if not self.shutdown_event.is_set():
                    self.on_ui_update_callback()
            except Exception as update_ex:
                logger.error(f"UI更新エラー: {update_ex}")

    def _create_memo_file(self, app_name):
        """メモファイルを作成"""
        data_dir = self.settings["data_save_dir"]
        if ensure_data_dir(data_dir) and not self.shutdown_event.is_set():
            memo_file = get_memo_file_path(app_name, data_dir)
            if not memo_file.exists():
                try:
                    with open(memo_file, "w", encoding="utf-8") as f:
                        f.write(f"# {app_name} のメモ\n\n")
                        f.write("ここにメモを記述してください。\n\n")
                        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                        f.write(f"作成日時: {timestamp}\n")
                    logger.debug(f"メモファイルを作成しました: {memo_file}")
                except Exception as e:
                    logger.error(f"メモファイル作成エラー: {e}")
