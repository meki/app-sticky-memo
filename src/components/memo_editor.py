import logging
from collections.abc import Callable
from pathlib import Path

import flet as ft

from src.locales.i18n import t

logger = logging.getLogger("app_sticky_memo")


class MemoEditor:
    """Memo editor component"""

    def __init__(self, on_content_change: Callable[[str], None] | None = None):
        """
        Initialize MemoEditor

        Args:
            on_content_change: Callback function on text change
        """
        self.on_content_change = on_content_change
        self.current_file_path = None
        self.is_dirty = False  # Whether there are unsaved changes
        self._create_components()
        logger.debug("MemoEditor initialized")

    def _create_components(self):
        """Create editor components"""
        # Memo title display
        self.title_text = ft.Text(
            value=t("memo_editor.not_loaded"),
            size=16,
            weight=ft.FontWeight.W_500,
            color=ft.Colors.BLUE_GREY_600,
        )

        # Text area
        self.text_area = ft.TextField(
            multiline=True,
            expand=True,
            hint_text=t("memo_editor.hint_text"),
            border=ft.InputBorder.OUTLINE,
            content_padding=ft.padding.all(15),
            text_size=14,
            on_change=self._on_text_change,
        )

        # Save status display
        self.save_status = ft.Text(
            value="", size=12, color=ft.Colors.GREEN_600, visible=False
        )

        # Editor container
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
        logger.debug("Editor components created")

    def _on_text_change(self, e):
        """Handle text change"""
        self.is_dirty = True
        self.save_status.visible = False
        if self.on_content_change:
            self.on_content_change(self.text_area.value)

    def load_memo(self, file_path: Path, app_name: str):
        """
        Load memo file

        Args:
            file_path: Path to memo file
            app_name: Application name
        """
        self.current_file_path = file_path
        self.title_text.value = t("memo_editor.memo_title", app_name=app_name)

        try:
            if file_path.exists():
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                    self.text_area.value = content
                    logger.debug(f"Memo file loaded: {file_path}")
            else:
                # Template for new memo file
                template_content = t(
                    "memo_editor.template_header",
                    app_name=app_name,
                    timestamp=self._get_current_timestamp(),
                )
                self.text_area.value = template_content
                msg = f"Template set for new memo file: {file_path}"
                logger.debug(msg)

            self.is_dirty = False
            self.save_status.visible = False

        except Exception as e:
            logger.error(f"Memo file load error: {e}")
            error_msg = t("errors.memo_load_error", error=str(e))
            self.text_area.value = f"# {app_name} Memo\n\n{error_msg}\n"
            self.is_dirty = False

    def save_memo(self) -> bool:
        """
        Save the current memo

        Returns:
            Whether save was successful
        """
        if not self.current_file_path or not self.is_dirty:
            return True

        try:
            # Create directory if it doesn't exist
            self.current_file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.current_file_path, "w", encoding="utf-8") as f:
                f.write(self.text_area.value)

            self.is_dirty = False
            self.save_status.value = t("memo_editor.saved_status")
            self.save_status.visible = True
            logger.debug(f"Memo file saved: {self.current_file_path}")
            return True

        except Exception as e:
            logger.error(f"Memo file save error: {e}")
            self.save_status.value = t("memo_editor.save_error", error=str(e))
            self.save_status.color = ft.Colors.RED_600
            self.save_status.visible = True
            return False

    def auto_save(self):
        """Auto-save (only if there are changes)"""
        if self.is_dirty:
            success = self.save_memo()
            if success:
                # Hide save status message after 3 seconds
                import threading

                def hide_status():
                    import time

                    time.sleep(3)
                    self.save_status.visible = False

                threading.Thread(target=hide_status, daemon=True).start()

    def get_component(self):
        """Get the editor component"""
        return self.editor_container

    def get_current_content(self) -> str:
        """Get current text content"""
        return self.text_area.value if self.text_area.value else ""

    def has_unsaved_changes(self) -> bool:
        """Whether there are unsaved changes"""
        return self.is_dirty

    def _get_current_timestamp(self) -> str:
        """Get current timestamp"""
        import time

        return time.strftime("%Y-%m-%d %H:%M:%S")

    def clear_memo(self):
        """Clear the memo"""
        self.text_area.value = ""
        self.title_text.value = t("memo_editor.not_loaded")
        self.current_file_path = None
        self.is_dirty = False
        self.save_status.visible = False
        logger.debug("Memo editor cleared")
