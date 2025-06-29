import logging

import flet as ft

from src.locales.i18n import t

logger = logging.getLogger("app_sticky_memo")


class HeaderComponent:
    """アプリのヘッダー部分を管理するコンポーネント"""

    def __init__(self, on_settings_click_callback=None, on_always_on_top_callback=None):
        """
        HeaderComponentを初期化

        Args:
            on_settings_click_callback: 設定ボタンクリック時のコールバック関数
            on_always_on_top_callback: 常に最前面チェックボックス変更時のコールバック
        """
        self.on_settings_click_callback = on_settings_click_callback
        self.on_always_on_top_callback = on_always_on_top_callback
        self._create_components()
        logger.debug("HeaderComponentを初期化しました")

    def _create_components(self):
        """ヘッダーコンポーネントを作成"""
        # 常に最前面チェックボックス
        self.always_on_top_checkbox = ft.Checkbox(
            label=t("header.always_on_top_label"),
            value=False,
            on_change=self._on_always_on_top_change,
        )

        # 設定ボタン
        self.settings_button = ft.IconButton(
            icon=ft.Icons.SETTINGS,
            tooltip=t("header.settings_tooltip"),
            on_click=self._on_settings_click,
        )

        # ヘッダー全体
        self.header = ft.Row(
            [
                # 左側：常に最前面チェックボックス
                ft.Container(
                    content=self.always_on_top_checkbox,
                    width=120,  # チェックボックスの幅を固定
                ),
                # 中央：タイトル
                ft.Container(
                    content=ft.Text(
                        t("app.title"),
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    expand=True,
                    alignment=ft.alignment.center,
                ),
                # 右側：設定ボタン
                ft.Container(
                    content=self.settings_button,
                    width=48,  # ボタンの幅を固定
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        logger.debug("ヘッダーコンポーネントを作成しました")

    def _on_always_on_top_change(self, e):
        """常に最前面チェックボックス変更時の処理"""
        is_checked = e.control.value
        logger.debug(f"常に最前面チェックボックスが変更されました: {is_checked}")
        if self.on_always_on_top_callback:
            self.on_always_on_top_callback(is_checked)

    def set_always_on_top_state(self, is_on_top: bool):
        """常に最前面チェックボックスの状態を設定"""
        if self.always_on_top_checkbox:
            self.always_on_top_checkbox.value = is_on_top
            logger.debug(f"常に最前面チェックボックスの状態を設定: {is_on_top}")

    def _on_settings_click(self, e):
        """設定ボタンクリック時の処理"""
        logger.debug("設定ボタンがクリックされました")
        if self.on_settings_click_callback:
            self.on_settings_click_callback()

    def get_component(self):
        """ヘッダーコンポーネントを取得"""
        return self.header
