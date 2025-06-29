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
        self.page = None  # Will be set when added to page
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

        # Title text component
        self.title_text = ft.Text(
            t("app.title"),
            size=18,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        )

        # Title container
        self.title_container = ft.Container(
            content=self.title_text,
            alignment=ft.alignment.center,
            visible=True,  # Default visible
        )

        # Header row
        self.header = ft.Row(
            [
                # Left: Hamburger menu
                ft.Container(
                    content=self.menu_button,
                    width=48,  # Fixed width for button
                ),
                # Center: Title (conditionally visible, with expand for centering)
                ft.Container(
                    content=self.title_container,
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

    def set_page(self, page):
        """Set the page reference for accessing window properties"""
        self.page = page
        logger.debug("Page reference set for header component")
        # Initial check for title visibility
        self.update_title_visibility()

    def update_title_visibility(self):
        """Update title visibility based on window width"""
        logger.debug("update_title_visibility called")

        if not self.page:
            logger.debug("No page reference - cannot update title visibility")
            return

        # Get window width from page.window.width
        try:
            window_width = self.page.window.width if self.page.window else None
            logger.debug(f"Current window width: {window_width}")

            if window_width is not None:
                # Hide title if window width is 450px or less
                should_show_title = window_width > 450
                current_visibility = self.title_container.visible

                if current_visibility != should_show_title:
                    self.title_container.visible = should_show_title
                    # Also hide the text itself for extra safety
                    self.title_text.visible = should_show_title
                    logger.info(
                        f"Title visibility changed: {should_show_title} "
                        f"(width: {window_width})"
                    )
                    # Update the page if available
                    if hasattr(self.page, "update"):
                        self.page.update()
                        logger.debug("Page updated after title visibility change")
                else:
                    logger.debug("Title visibility unchanged")
            else:
                logger.warning("Could not get window width")
        except Exception as e:
            logger.error(f"Error updating title visibility: {e}")

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
        logger.debug("Menu button clicked")
        if self.on_settings_click_callback:
            self.on_settings_click_callback()

    def get_component(self):
        """Get the header component"""
        return self.header
