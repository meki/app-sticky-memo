import logging
import time
from pathlib import Path

import yaml

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
        self.mapping_file = self.data_dir / "mapping.yaml"
        self.mapping = {}
        self.ensure_data_dir()
        self.load_mapping()
        logger.debug(f"MemoManagerを初期化しました: {self.data_dir}")

    def ensure_data_dir(self) -> bool:
        """データディレクトリを作成"""
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"データディレクトリ作成エラー: {e}")
            return False

    def get_memo_file_path(self, exe_name: str) -> Path:
        """
        exe名からメモファイルのパスを生成

        Args:
            exe_name: 実行可能ファイル名

        Returns:
            メモファイルのパス
        """
        memo_name = self.get_memo_name(exe_name)
        safe_memo_name = self._sanitize_filename(memo_name)
        return self.data_dir / f"{safe_memo_name}.md"

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

    def create_memo_file(self, exe_name: str, content: str | None = None) -> Path:
        """
        メモファイルを作成

        Args:
            exe_name: 実行可能ファイル名
            content: 初期コンテンツ（Noneの場合はデフォルトテンプレート）

        Returns:
            作成されたメモファイルのパス
        """
        memo_file = self.get_memo_file_path(exe_name)

        if not memo_file.exists():
            try:
                if content is None:
                    memo_name = self.get_memo_name(exe_name)
                    content = self._create_default_content(memo_name)

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
        self.mapping_file = self.data_dir / "mapping.yaml"
        self.ensure_data_dir()
        self.load_mapping()
        logger.info(f"データディレクトリを更新しました: {self.data_dir}")

    def load_mapping(self):
        """マッピングファイルを読み込み"""
        try:
            if self.mapping_file.exists():
                with open(self.mapping_file, encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                    mappings_list = data.get("mappings", [])
                    # リスト形式から辞書形式に変換
                    self.mapping = {}
                    for item in mappings_list:
                        if (
                            isinstance(item, dict)
                            and "exe_name" in item
                            and "memo_name" in item
                        ):
                            self.mapping[item["exe_name"]] = item["memo_name"]
                logger.debug(f"マッピング読み込み完了: {len(self.mapping)} 項目")
            else:
                self.mapping = {}
                logger.debug("マッピングファイルが存在しません - 空で開始")
        except Exception as e:
            logger.error(f"マッピングファイル読み込みエラー: {e}")
            self.mapping = {}

    def save_mapping(self):
        """マッピングファイルを保存"""
        try:
            # 辞書形式からリスト形式に変換
            mappings_list = []
            for exe_name, memo_name in self.mapping.items():
                mappings_list.append({"exe_name": exe_name, "memo_name": memo_name})

            data = {
                "version": "1.0",
                "description": "Mapping between exe names and memo names",
                "mappings": mappings_list,
            }
            with open(self.mapping_file, "w", encoding="utf-8") as f:
                yaml.dump(
                    data,
                    f,
                    allow_unicode=True,
                    default_flow_style=False,
                    indent=2,
                    sort_keys=False,
                )
            logger.debug(f"マッピングファイルを保存しました: {len(self.mapping)} 項目")
        except Exception as e:
            logger.error(f"マッピングファイル保存エラー: {e}")

    def get_memo_name(self, exe_name: str) -> str:
        """
        exe名からmemo名を取得

        Args:
            exe_name: 実行可能ファイル名

        Returns:
            対応するmemo名
        """
        # マッピングに存在する場合はそれを使用
        if exe_name in self.mapping:
            memo_name = self.mapping[exe_name]
            logger.debug(f"マッピング使用: {exe_name} -> {memo_name}")
            return memo_name

        # マッピングに存在しない場合は自動作成
        self.mapping[exe_name] = exe_name
        self.save_mapping()
        logger.debug(f"新しいマッピング作成: {exe_name} -> {exe_name}")
        return exe_name

    def update_mapping(self, exe_name: str, memo_name: str):
        """
        マッピングを更新

        Args:
            exe_name: 実行可能ファイル名
            memo_name: 対応するmemo名
        """
        self.mapping[exe_name] = memo_name
        self.save_mapping()
        logger.info(f"マッピングを更新しました: {exe_name} -> {memo_name}")

    def get_all_mappings(self) -> dict[str, str]:
        """全てのマッピングを取得"""
        return self.mapping.copy()
