import logging
from collections.abc import Callable
from pathlib import Path

import flet as ft

from src.locales.i18n import t

logger = logging.getLogger("app_sticky_memo")


class MemoEditor:
    """メモエディターコンポーネント"""

    def __init__(self, on_content_change: Callable[[str], None] | None = None):
        """
        MemoEditorを初期化

        Args:
            on_content_change: テキスト変更時のコールバック関数
        """
        self.on_content_change = on_content_change
        self.current_file_path = None
        self.is_dirty = False  # 変更されているかどうか
        self._create_components()
        logger.debug("MemoEditorを初期化しました")

    def _create_components(self):
        """エディターコンポーネントを作成"""
        # メモタイトル表示
        self.title_text = ft.Text(
            value=t("memo_editor.not_loaded"),
            size=16,
            weight=ft.FontWeight.W_500,
            color=ft.Colors.BLUE_GREY_600,
        )

        # テキストエリア
        self.text_area = ft.TextField(
            multiline=True,
            expand=True,
            hint_text=t("memo_editor.hint_text"),
            border=ft.InputBorder.OUTLINE,
            content_padding=ft.padding.all(15),
            text_size=14,
            on_change=self._on_text_change,
        )

        # 保存状態表示
        self.save_status = ft.Text(
            value="", size=12, color=ft.Colors.GREEN_600, visible=False
        )

        # エディターコンテナ
        self.editor_container = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            self.title_text,
                            ft.Container(expand=True),
                            self.save_status,
                        ]
                    ),
                    ft.Container(height=10),
                    self.text_area,
                ],
                spacing=0,
                expand=True,
            ),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.border_radius.all(10),
            margin=ft.margin.all(10),
            border=ft.border.all(1, ft.Colors.BLUE_GREY_200),
            expand=True,
        )
        logger.debug("エディターコンポーネントを作成しました")

    def _on_text_change(self, e):
        """テキスト変更時の処理"""
        self.is_dirty = True
        self.save_status.visible = False
        if self.on_content_change:
            self.on_content_change(self.text_area.value)

    def load_memo(self, file_path: Path, app_name: str):
        """
        メモファイルを読み込み

        Args:
            file_path: メモファイルのパス
            app_name: アプリケーション名
        """
        self.current_file_path = file_path
        self.title_text.value = t("memo_editor.memo_title", app_name=app_name)

        try:
            if file_path.exists():
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                    self.text_area.value = content
                    logger.debug(f"メモファイルを読み込みました: {file_path}")
            else:
                # 新しいメモファイルのテンプレート
                template_content = t(
                    "memo_editor.template_header",
                    app_name=app_name,
                    timestamp=self._get_current_timestamp(),
                )
                self.text_area.value = template_content
                msg = f"新しいメモファイル用テンプレートを設定しました: {file_path}"
                logger.debug(msg)

            self.is_dirty = False
            self.save_status.visible = False

        except Exception as e:
            logger.error(f"メモファイル読み込みエラー: {e}")
            error_msg = t("errors.memo_load_error", error=str(e))
            self.text_area.value = f"# {app_name} のメモ\n\n{error_msg}\n"
            self.is_dirty = False

    def save_memo(self) -> bool:
        """
        現在のメモを保存

        Returns:
            保存が成功したかどうか
        """
        if not self.current_file_path or not self.is_dirty:
            return True

        try:
            # ディレクトリが存在しない場合は作成
            self.current_file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.current_file_path, "w", encoding="utf-8") as f:
                f.write(self.text_area.value)

            self.is_dirty = False
            self.save_status.value = t("memo_editor.saved_status")
            self.save_status.visible = True
            logger.debug(f"メモファイルを保存しました: {self.current_file_path}")
            return True

        except Exception as e:
            logger.error(f"メモファイル保存エラー: {e}")
            self.save_status.value = t("memo_editor.save_error", error=str(e))
            self.save_status.color = ft.Colors.RED_600
            self.save_status.visible = True
            return False

    def auto_save(self):
        """自動保存（変更がある場合のみ）"""
        if self.is_dirty:
            success = self.save_memo()
            if success:
                # 3秒後に保存状態メッセージを非表示にする
                import threading

                def hide_status():
                    import time

                    time.sleep(3)
                    self.save_status.visible = False

                threading.Thread(target=hide_status, daemon=True).start()

    def get_component(self):
        """エディターコンポーネントを取得"""
        return self.editor_container

    def get_current_content(self) -> str:
        """現在のテキスト内容を取得"""
        return self.text_area.value if self.text_area.value else ""

    def has_unsaved_changes(self) -> bool:
        """未保存の変更があるかどうか"""
        return self.is_dirty

    def _get_current_timestamp(self) -> str:
        """現在のタイムスタンプを取得"""
        import time

        return time.strftime("%Y-%m-%d %H:%M:%S")

    def clear_memo(self):
        """メモをクリア"""
        self.text_area.value = ""
        self.title_text.value = t("memo_editor.not_loaded")
        self.current_file_path = None
        self.is_dirty = False
        self.save_status.visible = False
        logger.debug("メモエディターをクリアしました")
