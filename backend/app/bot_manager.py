"""Bot management: loading, validation, and execution"""
import os
import json
import importlib.util
import subprocess
import sys
import time
from typing import Optional, Tuple, List
from datetime import datetime, UTC
from .models import BotMetadata
from .bot_security import security_validator, security_logger, SecurityViolation


class BotManager:
    """Manages bot loading, storage, and execution"""

    BUILTIN_BOTS_DIR = "app/bots"
    UPLOADED_BOTS_DIR = "uploads"
    METADATA_FILE = "uploads/bots_metadata.json"
    DEFAULT_MOVE_TIMEOUT = 1.0  # 1 second per move (changed from 2.0)
    DEFAULT_INIT_TIMEOUT = 60.0  # 60 seconds for initialization

    def __init__(self):
        """Initialize the bot manager"""
        self.metadata: dict[str, BotMetadata] = {}
        self._ensure_directories()
        self._load_metadata()
        self._cleanup_stale_metadata()
        self._scan_builtin_bots()
        self._scan_uploaded_bots()

    def _cleanup_stale_metadata(self):
        """Remove metadata entries for bots whose files no longer exist"""
        stale_bots = []
        for bot_name, metadata in self.metadata.items():
            if not os.path.exists(metadata.file_path):
                stale_bots.append(bot_name)
        
        for bot_name in stale_bots:
            del self.metadata[bot_name]
        
        # Save if we removed any stale entries
        if stale_bots:
            self._save_metadata()

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

    def _scan_uploaded_bots(self):
        """
        Scan the uploads directory for bot files without metadata.
        
        This handles two scenarios:
        1. Bot files manually placed in uploads directory (not uploaded via API)
        2. Bot files whose metadata was lost (e.g., metadata file was deleted/corrupted)
        
        In both cases, we treat them as 'uploaded' type bots, which can be deleted.
        The stale metadata cleanup runs before this, so if a bot file exists here
        without metadata, it's either new or recovered from metadata loss.
        """
        if not os.path.exists(self.UPLOADED_BOTS_DIR):
            return

        for filename in os.listdir(self.UPLOADED_BOTS_DIR):
            if filename.endswith('.py') and not filename.startswith('_'):
                bot_name = filename[:-3]  # Remove .py extension
                if bot_name not in self.metadata:
                    # Bot file exists but has no metadata - treat as uploaded
                    self.metadata[bot_name] = BotMetadata(
                        name=bot_name,
                        type="uploaded",
                        file_path=os.path.join(self.UPLOADED_BOTS_DIR, filename)
                    )

    def list_bots(self) -> list[BotMetadata]:
        """Get list of all available bots"""
        return list(self.metadata.values())

    def upload_bot(self, filename: str, content: bytes, request_info: Optional[dict] = None) -> BotMetadata:
        """
        Save an uploaded bot file with security validation.

        Args:
            filename: Name of the bot file
            content: File content as bytes
            request_info: Optional request information for security logging (IP, user agent, etc.)

        Returns:
            BotMetadata for the uploaded bot

        Raises:
            ValueError: If filename is invalid, bot already exists, or security validation fails
        """
        if not filename.endswith('.py'):
            raise ValueError("Bot file must be a Python file (.py)")

        bot_name = filename[:-3]

        # Check if bot already exists
        if bot_name in self.metadata:
            raise ValueError(f"Bot '{bot_name}' already exists")

        # Security validation: decode content and validate code
        # Use 'utf-8-sig' to automatically handle BOM (Byte Order Mark) if present
        try:
            code_str = content.decode('utf-8-sig')
        except UnicodeDecodeError:
            raise ValueError("Bot file must be valid UTF-8 encoded text")
        
        # Validate the code for security issues
        is_valid, violations = security_validator.validate(code_str, filename)
        
        if not is_valid:
            # Log security event and quarantine the file
            if request_info is None:
                request_info = {}
            
            security_logger.log_security_event(
                filename=filename,
                violations=violations,
                request_info=request_info,
                file_content=content
            )
            
            # Build detailed error message
            error_parts = ["Security validation failed. The following issues were found:"]
            for i, violation in enumerate(violations, 1):
                error_parts.append(f"\n{i}. {violation.description}")
                if violation.line_number:
                    error_parts.append(f"   Line {violation.line_number}: {violation.code_snippet}")
            
            raise ValueError('\n'.join(error_parts))

        # Save the file
        file_path = os.path.join(self.UPLOADED_BOTS_DIR, filename)
        with open(file_path, 'wb') as f:
            f.write(content)

        # Create metadata
        metadata = BotMetadata(
            name=bot_name,
            type="uploaded",
            upload_time=datetime.now(UTC).isoformat(),
            file_path=file_path
        )

        self.metadata[bot_name] = metadata
        self._save_metadata()

        return metadata

    def delete_bot(self, bot_name: str) -> None:
        """
        Delete a bot.

        Args:
            bot_name: Name of the bot to delete

        Raises:
            ValueError: If bot not found or is builtin
        """
        if bot_name not in self.metadata:
            raise ValueError(f"Bot '{bot_name}' not found")

        metadata = self.metadata[bot_name]

        # Cannot delete builtin bots
        if metadata.type == "builtin":
            raise ValueError(f"Cannot delete builtin bot '{bot_name}'")

        # Delete the file
        if os.path.exists(metadata.file_path):
            os.remove(metadata.file_path)

        # Remove from metadata
        del self.metadata[bot_name]
        self._save_metadata()

    def rename_bot(self, old_name: str, new_name: str) -> BotMetadata:
        """
        Rename a bot.

        Args:
            old_name: Current bot name
            new_name: New bot name

        Returns:
            Updated BotMetadata

        Raises:
            ValueError: If bot not found, is builtin, or new name already exists
        """
        if old_name not in self.metadata:
            raise ValueError(f"Bot '{old_name}' not found")

        # Trim and validate new name
        new_name = new_name.strip()
        if not new_name:
            raise ValueError("New bot name cannot be empty")

        # Prevent path traversal attacks
        if '/' in new_name or '\\' in new_name or '..' in new_name:
            raise ValueError("Bot name cannot contain path separators or '..'")

        if new_name in self.metadata:
            raise ValueError(f"Bot '{new_name}' already exists")

        metadata = self.metadata[old_name]

        # Cannot rename builtin bots
        if metadata.type == "builtin":
            raise ValueError(f"Cannot rename builtin bot '{old_name}'")

        # Rename the file
        old_path = metadata.file_path
        new_filename = f"{new_name}.py"
        new_path = os.path.join(self.UPLOADED_BOTS_DIR, new_filename)

        # Ensure the new path is within the uploads directory (security check)
        new_path_absolute = os.path.abspath(new_path)
        uploads_dir_absolute = os.path.abspath(self.UPLOADED_BOTS_DIR)
        if not new_path_absolute.startswith(uploads_dir_absolute + os.sep):
            raise ValueError("Invalid bot name: path traversal detected")

        if os.path.exists(old_path):
            os.rename(old_path, new_path)

        # Update metadata
        metadata.name = new_name
        metadata.file_path = new_path

        # Move in metadata dict
        del self.metadata[old_name]
        self.metadata[new_name] = metadata
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

    def initialize_bot(self, bot_class, my_color: int, opp_color: int, 
                       bot_name: str, timeout: float = None) -> tuple[Optional[object], Optional[str], Optional[float]]:
        """
        Initialize a bot instance with timeout.

        Args:
            bot_class: The bot class to instantiate
            my_color: The bot's color (0 or 1)
            opp_color: The opponent's color (0 or 1)
            bot_name: Name of the bot (for error messages)
            timeout: Timeout in seconds (defaults to DEFAULT_INIT_TIMEOUT)

        Returns:
            Tuple of (bot_instance, error_message, init_time_ms)
            bot_instance: The initialized bot or None if error
            error_message: Error description or None if successful
            init_time_ms: Time taken to initialize in milliseconds or None if error
        """
        if timeout is None:
            timeout = self.DEFAULT_INIT_TIMEOUT

        try:
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError("Bot initialization exceeded time limit")

            # Set up timeout (Unix-like systems only)
            if hasattr(signal, 'SIGALRM'):
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(int(timeout))

            try:
                start_time = time.perf_counter()
                bot_instance = bot_class(my_color, opp_color)
                end_time = time.perf_counter()
                init_time_ms = (end_time - start_time) * 1000  # Convert to milliseconds
            finally:
                if hasattr(signal, 'SIGALRM'):
                    signal.alarm(0)  # Cancel the alarm

            return bot_instance, None, init_time_ms

        except TimeoutError:
            return None, f"Bot '{bot_name}' initialization exceeded {timeout}s time limit", None
        except Exception as e:
            return None, f"Bot '{bot_name}' raised error during initialization: {str(e)}", None

    def execute_bot_move(self, bot_instance, board: list[list[int]],
                         bot_name: str, timeout: float = None) -> tuple[Optional[tuple[int, int]], Optional[str], Optional[float]]:
        """
        Execute a bot's move with timeout and error handling.

        This method uses subprocess isolation for uploaded bots to provide
        basic sandboxing. For production, consider using Docker containers
        or other secure isolation methods.

        Args:
            bot_instance: The bot instance
            board: Current board state
            bot_name: Name of the bot (for error messages)
            timeout: Timeout in seconds (defaults to DEFAULT_MOVE_TIMEOUT)

        Returns:
            Tuple of (move, error_message, execution_time_ms)
            move: (row, col) tuple or None if error
            error_message: Error description or None if successful
            execution_time_ms: Time taken to execute select_move in milliseconds or None if error
        """
        if timeout is None:
            timeout = self.DEFAULT_MOVE_TIMEOUT

        try:
            # For now, call directly with timeout
            # TODO: Implement subprocess-based execution for better isolation
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError("Bot exceeded time limit")

            # Set up timeout (Unix-like systems only)
            if hasattr(signal, 'SIGALRM'):
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(int(timeout))

            try:
                start_time = time.perf_counter()
                move = bot_instance.select_move(board)
                end_time = time.perf_counter()
                execution_time_ms = (end_time - start_time) * 1000  # Convert to milliseconds
            finally:
                if hasattr(signal, 'SIGALRM'):
                    signal.alarm(0)  # Cancel the alarm

            # Validate move format
            if not isinstance(move, tuple) or len(move) != 2:
                return None, f"Bot '{bot_name}' returned invalid move format", None

            row, col = move
            if not isinstance(row, int) or not isinstance(col, int):
                return None, f"Bot '{bot_name}' returned non-integer coordinates", None

            return (row, col), None, execution_time_ms

        except TimeoutError:
            return None, f"Bot '{bot_name}' exceeded {timeout}s time limit", None
        except Exception as e:
            return None, f"Bot '{bot_name}' raised error: {str(e)}", None


# Global bot manager instance
bot_manager = BotManager()