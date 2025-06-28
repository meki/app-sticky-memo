import logging

import flet as ft

logger = logging.getLogger("app_sticky_memo")


class AppDisplayComponent:
    """現在のアプリ名を表示するコンポーネント"""

    def __init__(self, initial_text="アプリを監視中..."):
        """
        AppDisplayComponentを初期化

        Args:
            initial_text: 初期表示テキスト
        """
        self.initial_text = initial_text
        self._create_components()
        logger.debug("AppDisplayComponentを初期化しました")

    def _create_components(self):
        """アプリ表示コンポーネントを作成"""
        # アプリ名表示テキスト
        self.current_app_text = ft.Text(
            value=self.initial_text,
            size=16,
            text_align=ft.TextAlign.CENTER,
            weight=ft.FontWeight.W_500,
        )

        # アプリ名表示用のコンテナ
        self.app_display_container = ft.Container(
            content=self.current_app_text,
            padding=ft.padding.all(20),
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.BLUE_GREY_50,
            border_radius=ft.border_radius.all(10),
            margin=ft.margin.all(10),
            border=ft.border.all(1, ft.Colors.BLUE_GREY_200),
        )
        logger.debug("アプリ表示コンポーネントを作成しました")

    def update_app_name(self, app_name):
        """
        表示するアプリ名を更新

        Args:
            app_name: 表示するアプリ名
        """
        if app_name:
            self.current_app_text.value = f"現在のアプリ: {app_name}"
            logger.debug(f"アプリ名を更新しました: {app_name}")
        else:
            self.current_app_text.value = "App Sticky Memo にフォーカス中"
            logger.debug("App Sticky Memoにフォーカス中の表示に更新しました")

    def get_component(self):
        """アプリ表示コンポーネントを取得"""
        return self.app_display_container

    def get_text_component(self):
        """テキストコンポーネント自体を取得（直接参照が必要な場合）"""
        return self.current_app_text
