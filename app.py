import logging
import threading
import time

import flet as ft

from src.components.app_display import AppDisplayComponent

# 新しいコンポーネントとコアロジックのインポート
from src.components.header import HeaderComponent
from src.components.memo_editor import MemoEditor
from src.components.settings_panel import SettingsPanel
from src.core.foreground_monitor import ForegroundMonitor
from src.core.memo_manager import MemoManager
from src.core.settings_manager import SettingsManager
from src.locales.i18n import t

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


def main(page: ft.Page):
    logger.info(t("logging.app_start"))
    page.title = t("app.title")
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.padding = ft.padding.all(10)

    # アプリケーション終了フラグ（グローバル変数として参照を保持）
    _shutdown_event = threading.Event()

    def is_shutting_down():
        return _shutdown_event.is_set()

    def set_shutdown():
        _shutdown_event.set()
        logger.info("アプリケーション終了フラグを設定しました")

    # 設定マネージャーを初期化
    settings_manager = SettingsManager()
    settings = settings_manager.get_settings()
    logger.debug(f"設定を読み込みました: {settings}")

    # ウィンドウの位置とサイズを復元
    window_settings = settings_manager.get_window_settings()
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
            # 現在のメモを保存（終了時）
            if is_shutting_down():
                save_current_memo()

            # 現在のウィンドウの位置とサイズを取得
            current_width = page.window.width
            current_height = page.window.height
            current_left = page.window.left
            current_top = page.window.top

            logger.debug("現在のウィンドウ情報:")
            logger.debug(f"  サイズ: {current_width} x {current_height}")
            logger.debug(f"  位置: ({current_left}, {current_top})")

            # 設定を更新
            settings_manager.update_window_settings(
                current_width, current_height, current_left, current_top
            )

            # 設定を保存
            settings_manager.save_settings()
            window_settings_msg = settings_manager.get_window_settings()
            logger.debug(f"ウィンドウ設定を保存しました: {window_settings_msg}")
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

    # UIコンポーネントを初期化
    app_display = AppDisplayComponent()

    # メモマネージャーを初期化
    memo_manager = MemoManager(settings_manager.get_data_save_dir())

    # メモエディターを初期化

    def on_memo_content_change(content):
        """メモ内容変更時のコールバック"""

        # 単純に2秒後に自動保存を実行
        def delayed_save():
            time.sleep(2)  # 2秒待機
            if not is_shutting_down() and memo_editor:
                try:
                    memo_editor.auto_save()
                    # UI更新
                    if not is_shutting_down():
                        page.update()
                except Exception as ex:
                    logger.error(f"自動保存UI更新エラー: {ex}")

        # 既存のタイマーがあれば停止
        if (
            hasattr(on_memo_content_change, "_save_timer")
            and on_memo_content_change._save_timer
        ):
            on_memo_content_change._save_timer.cancel()

        # 新しいタイマーを開始
        on_memo_content_change._save_timer = threading.Timer(2.0, delayed_save)
        on_memo_content_change._save_timer.daemon = True
        on_memo_content_change._save_timer.start()

    memo_editor = MemoEditor(on_content_change=on_memo_content_change)

    # メモ保存用の共通関数
    def save_current_memo():
        """現在のメモを保存"""
        try:
            if memo_editor.has_unsaved_changes():
                memo_editor.save_memo()
                logger.debug("現在のメモを保存しました")
        except Exception as e:
            logger.error(f"メモ保存エラー: {e}")

    # 設定パネルの状態管理
    settings_panel_visible = False

    # 設定パネルを表示/非表示する関数
    def toggle_settings_panel():
        if is_shutting_down():
            return
        nonlocal settings_panel_visible
        settings_panel_visible = not settings_panel_visible
        logger.debug(f"設定パネルの表示状態: {settings_panel_visible}")
        settings_panel.toggle()
        try:
            if not is_shutting_down():
                page.update()
        except Exception as ex:
            logger.error(f"設定パネル更新エラー: {ex}")

    # ファイルピッカーを事前に初期化
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    logger.debug("ファイルピッカーを初期化しました")

    # フォルダ選択ハンドラー
    def pick_directory():
        """フォルダ選択処理"""
        logger.debug("フォルダ選択ボタンがクリックされました")

        def on_result(result: ft.FilePickerResultEvent):
            logger.debug(f"フォルダ選択結果: {result.path}")
            if result.path and not is_shutting_down():
                settings_panel.update_data_dir(result.path)
                try:
                    if not is_shutting_down():
                        page.update()
                except Exception as ex:
                    logger.error(f"フォルダ選択更新エラー: {ex}")

        file_picker.on_result = on_result
        file_picker.get_directory_path(t("messages.folder_picker_title"))

    # 設定保存コールバック
    def on_settings_save(new_data_dir):
        """設定保存時のコールバック"""
        if is_shutting_down():
            return

        from src.core.foreground_monitor import ensure_data_dir

        if new_data_dir and new_data_dir.strip():
            if ensure_data_dir(new_data_dir):
                settings_manager.update_setting("data_save_dir", new_data_dir)
                settings_manager.save_settings()
                # メモマネージャーのデータディレクトリも更新
                memo_manager.update_data_dir(new_data_dir)
                # SnackBarの表示
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(t("messages.settings_saved"))
                )
                page.snack_bar.open = True
                try:
                    if not is_shutting_down():
                        page.update()
                except Exception as ex:
                    logger.error(f"設定保存更新エラー: {ex}")
                logger.info(f"設定を保存しました: {new_data_dir}")
                toggle_settings_panel()  # 設定パネルを閉じる
            else:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(t("messages.invalid_directory"))
                )
                page.snack_bar.open = True
                try:
                    if not is_shutting_down():
                        page.update()
                except Exception as ex:
                    logger.error(f"エラー表示更新エラー: {ex}")
                logger.error(f"無効なディレクトリです: {new_data_dir}")
        else:
            snack_text = t("messages.directory_required")
            page.snack_bar = ft.SnackBar(content=ft.Text(snack_text))
            page.snack_bar.open = True
            try:
                if not is_shutting_down():
                    page.update()
            except Exception as ex:
                logger.error(f"エラー表示更新エラー: {ex}")
            logger.error("ディレクトリが入力されていません")

    # 設定パネルを初期化
    settings_panel = SettingsPanel(
        initial_data_dir=settings_manager.get_data_save_dir(),
        on_save=on_settings_save,
        on_cancel=toggle_settings_panel,
        on_pick_directory=pick_directory,
    )

    # ヘッダーコンポーネントを初期化
    def on_always_on_top_toggle(is_enabled: bool):
        """常に最前面設定の切り替え"""
        try:
            page.window.always_on_top = is_enabled
            settings_manager.update_always_on_top_setting(is_enabled)
            settings_manager.save_settings()
            logger.info(f"常に最前面設定を変更しました: {is_enabled}")

            # UI更新
            if not is_shutting_down():
                page.update()
        except Exception as e:
            logger.error(f"常に最前面設定変更エラー: {e}")

    header = HeaderComponent(
        on_settings_click_callback=toggle_settings_panel,
        on_always_on_top_callback=on_always_on_top_toggle,
    )

    # フォアグラウンド監視のコールバック関数
    def on_app_change(app_name):
        """アプリ変更時のコールバック"""
        if app_name:
            # 現在のメモを保存してから新しいメモを読み込み
            save_current_memo()

            # 実際のアプリ変更時のみ処理
            app_display.update_app_name(app_name)
            # メモファイルを作成/読み込み
            try:
                memo_file = memo_manager.get_memo_file_path(app_name)
                if not memo_file.exists():
                    memo_manager.create_memo_file(app_name)
                memo_editor.load_memo(memo_file, app_name)
                logger.debug(f"メモを読み込みました: {app_name}")
            except Exception as e:
                logger.error(f"メモ読み込みエラー: {e}")
        # Sticky Memoにフォーカスした場合は何もしない
        # （表示・メモ共に直前の状態を保持）

    def on_ui_update():
        """UI更新のコールバック"""
        try:
            if not is_shutting_down():
                page.update()
        except Exception as update_ex:
            logger.error(f"UI更新エラー: {update_ex}")

    # フォアグラウンド監視を初期化
    foreground_monitor = ForegroundMonitor(
        settings=settings_manager.get_settings(),
        shutdown_event=_shutdown_event,
        on_app_change_callback=on_app_change,
        on_ui_update_callback=on_ui_update,
    )

    # バックグラウンドで監視を開始
    foreground_monitor.start_monitoring()

    # 初期状態で現在のアプリをチェックしてメモを読み込み

    def initial_app_check():
        """初期状態でのアプリチェック"""
        from src.core.foreground_monitor import get_foreground_app

        time.sleep(0.5)  # 少し待機してから実行
        if not is_shutting_down():
            try:
                current_app = get_foreground_app()
                if current_app:
                    logger.debug(f"初期アプリを検出しました: {current_app}")
                    on_app_change(current_app)
                    if not is_shutting_down():
                        page.update()
            except Exception as e:
                logger.error(f"初期アプリチェックエラー: {e}")

    # 初期アプリチェックを別スレッドで実行
    threading.Thread(target=initial_app_check, daemon=True).start()

    logger.debug("UIを構築します")
    main_content = ft.Column(
        [
            header.get_component(),
            app_display.get_component(),
            memo_editor.get_component(),  # メモエディターを追加
            settings_panel.get_component(),  # 設定パネルを追加
        ],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )

    page.add(main_content)
    logger.info("UIの構築が完了しました")

    # ページロード後に直接ウィンドウ設定を適用
    try:
        logger.debug("ウィンドウ設定を再適用します")
        window_settings = settings_manager.get_window_settings()
        page.window.width = window_settings["width"]
        page.window.height = window_settings["height"]

        if window_settings["left"] is not None and window_settings["top"] is not None:
            page.window.left = window_settings["left"]
            page.window.top = window_settings["top"]

        # 常に最前面設定を適用
        always_on_top = settings_manager.get_always_on_top_setting()
        page.window.always_on_top = always_on_top
        header.set_always_on_top_state(always_on_top)
        logger.debug(f"常に最前面設定を適用しました: {always_on_top}")

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
