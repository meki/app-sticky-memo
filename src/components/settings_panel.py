from collections.abc import Callable

import flet as ft

from src.locales.i18n import t


class SettingsPanel:
    """設定パネルのUIコンポーネント"""

    def __init__(
        self,
        initial_data_dir: str,
        on_save: Callable[[str], None],
        on_cancel: Callable[[], None],
        on_pick_directory: Callable[[], None],
    ):
        self.initial_data_dir = initial_data_dir
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.on_pick_directory = on_pick_directory
        self.visible = False

        # テキストフィールド
        self.data_dir_field = ft.TextField(
            label=t("settings_panel.data_directory_label"),
            value=initial_data_dir,
            width=300,
            multiline=False,
        )

        # パネルコンテナ
        self.container = self._create_panel()

    def _create_panel(self) -> ft.Container:
        """設定パネルのコンテナを作成"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                t("settings_panel.title"),
                                size=20,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Container(expand=True),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                tooltip="閉じる",
                                on_click=self._on_cancel_click,
                            ),
                        ]
                    ),
                    ft.Container(height=10),
                    ft.Text(t("settings_panel.data_directory_label"), size=14),
                    ft.Container(height=5),
                    ft.Row(
                        [
                            self.data_dir_field,
                            ft.ElevatedButton(
                                t("settings_panel.browse_button"),
                                icon=ft.Icons.FOLDER_OPEN,
                                on_click=self._on_pick_directory_click,
                            ),
                        ]
                    ),
                    ft.Container(height=20),
                    ft.Row(
                        [
                            ft.Container(expand=True),
                            ft.TextButton(
                                t("settings_panel.cancel_button"),
                                on_click=self._on_cancel_click,
                            ),
                            ft.Container(width=10),
                            ft.ElevatedButton(
                                t("settings_panel.save_button"),
                                on_click=self._on_save_click,
                            ),
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

    def _on_save_click(self, e):
        """保存ボタンクリック時の処理"""
        self.on_save(self.data_dir_field.value.strip())

    def _on_cancel_click(self, e):
        """キャンセルボタンクリック時の処理"""
        self.data_dir_field.value = self.initial_data_dir
        self.on_cancel()

    def _on_pick_directory_click(self, e):
        """フォルダ選択ボタンクリック時の処理"""
        self.on_pick_directory()

    def show(self):
        """パネルを表示"""
        self.visible = True
        self.container.visible = True

    def hide(self):
        """パネルを非表示"""
        self.visible = False
        self.container.visible = False

    def toggle(self):
        """パネルの表示/非表示を切り替え"""
        if self.visible:
            self.hide()
        else:
            self.show()

    def update_data_dir(self, new_dir: str):
        """データディレクトリフィールドを更新"""
        self.data_dir_field.value = new_dir
        self.initial_data_dir = new_dir

    def get_data_dir(self) -> str:
        """現在のデータディレクトリ値を取得"""
        return self.data_dir_field.value.strip()

    def get_component(self) -> ft.Container:
        """設定パネルのコンポーネントを取得"""
        return self.container
