import json
import threading
import time
from pathlib import Path

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


def load_settings():
    """設定ファイルを読み込み"""
    settings_file = Path("settings.json")
    if settings_file.exists():
        try:
            with open(settings_file, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"data_save_dir": str(Path.home() / "Documents" / "StickyMemos")}


def save_settings(settings):
    """設定ファイルを保存"""
    try:
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"設定保存エラー: {e}")


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


def main(page: ft.Page):
    print("App Sticky Memo を開始します")
    page.title = "App Sticky Memo"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.window.width = 400
    page.window.height = 300

    # 設定を読み込み
    settings = load_settings()
    print(f"設定を読み込みました: {settings}")

    # 現在のアプリ名を表示するテキスト
    current_app_text = ft.Text(
        value="アプリを監視中...",
        size=16,
        text_align=ft.TextAlign.CENTER,
        weight=ft.FontWeight.W_500,
    )

    # ファイルピッカーを事前に初期化
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    print("ファイルピッカーを初期化しました")

    # 設定パネルの状態管理
    settings_panel_visible = False

    # メインコンテンツの参照を保持
    main_content = None

    # 設定パネルを表示/非表示する関数
    def toggle_settings_panel():
        nonlocal settings_panel_visible
        settings_panel_visible = not settings_panel_visible
        print(f"設定パネルの表示状態: {settings_panel_visible}")
        settings_panel.visible = settings_panel_visible
        page.update()

    # 設定パネルのコンポーネント
    data_dir_field = ft.TextField(
        label="Data Save Directory",
        value=settings["data_save_dir"],
        width=300,
        multiline=False,
    )

    def pick_directory(e):
        print("フォルダ選択ボタンがクリックされました")

        def on_result(result: ft.FilePickerResultEvent):
            print(f"フォルダ選択結果: {result.path}")
            if result.path:
                data_dir_field.value = result.path
                page.update()

        file_picker.on_result = on_result
        file_picker.get_directory_path("フォルダを選択してください")

    def save_settings_action(e):
        print("設定保存ボタンがクリックされました")
        new_dir = data_dir_field.value.strip()
        if new_dir and new_dir != "":
            if ensure_data_dir(new_dir):
                settings["data_save_dir"] = new_dir
                save_settings(settings)
                # SnackBarの表示方法を修正
                page.snack_bar = ft.SnackBar(content=ft.Text("設定を保存しました"))
                page.snack_bar.open = True
                page.update()
                print(f"設定を保存しました: {new_dir}")
                toggle_settings_panel()  # 設定パネルを閉じる
            else:
                page.snack_bar = ft.SnackBar(content=ft.Text("無効なディレクトリです"))
                page.snack_bar.open = True
                page.update()
                print(f"無効なディレクトリです: {new_dir}")
        else:
            snack_text = "ディレクトリを入力してください"
            page.snack_bar = ft.SnackBar(content=ft.Text(snack_text))
            page.snack_bar.open = True
            page.update()
            print("ディレクトリが入力されていません")

    def cancel_settings_action(e):
        print("設定キャンセルボタンがクリックされました")
        # 元の値に戻す
        data_dir_field.value = settings["data_save_dir"]
        page.update()  # フィールドの値を更新
        toggle_settings_panel()  # 設定パネルを閉じる

    # 設定パネル
    settings_panel = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("設定", size=20, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            tooltip="閉じる",
                            on_click=cancel_settings_action,
                        ),
                    ]
                ),
                ft.Container(height=10),
                ft.Text("データ保存ディレクトリ:", size=14),
                ft.Container(height=5),
                ft.Row(
                    [
                        data_dir_field,
                        ft.ElevatedButton(
                            "選択",
                            icon=ft.Icons.FOLDER_OPEN,
                            on_click=pick_directory,
                        ),
                    ]
                ),
                ft.Container(height=20),
                ft.Row(
                    [
                        ft.Container(expand=True),
                        ft.TextButton("キャンセル", on_click=cancel_settings_action),
                        ft.Container(width=10),
                        ft.ElevatedButton("保存", on_click=save_settings_action),
                    ]
                ),
            ],
            spacing=0,
        ),
        padding=ft.padding.all(20),
        bgcolor=ft.Colors.WHITE,
        border_radius=ft.border_radius.all(10),
        border=ft.border.all(2, ft.Colors.BLUE_GREY_200),
        margin=ft.margin.all(10),
        visible=False,  # 初期状態は非表示
    )

    # 設定ボタン
    def on_settings_click(e):
        print("設定ボタンがクリックされました")
        toggle_settings_panel()

    settings_button = ft.IconButton(
        icon=ft.Icons.SETTINGS,
        tooltip="設定",
        on_click=on_settings_click,
    )
    print("設定ボタンを作成しました")

    # ヘッダー部分
    header = ft.Row(
        [
            ft.Container(expand=True),  # 左側のスペース
            ft.Text(
                "App Sticky Memo",
                size=24,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Container(
                content=settings_button,
                width=48,  # ボタンの幅を固定
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
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

                    # メモファイルを作成/更新
                    data_dir = settings["data_save_dir"]
                    if ensure_data_dir(data_dir):
                        memo_file = get_memo_file_path(app_name, data_dir)
                        if not memo_file.exists():
                            try:
                                with open(memo_file, "w", encoding="utf-8") as f:
                                    f.write(f"# {app_name} のメモ\n\n")
                                    f.write("ここにメモを記述してください。\n\n")
                                    f.write(
                                        f"作成日時: "
                                        f"{time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                                    )
                            except Exception as e:
                                print(f"メモファイル作成エラー: {e}")

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
    print("フォアグラウンドアプリ監視を開始しました")

    print("UIを構築します")
    main_content = ft.Column(
        [
            header,
            app_display_container,
            settings_panel,  # 設定パネルを追加
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    page.add(main_content)
    print("UIの構築が完了しました")


print("App Sticky Memo を起動します")
ft.app(main)
