import logging
import time
from pathlib import Path

import yaml

logger = logging.getLogger("app_sticky_memo")


class MemoManager:
    """Memo file management class"""

    def __init__(self, data_dir: str):
        """
        Initialize MemoManager

        Args:
            data_dir: Directory for saving memo files
        """
        self.data_dir = Path(data_dir)
        self.mapping_file = self.data_dir / "mapping.yaml"
        self.mapping = {}
        self.ensure_data_dir()
        self.load_mapping()
        logger.debug(f"MemoManager initialized: {self.data_dir}")

    def ensure_data_dir(self) -> bool:
        """Create data directory"""
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Data directory creation error: {e}")
            return False

    def get_memo_file_path(self, exe_name: str) -> Path:
        """
        Generate memo file path from exe name

        Args:
            exe_name: Executable file name

        Returns:
            Path to memo file
        """
        memo_name = self.get_memo_name(exe_name)
        safe_memo_name = self._sanitize_filename(memo_name)
        return self.data_dir / f"{safe_memo_name}.md"

    def _sanitize_filename(self, filename: str) -> str:
        """
        Convert to safe filename string

        Args:
            filename: Original filename

        Returns:
            Safe filename
        """
        # Extract only usable characters
        safe_chars = "".join(
            c for c in filename if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()

        # Replace spaces with underscores
        safe_chars = safe_chars.replace(" ", "_")

        # Fallback for empty string
        if not safe_chars:
            safe_chars = "unknown_app"

        return safe_chars

    def create_memo_file(self, exe_name: str, content: str | None = None) -> Path:
        """
        Create memo file

        Args:
            exe_name: Executable file name
            content: Initial content (default template if None)

        Returns:
            Path to created memo file
        """
        memo_file = self.get_memo_file_path(exe_name)

        if not memo_file.exists():
            try:
                if content is None:
                    memo_name = self.get_memo_name(exe_name)
                    content = self._create_default_content(memo_name)

                with open(memo_file, "w", encoding="utf-8") as f:
                    f.write(content)

                logger.debug(f"Memo file created: {memo_file}")
            except Exception as e:
                logger.error(f"Memo file creation error: {e}")
                raise

        return memo_file

    def _create_default_content(self, app_name: str) -> str:
        """
        Create default memo content

        Args:
            app_name: Application name

        Returns:
            Default content
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        return f"""# Memo for {app_name}

Write your notes here.

## How to use this memo
- This file can be written in Markdown format
- You can use headings, lists, links, etc.
- Content is saved automatically

## Created at
{timestamp}
"""

    def read_memo_file(self, memo_file: Path) -> str:
        """
        Read memo file

        Args:
            memo_file: Path to memo file

        Returns:
            File content
        """
        try:
            if memo_file.exists():
                with open(memo_file, encoding="utf-8") as f:
                    return f.read()
            else:
                logger.warning(f"Memo file does not exist: {memo_file}")
                return ""
        except Exception as e:
            logger.error(f"Memo file read error: {e}")
            return f"# Error\n\nFailed to read memo file.\nError: {e}"

    def save_memo_file(self, memo_file: Path, content: str) -> bool:
        """
        Save memo file

        Args:
            memo_file: Path to memo file
            content: Content to save

        Returns:
            Whether save was successful
        """
        try:
            # Create directory if it doesn't exist
            memo_file.parent.mkdir(parents=True, exist_ok=True)

            with open(memo_file, "w", encoding="utf-8") as f:
                f.write(content)

            logger.debug(f"Memo file saved: {memo_file}")
            return True

        except Exception as e:
            logger.error(f"Memo file save error: {e}")
            return False

    def list_memo_files(self) -> list[Path]:
        """
        Get list of all memo files

        Returns:
            List of memo file paths
        """
        try:
            if self.data_dir.exists():
                return list(self.data_dir.glob("*.md"))
            else:
                return []
        except Exception as e:
            logger.error(f"Memo file list error: {e}")
            return []

    def get_app_name_from_file(self, memo_file: Path) -> str:
        """
        Get app name from memo file path

        Args:
            memo_file: Path to memo file

        Returns:
            Application name
        """
        return memo_file.stem.replace("_", " ")

    def update_data_dir(self, new_data_dir: str):
        """
        Update data directory

        Args:
            new_data_dir: New data directory
        """
        self.data_dir = Path(new_data_dir)
        self.mapping_file = self.data_dir / "mapping.yaml"
        self.ensure_data_dir()
        self.load_mapping()
        logger.info(f"Data directory updated: {self.data_dir}")

    def load_mapping(self):
        """Load mapping file"""
        try:
            if self.mapping_file.exists():
                with open(self.mapping_file, encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                    mappings_list = data.get("mappings", [])
                    # Convert from list format to dict format
                    self.mapping = {}
                    for item in mappings_list:
                        if (
                            isinstance(item, dict)
                            and "exe_name" in item
                            and "memo_name" in item
                        ):
                            self.mapping[item["exe_name"]] = item["memo_name"]
                logger.debug(f"Mapping loaded: {len(self.mapping)} items")
            else:
                self.mapping = {}
                logger.debug("Mapping file does not exist - starting empty")
        except Exception as e:
            logger.error(f"Mapping file load error: {e}")
            self.mapping = {}

    def save_mapping(self):
        """Save mapping file"""
        try:
            # Convert from dict format to list format
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
            logger.debug(f"Mapping file saved: {len(self.mapping)} items")
        except Exception as e:
            logger.error(f"Mapping file save error: {e}")

    def _remove_extension(self, filename: str) -> str:
        """
        Remove extension from filename

        Args:
            filename: Original filename

        Returns:
            Filename without extension
        """
        if filename.lower().endswith(".exe"):
            return filename[:-4]
        return filename

    def get_memo_name(self, exe_name: str) -> str:
        """
        Get memo name from exe name

        Args:
            exe_name: Executable file name

        Returns:
            Corresponding memo name
        """
        # Use existing mapping if available
        if exe_name in self.mapping:
            memo_name = self.mapping[exe_name]
            logger.debug(f"Using mapping: {exe_name} -> {memo_name}")
            return memo_name

        # Auto-create mapping if not found (removing extension)
        base_name = self._remove_extension(exe_name)
        self.mapping[exe_name] = base_name
        self.save_mapping()
        logger.debug(f"New mapping created: {exe_name} -> {base_name}")
        return base_name

    def update_mapping(self, exe_name: str, memo_name: str):
        """
        Update mapping

        Args:
            exe_name: Executable file name
            memo_name: Corresponding memo name
        """
        self.mapping[exe_name] = memo_name
        self.save_mapping()
        logger.info(f"Mapping updated: {exe_name} -> {memo_name}")

    def get_all_mappings(self) -> dict[str, str]:
        """Get all mappings"""
        return self.mapping.copy()
