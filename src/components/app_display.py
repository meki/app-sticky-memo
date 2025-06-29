import logging

import flet as ft

logger = logging.getLogger("app_sticky_memo")


class AppDisplayComponent:
    """Component to display the current app name"""

    def __init__(self, initial_text="Monitoring app..."):
        """
        Initialize AppDisplayComponent

        Args:
            initial_text: Initial display text
        """
        self.initial_text = initial_text
        self._create_components()
        logger.debug("AppDisplayComponent initialized")

    def _create_components(self):
        """Create app display components"""
        # App name display text
        self.current_app_text = ft.Text(
            value=self.initial_text,
            size=16,
            text_align=ft.TextAlign.CENTER,
            weight=ft.FontWeight.W_500,
        )

        # Container for app name display
        self.app_display_container = ft.Container(
            content=self.current_app_text,
            padding=ft.padding.all(20),
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.BLUE_GREY_50,
            border_radius=ft.border_radius.all(10),
            margin=ft.margin.all(10),
            border=ft.border.all(1, ft.Colors.BLUE_GREY_200),
        )
        logger.debug("App display components created")

    def update_app_name(self, app_name):
        """
        Update the displayed app name

        Args:
            app_name: App name to display
        """
        if app_name:
            self.current_app_text.value = f"Current app: {app_name}"
            logger.debug(f"App name updated: {app_name}")
        else:
            self.current_app_text.value = "App Sticky Memo is focused"
            logger.debug("Updated display to show App Sticky Memo is focused")

    def get_component(self):
        """Get the app display component"""
        return self.app_display_container

    def get_text_component(self):
        """Get the text component itself (for direct reference)"""
        return self.current_app_text
