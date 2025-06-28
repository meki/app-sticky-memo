import logging
import time
from pathlib import Path

logger = logging.getLogger("app_sticky_memo")


class MemoManager:
    """メモファイル管理クラス"""

    def __init__(self, data_dir: str):
        """
        MemoManagerを初期化

        Args:
            data_dir: メモファイルの保存ディレクトリ
        """
        self.data_dir = Path(data_dir)
        self.ensure_data_dir()
        logger.debug(f"MemoManagerを初期化しました: {self.data_dir}")

    def ensure_data_dir(self) -> bool:
        """データディレクトリを作成"""
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"データディレクトリ作成エラー: {e}")
            return False

    def get_memo_file_path(self, app_name: str) -> Path:
        """
        アプリ名からメモファイルのパスを生成

        Args:
            app_name: アプリケーション名

        Returns:
            メモファイルのパス
        """
        safe_app_name = self._sanitize_filename(app_name)
        return self.data_dir / f"{safe_app_name}.md"

    def _sanitize_filename(self, filename: str) -> str:
        """
        ファイル名として安全な文字列に変換

        Args:
            filename: 元のファイル名

        Returns:
            安全なファイル名
        """
        # 使用可能な文字のみを抽出
        safe_chars = "".join(
            c for c in filename if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()

        # スペースをアンダースコアに置換
        safe_chars = safe_chars.replace(" ", "_")

        # 空文字列の場合のフォールバック
        if not safe_chars:
            safe_chars = "unknown_app"

        return safe_chars

    def create_memo_file(self, app_name: str, content: str | None = None) -> Path:
        """
        メモファイルを作成

        Args:
            app_name: アプリケーション名
            content: 初期コンテンツ（Noneの場合はデフォルトテンプレート）

        Returns:
            作成されたメモファイルのパス
        """
        memo_file = self.get_memo_file_path(app_name)

        if not memo_file.exists():
            try:
                if content is None:
                    content = self._create_default_content(app_name)

                with open(memo_file, "w", encoding="utf-8") as f:
                    f.write(content)

                logger.debug(f"メモファイルを作成しました: {memo_file}")
            except Exception as e:
                logger.error(f"メモファイル作成エラー: {e}")
                raise

        return memo_file

    def _create_default_content(self, app_name: str) -> str:
        """
        デフォルトのメモコンテンツを作成

        Args:
            app_name: アプリケーション名

        Returns:
            デフォルトコンテンツ
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        return f"""# {app_name} のメモ

ここにメモを記述してください。

## メモの使い方
- このファイルはMarkdown形式で記述できます
- 見出し、リスト、リンクなどが使用可能です
- 内容は自動保存されます

## 作成日時
{timestamp}
"""

    def read_memo_file(self, memo_file: Path) -> str:
        """
        メモファイルを読み込み

        Args:
            memo_file: メモファイルのパス

        Returns:
            ファイルの内容
        """
        try:
            if memo_file.exists():
                with open(memo_file, encoding="utf-8") as f:
                    return f.read()
            else:
                logger.warning(f"メモファイルが存在しません: {memo_file}")
                return ""
        except Exception as e:
            logger.error(f"メモファイル読み込みエラー: {e}")
            return f"# エラー\n\nメモファイルの読み込みに失敗しました。\nエラー: {e}"

    def save_memo_file(self, memo_file: Path, content: str) -> bool:
        """
        メモファイルを保存

        Args:
            memo_file: メモファイルのパス
            content: 保存する内容

        Returns:
            保存が成功したかどうか
        """
        try:
            # ディレクトリが存在しない場合は作成
            memo_file.parent.mkdir(parents=True, exist_ok=True)

            with open(memo_file, "w", encoding="utf-8") as f:
                f.write(content)

            logger.debug(f"メモファイルを保存しました: {memo_file}")
            return True

        except Exception as e:
            logger.error(f"メモファイル保存エラー: {e}")
            return False

    def list_memo_files(self) -> list[Path]:
        """
        すべてのメモファイルのリストを取得

        Returns:
            メモファイルのパスのリスト
        """
        try:
            if self.data_dir.exists():
                return list(self.data_dir.glob("*.md"))
            else:
                return []
        except Exception as e:
            logger.error(f"メモファイル一覧取得エラー: {e}")
            return []

    def get_app_name_from_file(self, memo_file: Path) -> str:
        """
        メモファイルのパスからアプリ名を取得

        Args:
            memo_file: メモファイルのパス

        Returns:
            アプリケーション名
        """
        return memo_file.stem.replace("_", " ")

    def update_data_dir(self, new_data_dir: str):
        """
        データディレクトリを更新

        Args:
            new_data_dir: 新しいデータディレクトリ
        """
        self.data_dir = Path(new_data_dir)
        self.ensure_data_dir()
        logger.info(f"データディレクトリを更新しました: {self.data_dir}")
