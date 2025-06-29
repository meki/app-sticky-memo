import logging
from pathlib import Path

import yaml

logger = logging.getLogger("app_sticky_memo")


class I18nManager:
    """多言語対応管理クラス"""

    def __init__(self, language: str = "ja", locales_dir: str = "src/locales"):
        """
        I18nManagerを初期化

        Args:
            language: 使用する言語コード（例: ja, en）
            locales_dir: ロケールファイルが保存されているディレクトリ
        """
        self.language = language
        self.locales_dir = Path(locales_dir)
        self.strings = {}
        self._load_language_file()
        logger.debug(f"I18nManagerを初期化しました（言語: {language}）")

    def _load_language_file(self):
        """言語ファイルを読み込み"""
        language_file = self.locales_dir / f"{self.language}.yaml"

        if not language_file.exists():
            logger.error(f"言語ファイルが見つかりません: {language_file}")
            self.strings = {}
            return

        try:
            with open(language_file, encoding="utf-8") as f:
                self.strings = yaml.safe_load(f) or {}
            logger.debug(f"言語ファイルを読み込みました: {language_file}")
        except Exception as e:
            logger.error(f"言語ファイル読み込みエラー: {e}")
            self.strings = {}

    def t(self, key: str, **kwargs) -> str:
        """
        翻訳テキストを取得

        Args:
            key: ドット記法のキー（例: "memo_editor.hint_text"）
            **kwargs: フォーマット用のパラメータ

        Returns:
            翻訳されたテキスト
        """
        try:
            # ドット記法でネストされた辞書にアクセス
            value = self.strings
            for part in key.split("."):
                value = value[part]

            # フォーマットパラメータがある場合は適用
            if kwargs and isinstance(value, str):
                return value.format(**kwargs)

            return str(value)
        except (KeyError, TypeError) as e:
            logger.warning(f"翻訳キーが見つかりません: {key} - {e}")
            return key  # キーが見つからない場合はキー自体を返す

    def get_language(self) -> str:
        """現在の言語コードを取得"""
        return self.language

    def set_language(self, language: str):
        """言語を変更"""
        if language != self.language:
            self.language = language
            self._load_language_file()
            logger.info(f"言語を変更しました: {language}")

    def get_available_languages(self) -> list[str]:
        """利用可能な言語の一覧を取得"""
        languages = []
        for file_path in self.locales_dir.glob("*.yaml"):
            languages.append(file_path.stem)
        return sorted(languages)


# グローバルなi18nインスタンス
_i18n_instance = None


def get_i18n() -> I18nManager:
    """グローバルなi18nインスタンスを取得"""
    global _i18n_instance
    if _i18n_instance is None:
        _i18n_instance = I18nManager()
    return _i18n_instance


def t(key: str, **kwargs) -> str:
    """翻訳テキストを取得する便利関数"""
    return get_i18n().t(key, **kwargs)
