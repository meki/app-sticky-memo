import logging
import sys
from pathlib import Path

import yaml

logger = logging.getLogger("app_sticky_memo")


def get_resource_path(relative_path: str) -> Path:
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        # Normal execution
        base_path = Path(__file__).parent.parent.parent

    return base_path / relative_path


class I18nManager:
    """Internationalization manager class"""

    def __init__(self, language: str = "ja", locales_dir: str = "src/locales"):
        """
        Initialize I18nManager

        Args:
            language: Language code to use (e.g. ja, en)
            locales_dir: Directory where locale files are stored
        """
        self.language = language
        # Use resource path function for proper path resolution
        self.locales_dir = get_resource_path(locales_dir)
        self.strings = {}
        self._load_language_file()
        logger.debug(
            f"I18nManager initialized (language: {language}, "
            f"locales_dir: {self.locales_dir})"
        )

    def _load_language_file(self):
        """Load language file"""
        language_file = self.locales_dir / f"{self.language}.yaml"

        if not language_file.exists():
            logger.error(f"Language file not found: {language_file}")
            self.strings = {}
            return

        try:
            with open(language_file, encoding="utf-8") as f:
                self.strings = yaml.safe_load(f) or {}
            logger.debug(f"Language file loaded: {language_file}")
        except Exception as e:
            logger.error(f"Language file load error: {e}")
            self.strings = {}

    def t(self, key: str, **kwargs) -> str:
        """
        Get translated text

        Args:
            key: Dot notation key (e.g. "memo_editor.hint_text")
            **kwargs: Parameters for formatting

        Returns:
            Translated text
        """
        try:
            # Access nested dict by dot notation
            value = self.strings
            for part in key.split("."):
                value = value[part]

            # Apply format parameters if present
            if kwargs and isinstance(value, str):
                return value.format(**kwargs)

            return str(value)
        except (KeyError, TypeError) as e:
            logger.warning(f"Translation key not found: {key} - {e}")
            return key  # Return key itself if not found

    def get_language(self) -> str:
        """Get current language code"""
        return self.language

    def set_language(self, language: str):
        """Change language"""
        if language != self.language:
            self.language = language
            self._load_language_file()
            logger.info(f"Language changed: {language}")

    def get_available_languages(self) -> list[str]:
        """Get list of available languages"""
        languages = []
        for file_path in self.locales_dir.glob("*.yaml"):
            languages.append(file_path.stem)
        return sorted(languages)


# Global i18n instance
_i18n_instance = None


def get_i18n() -> I18nManager:
    """Get the global i18n instance"""
    global _i18n_instance
    if _i18n_instance is None:
        _i18n_instance = I18nManager()
    return _i18n_instance


def t(key: str, **kwargs) -> str:
    """Convenience function to get translated text"""
    return get_i18n().t(key, **kwargs)
