from collections.abc import Callable

import flet as ft

from src.locales.i18n import t


class SettingsPanel:
    """UI component for the settings panel"""

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

        # Text field
        self.data_dir_field = ft.TextField(
            label=t("settings_panel.data_directory_label"),
            value=initial_data_dir,
            width=300,
            multiline=False,
        )

        # Panel container
        self.container = self._create_panel()

    def _create_panel(self) -> ft.Container:
        """Create the container for the settings panel"""
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
                                tooltip="Close",
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
            visible=False,  # Initially hidden
        )

    def _on_save_click(self, e):
        """Handle save button click"""
        self.on_save(self.data_dir_field.value.strip())

    def _on_cancel_click(self, e):
        """Handle cancel button click"""
        self.data_dir_field.value = self.initial_data_dir
        self.on_cancel()

    def _on_pick_directory_click(self, e):
        """Handle folder select button click"""
        self.on_pick_directory()

    def show(self):
        """Show the panel"""
        self.visible = True
        self.container.visible = True

    def hide(self):
        """Hide the panel"""
        self.visible = False
        self.container.visible = False

    def toggle(self):
        """Toggle panel visibility"""
        if self.visible:
            self.hide()
        else:
            self.show()

    def update_data_dir(self, new_dir: str):
        """Update the data directory field"""
        self.data_dir_field.value = new_dir
        self.initial_data_dir = new_dir

    def get_data_dir(self) -> str:
        """Get the current data directory value"""
        return self.data_dir_field.value.strip()

    def get_component(self) -> ft.Container:
        """Get the settings panel component"""
        return self.container
