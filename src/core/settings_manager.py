import json
import logging
from pathlib import Path

logger = logging.getLogger("app_sticky_memo")


class SettingsManager:
    """Settings management class"""

    def __init__(self, settings_file="settings.json"):
        """
        Initialize SettingsManager

        Args:
            settings_file: Settings file name
        """
        self.settings_file = Path(settings_file)
        self.default_settings = {
            "data_save_dir": str(Path.home() / "Documents" / "StickyMemos"),
            "window": {
                "width": 400,
                "height": 300,
                "left": None,
                "top": None,
                "always_on_top": False,
            },
        }
        self.settings = self.load_settings()
        logger.debug("SettingsManager initialized")

    def load_settings(self):
        """Load settings file"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, encoding="utf-8") as f:
                    loaded_settings = json.load(f)
                    # Merge loaded settings into default settings
                    merged_settings = self.default_settings.copy()
                    for key, value in loaded_settings.items():
                        if key in merged_settings:
                            if isinstance(value, dict) and isinstance(
                                merged_settings[key], dict
                            ):
                                merged_settings[key].update(value)
                            else:
                                merged_settings[key] = value
                    logger.debug(f"Settings loaded: {merged_settings}")
                    return merged_settings
            except Exception as e:
                logger.error(f"Settings load error: {e}")

        logger.debug(f"Using default settings: {self.default_settings}")
        return self.default_settings.copy()

    def save_settings(self, settings=None):
        """Save settings file"""
        if settings is not None:
            self.settings = settings

        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            logger.debug("Settings file saved")
            return True
        except Exception as e:
            logger.error(f"Settings save error: {e}")
            return False

    def get_settings(self):
        """Get current settings"""
        return self.settings

    def update_setting(self, key, value):
        """Update a specific setting"""
        self.settings[key] = value
        logger.debug(f"Setting updated: {key} = {value}")

    def update_window_settings(self, width, height, left, top):
        """Update window settings"""
        self.settings["window"]["width"] = width
        self.settings["window"]["height"] = height
        self.settings["window"]["left"] = left
        self.settings["window"]["top"] = top
        logger.debug(f"Window settings updated: {self.settings['window']}")

    def get_window_settings(self):
        """Get window settings"""
        return self.settings["window"]

    def update_always_on_top_setting(self, always_on_top: bool):
        """Update always-on-top setting"""
        self.settings["window"]["always_on_top"] = always_on_top
        logger.debug(f"Always-on-top setting updated: {always_on_top}")

    def get_always_on_top_setting(self) -> bool:
        """Get always-on-top setting"""
        return self.settings["window"].get("always_on_top", False)

    def get_data_save_dir(self):
        """Get data save directory"""
        return self.settings["data_save_dir"]
