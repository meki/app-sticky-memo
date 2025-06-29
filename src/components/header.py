import logging

import flet as ft

from src.locales.i18n import t

logger = logging.getLogger("app_sticky_memo")


class HeaderComponent:
    """Component managing the app header section"""

    def __init__(self, on_settings_click_callback=None, on_always_on_top_callback=None):
        """
        Initialize HeaderComponent

        Args:
            on_settings_click_callback: Callback for settings button click
            on_always_on_top_callback: Callback for always-on-top checkbox change
        """
        self.on_settings_click_callback = on_settings_click_callback
        self.on_always_on_top_callback = on_always_on_top_callback
        self._create_components()
        logger.debug("HeaderComponent initialized")

    def _create_components(self):
        """Create header components"""
        # Hamburger menu button
        self.menu_button = ft.IconButton(
            icon=ft.Icons.MENU,
            tooltip=t("header.menu_tooltip"),
            on_click=self._on_menu_click,
        )

        # Always-on-top checkbox (moved to sidebar)
        self.always_on_top_checkbox = ft.Checkbox(
            label=t("header.always_on_top_label"),
            value=False,
            on_change=self._on_always_on_top_change,
        )

        # Header row
        self.header = ft.Row(
            [
                # Left: Hamburger menu
                ft.Container(
                    content=self.menu_button,
                    width=48,  # Fixed width for button
                ),
                # Center: Title
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
                # Right: Always-on-top checkbox
                ft.Container(
                    content=self.always_on_top_checkbox,
                    width=150,  # Fixed width for checkbox
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        logger.debug("Header components created")

    def _on_always_on_top_change(self, e):
        """Handle always-on-top checkbox change"""
        is_checked = e.control.value
        logger.debug(f"Always-on-top checkbox changed: {is_checked}")
        if self.on_always_on_top_callback:
            self.on_always_on_top_callback(is_checked)

    def set_always_on_top_state(self, is_on_top: bool):
        """Set always-on-top checkbox state"""
        if self.always_on_top_checkbox:
            self.always_on_top_checkbox.value = is_on_top
            logger.debug(f"Always-on-top checkbox state set: {is_on_top}")

    def _on_menu_click(self, e):
        """Handle menu button click"""
        print("DEBUG: Menu button clicked in header")
        logger.debug("Menu button clicked")
        if self.on_settings_click_callback:
            print("DEBUG: Calling settings callback")
            self.on_settings_click_callback()
        else:
            print("DEBUG: No settings callback found!")

    def get_component(self):
        """Get the header component"""
        return self.header
