import json
import logging
from pathlib import Path

logger = logging.getLogger("app_sticky_memo")


class SettingsManager:
    """設定管理クラス"""

    def __init__(self, settings_file="settings.json"):
        """
        SettingsManagerを初期化

        Args:
            settings_file: 設定ファイル名
        """
        self.settings_file = Path(settings_file)
        self.default_settings = {
            "data_save_dir": str(Path.home() / "Documents" / "StickyMemos"),
            "window": {
                "width": 400,
                "height": 300,
                "left": None,
                "top": None,
            },
        }
        self.settings = self.load_settings()
        logger.debug("SettingsManagerを初期化しました")

    def load_settings(self):
        """設定ファイルを読み込み"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, encoding="utf-8") as f:
                    loaded_settings = json.load(f)
                    # デフォルト設定をベースに、読み込んだ設定をマージ
                    merged_settings = self.default_settings.copy()
                    for key, value in loaded_settings.items():
                        if key in merged_settings:
                            if isinstance(value, dict) and isinstance(
                                merged_settings[key], dict
                            ):
                                merged_settings[key].update(value)
                            else:
                                merged_settings[key] = value
                    logger.debug(f"設定を読み込みました: {merged_settings}")
                    return merged_settings
            except Exception as e:
                logger.error(f"設定読み込みエラー: {e}")

        logger.debug(f"デフォルト設定を使用します: {self.default_settings}")
        return self.default_settings.copy()

    def save_settings(self, settings=None):
        """設定ファイルを保存"""
        if settings is not None:
            self.settings = settings

        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            logger.debug("設定ファイルを保存しました")
            return True
        except Exception as e:
            logger.error(f"設定保存エラー: {e}")
            return False

    def get_settings(self):
        """現在の設定を取得"""
        return self.settings

    def update_setting(self, key, value):
        """特定の設定を更新"""
        self.settings[key] = value
        logger.debug(f"設定を更新しました: {key} = {value}")

    def update_window_settings(self, width, height, left, top):
        """ウィンドウ設定を更新"""
        self.settings["window"]["width"] = width
        self.settings["window"]["height"] = height
        self.settings["window"]["left"] = left
        self.settings["window"]["top"] = top
        logger.debug(f"ウィンドウ設定を更新しました: {self.settings['window']}")

    def get_window_settings(self):
        """ウィンドウ設定を取得"""
        return self.settings["window"]

    def get_data_save_dir(self):
        """データ保存ディレクトリを取得"""
        return self.settings["data_save_dir"]
