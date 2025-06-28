import json
import logging
import time
from pathlib import Path

import flet as ft
import psutil
import win32gui
import win32process

# カスタムロガーの設定
logger = logging.getLogger("app_sticky_memo")
logger.setLevel(logging.DEBUG)

# コンソールハンドラーの設定
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# フォーマッターの設定
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
)
console_handler.setFormatter(formatter)

# ハンドラーをロガーに追加
logger.addHandler(console_handler)


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
    default_settings = {
        "data_save_dir": str(Path.home() / "Documents" / "StickyMemos"),
        "window": {
            "width": 400,
            "height": 300,
            "left": None,
            "top": None,
        },
    }

    if settings_file.exists():
        try:
            with open(settings_file, encoding="utf-8") as f:
                loaded_settings = json.load(f)
                # デフォルト設定をベースに、読み込んだ設定をマージ
                for key, value in loaded_settings.items():
                    if key in default_settings:
                        if isinstance(value, dict) and isinstance(
                            default_settings[key], dict
                        ):
                            default_settings[key].update(value)
                        else:
                            default_settings[key] = value
                return default_settings
        except Exception:
            pass
    return default_settings


def save_settings(settings):
    """設定ファイルを保存"""
    try:
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        logger.debug("設定ファイルを保存しました")
    except Exception as e:
        logger.error(f"設定保存エラー: {e}")


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
    logger.info("App Sticky Memo を開始します")
    page.title = "App Sticky Memo"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # アプリケーション終了フラグ（グローバル変数として参照を保持）
    import threading

    _shutdown_event = threading.Event()

    def is_shutting_down():
        return _shutdown_event.is_set()

    def set_shutdown():
        _shutdown_event.set()
        logger.info("アプリケーション終了フラグを設定しました")

    # 設定を読み込み
    settings = load_settings()
    logger.debug(f"設定を読み込みました: {settings}")

    # ウィンドウの位置とサイズを復元
    window_settings = settings["window"]
    logger.debug(f"ウィンドウ設定を復元します: {window_settings}")

    page.window.width = window_settings["width"]
    page.window.height = window_settings["height"]
    width, height = window_settings["width"], window_settings["height"]
    logger.info(f"ウィンドウサイズを設定しました: {width} x {height}")

    if window_settings["left"] is not None and window_settings["top"] is not None:
        page.window.left = window_settings["left"]
        page.window.top = window_settings["top"]
        left, top = window_settings["left"], window_settings["top"]
        logger.info(f"ウィンドウ位置を設定しました: ({left}, {top})")
    else:
        logger.info("ウィンドウ位置の設定がありません（初回起動）")

    # ウィンドウが閉じられる時の処理
    def on_window_event(e):
        logger.debug(f"ウィンドウイベントが発生しました: {e.data}")

        if e.data == "close":
            logger.info("ウィンドウが閉じられます - 設定を保存します")
            set_shutdown()
            save_window_settings()
        elif e.data in ["moved", "resized"] and not is_shutting_down():
            logger.debug("ウィンドウの位置またはサイズが変更されました")
            # 直接保存（遅延なし）
            save_window_settings()

    def save_window_settings():
        """ウィンドウ設定を保存する共通関数"""
        if is_shutting_down():
            logger.debug("アプリ終了中のため、ウィンドウ設定保存をスキップします")
            return

        try:
            # 現在のウィンドウの位置とサイズを取得
            current_width = page.window.width
            current_height = page.window.height
            current_left = page.window.left
            current_top = page.window.top

            logger.debug("現在のウィンドウ情報:")
            logger.debug(f"  サイズ: {current_width} x {current_height}")
            logger.debug(f"  位置: ({current_left}, {current_top})")

            # 設定を更新
            settings["window"]["width"] = current_width
            settings["window"]["height"] = current_height
            settings["window"]["left"] = current_left
            settings["window"]["top"] = current_top

            # 設定を保存
            save_settings(settings)
            logger.debug(f"ウィンドウ設定を保存しました: {settings['window']}")
        except Exception as ex:
            logger.error(f"ウィンドウ設定保存でエラー: {ex}")
            # エラーが発生した場合は終了フラグをチェックして、必要に応じて処理を停止
            if is_shutting_down():
                return

    # ウィンドウサイズが変更された時の処理
    def on_resize(e):
        if is_shutting_down():
            return

        width, height = page.window.width, page.window.height
        logger.debug(f"リサイズイベント: {width} x {height}")

        # リサイズ後に直接設定を保存（遅延なし）
        save_window_settings()

    page.window.on_event = on_window_event
    page.on_resize = on_resize

    # ページが切断される時の処理（バックアップとして）
    def on_disconnect(e):
        logger.info("ページが切断されました - 設定を保存します")
        set_shutdown()
        save_window_settings()

    page.on_disconnect = on_disconnect

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
    logger.debug("ファイルピッカーを初期化しました")

    # 設定パネルの状態管理
    settings_panel_visible = False

    # メインコンテンツの参照を保持
    main_content = None

    # 設定パネルを表示/非表示する関数
    def toggle_settings_panel():
        if is_shutting_down():
            return
        nonlocal settings_panel_visible
        settings_panel_visible = not settings_panel_visible
        logger.debug(f"設定パネルの表示状態: {settings_panel_visible}")
        settings_panel.visible = settings_panel_visible
        try:
            if not is_shutting_down():
                page.update()
        except Exception as ex:
            logger.error(f"設定パネル更新エラー: {ex}")

    # 設定パネルのコンポーネント
    data_dir_field = ft.TextField(
        label="Data Save Directory",
        value=settings["data_save_dir"],
        width=300,
        multiline=False,
    )

    def pick_directory(e):
        logger.debug("フォルダ選択ボタンがクリックされました")

        def on_result(result: ft.FilePickerResultEvent):
            logger.debug(f"フォルダ選択結果: {result.path}")
            if result.path and not is_shutting_down():
                data_dir_field.value = result.path
                try:
                    if not is_shutting_down():
                        page.update()
                except Exception as ex:
                    logger.error(f"フォルダ選択更新エラー: {ex}")

        file_picker.on_result = on_result
        file_picker.get_directory_path("フォルダを選択してください")

    def save_settings_action(e):
        if is_shutting_down():
            return
        logger.debug("設定保存ボタンがクリックされました")
        new_dir = data_dir_field.value.strip()
        if new_dir and new_dir != "":
            if ensure_data_dir(new_dir):
                settings["data_save_dir"] = new_dir
                save_settings(settings)
                # SnackBarの表示方法を修正
                page.snack_bar = ft.SnackBar(content=ft.Text("設定を保存しました"))
                page.snack_bar.open = True
                try:
                    if not is_shutting_down():
                        page.update()
                except Exception as ex:
                    logger.error(f"設定保存更新エラー: {ex}")
                logger.info(f"設定を保存しました: {new_dir}")
                toggle_settings_panel()  # 設定パネルを閉じる
            else:
                page.snack_bar = ft.SnackBar(content=ft.Text("無効なディレクトリです"))
                page.snack_bar.open = True
                try:
                    if not is_shutting_down():
                        page.update()
                except Exception as ex:
                    logger.error(f"エラー表示更新エラー: {ex}")
                logger.error(f"無効なディレクトリです: {new_dir}")
        else:
            snack_text = "ディレクトリを入力してください"
            page.snack_bar = ft.SnackBar(content=ft.Text(snack_text))
            page.snack_bar.open = True
            try:
                if not is_shutting_down():
                    page.update()
            except Exception as ex:
                logger.error(f"エラー表示更新エラー: {ex}")
            logger.error("ディレクトリが入力されていません")

    def cancel_settings_action(e):
        if is_shutting_down():
            return
        logger.debug("設定キャンセルボタンがクリックされました")
        # 元の値に戻す
        data_dir_field.value = settings["data_save_dir"]
        try:
            if not is_shutting_down():
                page.update()
        except Exception as ex:
            logger.error(f"キャンセル更新エラー: {ex}")
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
        logger.debug("設定ボタンがクリックされました")
        toggle_settings_panel()

    settings_button = ft.IconButton(
        icon=ft.Icons.SETTINGS,
        tooltip="設定",
        on_click=on_settings_click,
    )
    logger.debug("設定ボタンを作成しました")

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
        while not is_shutting_down():
            try:
                if is_shutting_down():
                    break

                app_name = get_foreground_app()
                if app_name and app_name != last_app and not is_shutting_down():
                    current_app_text.value = f"現在のアプリ: {app_name}"
                    last_app = app_name

                    # UI更新を安全に実行
                    try:
                        if not is_shutting_down():
                            page.update()
                    except Exception as update_ex:
                        logger.error(f"UI更新エラー: {update_ex}")
                        if is_shutting_down():
                            break

                    # メモファイルを作成/更新
                    data_dir = settings["data_save_dir"]
                    if ensure_data_dir(data_dir) and not is_shutting_down():
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

                elif (
                    app_name is None and last_app is not None and not is_shutting_down()
                ):
                    # app-sticky-memo自体にフォーカスした場合
                    current_app_text.value = "App Sticky Memo にフォーカス中"
                    last_app = None

                    # UI更新を安全に実行
                    try:
                        if not is_shutting_down():
                            page.update()
                    except Exception as update_ex:
                        logger.error(f"UI更新エラー: {update_ex}")
                        if is_shutting_down():
                            break

                if not is_shutting_down():
                    time.sleep(0.5)  # 0.5秒間隔で監視
            except Exception as e:
                logger.error(f"監視エラー: {e}")
                if not is_shutting_down():
                    time.sleep(1)
                else:
                    break
        logger.info("フォアグラウンドアプリ監視を終了しました")

    # バックグラウンドで監視を開始
    if not is_shutting_down():
        try:
            monitor_thread = threading.Thread(target=update_foreground_app, daemon=True)
            monitor_thread.start()
            logger.info("フォアグラウンドアプリ監視を開始しました")
        except RuntimeError as e:
            logger.error(f"監視スレッドの開始でエラー: {e}")
    else:
        logger.info("アプリ終了中のため、監視スレッドを開始しません")

    logger.debug("UIを構築します")
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
    logger.info("UIの構築が完了しました")

    # ページロード後に直接ウィンドウ設定を適用
    try:
        logger.debug("ウィンドウ設定を再適用します")
        page.window.width = window_settings["width"]
        page.window.height = window_settings["height"]

        if window_settings["left"] is not None and window_settings["top"] is not None:
            page.window.left = window_settings["left"]
            page.window.top = window_settings["top"]

        try:
            if not is_shutting_down():
                page.update()
        except Exception as update_ex:
            logger.error(f"ウィンドウ設定更新エラー: {update_ex}")
        logger.info("ウィンドウ設定の再適用が完了しました")
    except Exception as ex:
        logger.error(f"ウィンドウ設定の再適用でエラー: {ex}")


logger.info("App Sticky Memo を起動します")
ft.app(main)
