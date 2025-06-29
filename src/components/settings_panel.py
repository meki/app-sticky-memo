from collections.abc import Callable

import flet as ft

from src.locales.i18n import t


class SettingsPanel:
    """UI component for the sidebar settings panel"""

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
            width=280,
            multiline=False,
            color=ft.Colors.WHITE,  # Bright text color for dark background
            border_color=ft.Colors.WHITE54,  # Light border for dark theme
            focused_border_color=ft.Colors.BLUE_400,  # Focused border color
        )

        # Sidebar container
        self.container = self._create_sidebar()

    def _create_sidebar(self) -> ft.Container:
        """Create the sidebar container for settings"""
        return ft.Container(
            content=ft.Column(
                [
                    # Header with close button
                    ft.Row(
                        [
                            ft.Text(
                                t("settings_panel.title"),
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Container(expand=True),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                tooltip="Close",
                                icon_color=ft.Colors.WHITE,
                                on_click=self._on_cancel_click,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(color=ft.Colors.WHITE24),
                    ft.Container(height=10),
                    # Settings content
                    ft.Text(
                        t("settings_panel.data_directory_label"),
                        size=14,
                        color=ft.Colors.WHITE70,
                    ),
                    ft.Container(height=5),
                    self.data_dir_field,
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        t("settings_panel.browse_button"),
                        icon=ft.Icons.FOLDER_OPEN,
                        width=280,
                        on_click=self._on_pick_directory_click,
                    ),
                    ft.Container(height=30),
                    # Action buttons
                    ft.ElevatedButton(
                        t("settings_panel.save_button"),
                        width=280,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.BLUE_600,
                            color=ft.Colors.WHITE,
                        ),
                        on_click=self._on_save_click,
                    ),
                    ft.Container(height=10),
                    ft.TextButton(
                        t("settings_panel.cancel_button"),
                        width=280,
                        style=ft.ButtonStyle(color=ft.Colors.WHITE70),
                        on_click=self._on_cancel_click,
                    ),
                ],
                spacing=0,
                scroll=ft.ScrollMode.AUTO,
            ),
            width=320,
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.BLUE_GREY_800,
            visible=False,  # Initially hidden
            border_radius=ft.border_radius.only(top_right=10, bottom_right=10),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.BLACK26,
                offset=ft.Offset(2, 0),
            ),
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
