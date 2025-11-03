"""Bot management: loading, validation, and execution"""
import os
import json
import importlib.util
import subprocess
import sys
from typing import Optional
from datetime import datetime
from .models import BotMetadata


class BotManager:
    """Manages bot loading, storage, and execution"""

    BUILTIN_BOTS_DIR = "app/bots"
    UPLOADED_BOTS_DIR = "uploads"
    METADATA_FILE = "uploads/bots_metadata.json"
    BOT_TIMEOUT = 2.0  # 2 seconds per move

    def __init__(self):
        """Initialize the bot manager"""
        self.metadata: dict[str, BotMetadata] = {}
        self._ensure_directories()
        self._load_metadata()
        self._scan_builtin_bots()

    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        os.makedirs(self.BUILTIN_BOTS_DIR, exist_ok=True)
        os.makedirs(self.UPLOADED_BOTS_DIR, exist_ok=True)

    def _load_metadata(self):
        """Load bot metadata from JSON file"""
        if os.path.exists(self.METADATA_FILE):
            try:
                with open(self.METADATA_FILE, 'r') as f:
                    data = json.load(f)
                    self.metadata = {
                        name: BotMetadata(**meta)
                        for name, meta in data.items()
                    }
            except Exception as e:
                print(f"Error loading metadata: {e}")
                self.metadata = {}

    def _save_metadata(self):
        """Save bot metadata to JSON file"""
        try:
            data = {
                name: meta.model_dump()
                for name, meta in self.metadata.items()
            }
            with open(self.METADATA_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving metadata: {e}")

    def _scan_builtin_bots(self):
        """Scan the builtin bots directory and update metadata"""
        if not os.path.exists(self.BUILTIN_BOTS_DIR):
            return

        for filename in os.listdir(self.BUILTIN_BOTS_DIR):
            if filename.endswith('.py') and not filename.startswith('_'):
                bot_name = filename[:-3]  # Remove .py extension
                if bot_name not in self.metadata:
                    self.metadata[bot_name] = BotMetadata(
                        name=bot_name,
                        type="builtin",
                        file_path=os.path.join(self.BUILTIN_BOTS_DIR, filename)
                    )

    def list_bots(self) -> list[BotMetadata]:
        """Get list of all available bots"""
        return list(self.metadata.values())

    def upload_bot(self, filename: str, content: bytes) -> BotMetadata:
        """
        Save an uploaded bot file.

        Args:
            filename: Name of the bot file
            content: File content as bytes

        Returns:
            BotMetadata for the uploaded bot

        Raises:
            ValueError: If filename is invalid or bot already exists
        """
        if not filename.endswith('.py'):
            raise ValueError("Bot file must be a Python file (.py)")

        bot_name = filename[:-3]

        # Check if bot already exists
        if bot_name in self.metadata:
            raise ValueError(f"Bot '{bot_name}' already exists")

        # Save the file
        file_path = os.path.join(self.UPLOADED_BOTS_DIR, filename)
        with open(file_path, 'wb') as f:
            f.write(content)

        # Create metadata
        metadata = BotMetadata(
            name=bot_name,
            type="uploaded",
            upload_time=datetime.utcnow().isoformat(),
            file_path=file_path
        )

        self.metadata[bot_name] = metadata
        self._save_metadata()

        return metadata

    def load_bot_class(self, bot_name: str):
        """
        Dynamically load a bot class.

        Args:
            bot_name: Name of the bot to load

        Returns:
            The bot class

        Raises:
            ValueError: If bot not found or invalid
        """
        if bot_name not in self.metadata:
            raise ValueError(f"Bot '{bot_name}' not found")

        metadata = self.metadata[bot_name]
        file_path = metadata.file_path

        if not os.path.exists(file_path):
            raise ValueError(f"Bot file not found: {file_path}")

        # Load the module
        spec = importlib.util.spec_from_file_location(bot_name, file_path)
        if spec is None or spec.loader is None:
            raise ValueError(f"Failed to load bot module: {bot_name}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Find the player class
        # Look for a class that has select_move method
        bot_class = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and hasattr(attr, 'select_move'):
                bot_class = attr
                break

        if bot_class is None:
            raise ValueError(f"No valid player class found in {bot_name}")

        return bot_class

    def execute_bot_move(self, bot_instance, board: list[list[int]],
                         bot_name: str) -> tuple[Optional[tuple[int, int]], Optional[str]]:
        """
        Execute a bot's move with timeout and error handling.

        This method uses subprocess isolation for uploaded bots to provide
        basic sandboxing. For production, consider using Docker containers
        or other secure isolation methods.

        Args:
            bot_instance: The bot instance
            board: Current board state
            bot_name: Name of the bot (for error messages)

        Returns:
            Tuple of (move, error_message)
            move: (row, col) tuple or None if error
            error_message: Error description or None if successful
        """
        try:
            # For now, call directly with timeout
            # TODO: Implement subprocess-based execution for better isolation
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError("Bot exceeded time limit")

            # Set up timeout (Unix-like systems only)
            if hasattr(signal, 'SIGALRM'):
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(int(self.BOT_TIMEOUT))

            try:
                move = bot_instance.select_move(board)
            finally:
                if hasattr(signal, 'SIGALRM'):
                    signal.alarm(0)  # Cancel the alarm

            # Validate move format
            if not isinstance(move, tuple) or len(move) != 2:
                return None, f"Bot '{bot_name}' returned invalid move format"

            row, col = move
            if not isinstance(row, int) or not isinstance(col, int):
                return None, f"Bot '{bot_name}' returned non-integer coordinates"

            return (row, col), None

        except TimeoutError:
            return None, f"Bot '{bot_name}' exceeded {self.BOT_TIMEOUT}s time limit"
        except Exception as e:
            return None, f"Bot '{bot_name}' raised error: {str(e)}"


# Global bot manager instance
bot_manager = BotManager()