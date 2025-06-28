import threading
import time

import flet as ft
import psutil
import win32gui
import win32process


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


def main(page: ft.Page):
    page.title = "App Sticky Memo"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.window.width = 400
    page.window.height = 300

    # 現在のアプリ名を表示するテキスト
    current_app_text = ft.Text(
        value="アプリを監視中...",
        size=16,
        text_align=ft.TextAlign.CENTER,
        weight=ft.FontWeight.W_500,
    )

    # アプリ名表示用のコンテナ
    app_display_container = ft.Container(
        content=current_app_text,
        padding=ft.padding.all(20),
        alignment=ft.alignment.center,
        bgcolor=ft.Colors.BLUE_GREY_50,
        border_radius=ft.border_radius.all(10),
        margin=ft.margin.all(10),
        border=ft.border.all(1, ft.Colors.BLUE_GREY_200),
    )

    def update_foreground_app():
        """フォアグラウンドアプリを定期的に監視"""
        last_app = None
        while True:
            try:
                app_name = get_foreground_app()
                if app_name and app_name != last_app:
                    current_app_text.value = f"現在のアプリ: {app_name}"
                    last_app = app_name
                    page.update()
                elif app_name is None and last_app is not None:
                    # app-sticky-memo自体にフォーカスした場合
                    current_app_text.value = "App Sticky Memo にフォーカス中"
                    last_app = None
                    page.update()
                time.sleep(0.5)  # 0.5秒間隔で監視
            except Exception as e:
                print(f"監視エラー: {e}")
                time.sleep(1)

    # バックグラウンドで監視を開始
    monitor_thread = threading.Thread(target=update_foreground_app, daemon=True)
    monitor_thread.start()

    page.add(
        ft.Column(
            [
                ft.Text(
                    "App Sticky Memo",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                app_display_container,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )


ft.app(main)
