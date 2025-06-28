import logging

import flet as ft

logger = logging.getLogger("app_sticky_memo")


class HeaderComponent:
    """アプリのヘッダー部分を管理するコンポーネント"""

    def __init__(self, on_settings_click_callback=None):
        """
        HeaderComponentを初期化

        Args:
            on_settings_click_callback: 設定ボタンクリック時のコールバック関数
        """
        self.on_settings_click_callback = on_settings_click_callback
        self._create_components()
        logger.debug("HeaderComponentを初期化しました")

    def _create_components(self):
        """ヘッダーコンポーネントを作成"""
        # 設定ボタン
        self.settings_button = ft.IconButton(
            icon=ft.Icons.SETTINGS,
            tooltip="設定",
            on_click=self._on_settings_click,
        )

        # ヘッダー全体
        self.header = ft.Row(
            [
                ft.Container(expand=True),  # 左側のスペース
                ft.Text(
                    "App Sticky Memo",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(
                    content=self.settings_button,
                    width=48,  # ボタンの幅を固定
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        logger.debug("ヘッダーコンポーネントを作成しました")

    def _on_settings_click(self, e):
        """設定ボタンクリック時の処理"""
        logger.debug("設定ボタンがクリックされました")
        if self.on_settings_click_callback:
            self.on_settings_click_callback()

    def get_component(self):
        """ヘッダーコンポーネントを取得"""
        return self.header
