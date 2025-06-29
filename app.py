import logging
import threading
import time

import flet as ft

from src.components.header import HeaderComponent
from src.components.memo_editor import MemoEditor
from src.components.settings_panel import SettingsPanel
from src.core.foreground_monitor import ForegroundMonitor
from src.core.memo_manager import MemoManager
from src.core.settings_manager import SettingsManager
from src.locales.i18n import t

# Custom logger setup
logger = logging.getLogger("app_sticky_memo")
logger.setLevel(logging.DEBUG)

# Console handler setup
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter setup
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
)
console_handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(console_handler)


def main(page: ft.Page):
    logger.info(t("logging.app_start"))
    page.title = t("app.title")
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.padding = ft.padding.all(10)

    # Application shutdown flag (kept as a global reference)
    _shutdown_event = threading.Event()

    def is_shutting_down():
        return _shutdown_event.is_set()

    def set_shutdown():
        _shutdown_event.set()
        logger.info("Set application shutdown flag")

    # Initialize settings manager
    settings_manager = SettingsManager()
    settings = settings_manager.get_settings()
    logger.debug(f"Loaded settings: {settings}")

    # Restore window position and size
    window_settings = settings_manager.get_window_settings()
    logger.debug(f"Restoring window settings: {window_settings}")

    page.window.width = window_settings["width"]
    page.window.height = window_settings["height"]
    width, height = window_settings["width"], window_settings["height"]
    logger.info(f"Set window size: {width} x {height}")

    if window_settings["left"] is not None and window_settings["top"] is not None:
        page.window.left = window_settings["left"]
        page.window.top = window_settings["top"]
        left, top = window_settings["left"], window_settings["top"]
        logger.info(f"Set window position: ({left}, {top})")
    else:
        logger.info("No window position set (first launch)")

    # Handle window events
    def on_window_event(e):
        logger.debug(f"Window event: {e.data}")

        if e.data == "close":
            logger.info("Window is closing - saving settings")
            set_shutdown()
            save_window_settings()
        elif e.data in ["moved", "resized"] and not is_shutting_down():
            logger.info(f"Window {e.data} event detected")
            # Save directly (no delay)
            save_window_settings()

    def save_window_settings():
        """Common function to save window settings"""
        if is_shutting_down():
            logger.debug("Skipping window settings save during shutdown")
            return

        try:
            # Save current memo (on shutdown)
            if is_shutting_down():
                save_current_memo()

            # Get current window position and size
            current_width = page.window.width
            current_height = page.window.height
            current_left = page.window.left
            current_top = page.window.top

            logger.debug("Current window info:")
            logger.debug(f"  Size: {current_width} x {current_height}")
            logger.debug(f"  Position: ({current_left}, {current_top})")

            # Update settings
            settings_manager.update_window_settings(
                current_width, current_height, current_left, current_top
            )

            # Save settings
            settings_manager.save_settings()
            window_settings_msg = settings_manager.get_window_settings()
            logger.debug(f"Saved window settings: {window_settings_msg}")
        except Exception as ex:
            logger.error(f"Error saving window settings: {ex}")
            # If error occurs, check shutdown flag and stop if needed
            if is_shutting_down():
                return

    page.window.on_event = on_window_event

    # Handle page disconnect (as backup)
    def on_disconnect(e):
        logger.info("Page disconnected - saving settings")
        set_shutdown()
        save_window_settings()

    page.on_disconnect = on_disconnect

    # Initialize memo manager
    memo_manager = MemoManager(settings_manager.get_data_save_dir())

    # Initialize memo editor
    def on_memo_content_change(content):
        """Callback when memo content changes"""

        # Just auto-save after 2 seconds
        def delayed_save():
            time.sleep(2)  # Wait 2 seconds
            if not is_shutting_down() and memo_editor:
                try:
                    memo_editor.auto_save()
                    # Update UI
                    if not is_shutting_down():
                        page.update()
                except Exception as ex:
                    logger.error(f"Error updating UI after autosave: {ex}")

        # Cancel existing timer if present
        if (
            hasattr(on_memo_content_change, "_save_timer")
            and on_memo_content_change._save_timer
        ):
            on_memo_content_change._save_timer.cancel()

        # Start new timer
        on_memo_content_change._save_timer = threading.Timer(2.0, delayed_save)
        on_memo_content_change._save_timer.daemon = True
        on_memo_content_change._save_timer.start()

    memo_editor = MemoEditor(on_content_change=on_memo_content_change)

    # Common function to save current memo
    def save_current_memo():
        """Save the current memo"""
        try:
            if memo_editor.has_unsaved_changes():
                memo_editor.save_memo()
                logger.debug("Saved current memo")
        except Exception as e:
            logger.error(f"Error saving memo: {e}")

    # State for settings panel
    settings_panel_visible = False

    # Function to toggle settings panel
    def toggle_settings_panel():
        if is_shutting_down():
            return
        nonlocal settings_panel_visible
        settings_panel_visible = not settings_panel_visible
        logger.debug(f"Settings panel visibility: {settings_panel_visible}")

        # Update settings panel visibility
        settings_panel.toggle()

        # Recreate layout
        page.controls.clear()
        app_layout = create_layout()
        page.add(app_layout)

        try:
            if not is_shutting_down():
                page.update()
        except Exception as ex:
            logger.error(f"Error updating settings panel: {ex}")

    # Pre-initialize file picker
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    logger.debug("File picker initialized")

    # Folder select handler
    def pick_directory():
        """Handle folder selection"""
        logger.debug("Folder select button clicked")

        def on_result(result: ft.FilePickerResultEvent):
            logger.debug(f"Folder select result: {result.path}")
            if result.path and not is_shutting_down():
                settings_panel.update_data_dir(result.path)
                try:
                    if not is_shutting_down():
                        page.update()
                except Exception as ex:
                    logger.error(f"Error updating after folder select: {ex}")

        file_picker.on_result = on_result
        file_picker.get_directory_path(t("messages.folder_picker_title"))

    # Settings save callback
    def on_settings_save(new_data_dir):
        """Callback when saving settings"""
        if is_shutting_down():
            return

        from src.core.foreground_monitor import ensure_data_dir

        if new_data_dir and new_data_dir.strip():
            if ensure_data_dir(new_data_dir):
                settings_manager.update_setting("data_save_dir", new_data_dir)
                settings_manager.save_settings()
                # Also update memo manager's data directory
                memo_manager.update_data_dir(new_data_dir)
                # Show SnackBar
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(t("messages.settings_saved"))
                )
                page.snack_bar.open = True
                try:
                    if not is_shutting_down():
                        page.update()
                except Exception as ex:
                    logger.error(f"Error updating after settings save: {ex}")
                logger.info(f"Settings saved: {new_data_dir}")
                toggle_settings_panel()  # Close settings panel
            else:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(t("messages.invalid_directory"))
                )
                page.snack_bar.open = True
                try:
                    if not is_shutting_down():
                        page.update()
                except Exception as ex:
                    logger.error(f"Error updating after invalid directory: {ex}")
                logger.error(f"Invalid directory: {new_data_dir}")
        else:
            snack_text = t("messages.directory_required")
            page.snack_bar = ft.SnackBar(content=ft.Text(snack_text))
            page.snack_bar.open = True
            try:
                if not is_shutting_down():
                    page.update()
            except Exception as ex:
                logger.error(f"Error updating after empty directory: {ex}")
            logger.error("No directory entered")

    # Initialize settings panel
    settings_panel = SettingsPanel(
        initial_data_dir=settings_manager.get_data_save_dir(),
        on_save=on_settings_save,
        on_cancel=toggle_settings_panel,
        on_pick_directory=pick_directory,
    )

    # Initialize header component
    def on_always_on_top_toggle(is_enabled: bool):
        """Toggle always-on-top setting"""
        try:
            page.window.always_on_top = is_enabled
            settings_manager.update_always_on_top_setting(is_enabled)
            settings_manager.save_settings()
            logger.info(f"Always-on-top setting changed: {is_enabled}")

            # Update UI
            if not is_shutting_down():
                page.update()
        except Exception as e:
            logger.error(f"Error changing always-on-top setting: {e}")

    header = HeaderComponent(
        on_settings_click_callback=toggle_settings_panel,
        on_always_on_top_callback=on_always_on_top_toggle,
    )

    # Set page reference for header to handle window resize
    header.set_page(page)

    # Handle window resize
    def on_resize(e):
        logger.debug("page.on_resize event triggered")
        if is_shutting_down():
            logger.debug("Skipping resize handling due to shutdown")
            return

        width, height = page.window.width, page.window.height
        logger.debug(f"Resize event: {width} x {height}")

        # Save settings directly after resize (no delay)
        save_window_settings()

        header.update_title_visibility()

    def enhanced_window_event(e):
        logger.debug(f"Window event: {e.data}")

        if e.data == "close":
            logger.info("Window is closing - saving settings")
            set_shutdown()
            save_window_settings()
        elif e.data in ["moved", "resized"] and not is_shutting_down():
            logger.info(f"window.on_event {e.data} event detected")
            # Save directly (no delay)
            save_window_settings()

            # If resized, update header title visibility
            if e.data == "resized":
                on_resize(e)

    # Replace the window event handler with the enhanced version
    page.window.on_event = enhanced_window_event

    # Callback for foreground app change
    def on_app_change(app_name):
        """Callback when app changes"""
        if app_name:
            # Save current memo before loading new one
            save_current_memo()

            try:
                memo_file = memo_manager.get_memo_file_path(app_name)
                if not memo_file.exists():
                    memo_manager.create_memo_file(app_name)
                # Use mapped memo name for display in memo_editor
                memo_name = memo_manager.get_memo_name(app_name)
                memo_editor.load_memo(memo_file, memo_name)
                logger.debug(f"Loaded memo: {app_name} -> {memo_name}")
            except Exception as e:
                logger.error(f"Error loading memo: {e}")
        # Do nothing if Sticky Memo is focused (keep previous state)

    def on_ui_update():
        """Callback for UI update"""
        try:
            if not is_shutting_down():
                page.update()
        except Exception as update_ex:
            logger.error(f"Error updating UI: {update_ex}")

    # Initialize foreground monitor
    foreground_monitor = ForegroundMonitor(
        settings=settings_manager.get_settings(),
        shutdown_event=_shutdown_event,
        on_app_change_callback=on_app_change,
        on_ui_update_callback=on_ui_update,
    )

    # Start monitoring in background
    foreground_monitor.start_monitoring()

    # Check current app and load memo on startup
    def initial_app_check():
        """Check app on startup"""
        from src.core.foreground_monitor import get_foreground_app

        time.sleep(0.5)  # Wait a bit before running
        if not is_shutting_down():
            try:
                current_app = get_foreground_app()
                if current_app:
                    logger.debug(f"Detected initial app: {current_app}")
                    on_app_change(current_app)
                    if not is_shutting_down():
                        page.update()
            except Exception as e:
                logger.error(f"Error during initial app check: {e}")

    # Run initial app check in a separate thread
    threading.Thread(target=initial_app_check, daemon=True).start()

    logger.debug("Building UI")

    # Create main content area
    main_content = ft.Column(
        [
            header.get_component(),
            memo_editor.get_component(),
        ],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )

    # Function to create layout with conditional sidebar
    def create_layout():
        """Create layout with conditional sidebar"""
        if settings_panel_visible:
            # When sidebar is visible, show it as overlay
            return ft.Stack(
                [
                    # Main content (background layer)
                    ft.Container(
                        content=main_content,
                        expand=True,
                    ),
                    # Sidebar overlay (foreground layer)
                    ft.Container(
                        content=settings_panel.get_component(),
                        alignment=ft.alignment.center_left,
                        expand=True,
                    ),
                ],
                expand=True,
            )
        else:
            # When sidebar is hidden, show only main content
            return ft.Container(
                content=main_content,
                expand=True,
            )

    # Create initial app layout
    app_layout = create_layout()

    page.add(app_layout)
    logger.info("UI build complete")

    # Apply window settings directly after page load
    try:
        logger.debug("Reapplying window settings")
        window_settings = settings_manager.get_window_settings()
        page.window.width = window_settings["width"]
        page.window.height = window_settings["height"]

        if window_settings["left"] is not None and window_settings["top"] is not None:
            page.window.left = window_settings["left"]
            page.window.top = window_settings["top"]

        # Apply always-on-top setting
        always_on_top = settings_manager.get_always_on_top_setting()
        page.window.always_on_top = always_on_top
        header.set_always_on_top_state(always_on_top)
        logger.debug(f"Applied always-on-top setting: {always_on_top}")

        # Update header title visibility after window settings are applied
        header.update_title_visibility()

        try:
            if not is_shutting_down():
                page.update()
        except Exception as update_ex:
            logger.error(f"Error updating window settings: {update_ex}")
        logger.info("Reapplied window settings complete")
    except Exception as ex:
        logger.error(f"Error reapplying window settings: {ex}")


logger.info("Starting App Sticky Memo")
ft.app(main)
