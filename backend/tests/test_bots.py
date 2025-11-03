"""Tests for bot management and validation"""
import pytest
import os
import tempfile
from app.bot_manager import BotManager
from app.game.board import Board

# Sample valid bot code
VALID_BOT_CODE = '''
class TestBot:
    def __init__(self, my_color: int, opp_color: int):
        self.my_color = my_color
        self.opp_color = opp_color

    def select_move(self, board):
        # Return first empty position
        n = len(board)
        for i in range(n):
            for j in range(n):
                if board[i][j] == -1:
                    return (i, j)
        return (0, 0)
'''

# Sample invalid bot code (missing select_move)
INVALID_BOT_CODE = '''
class TestBot:
    def __init__(self, my_color: int, opp_color: int):
        self.my_color = my_color
        self.opp_color = opp_color
'''


def test_bot_manager_initialization():
    """Test bot manager initialization"""
    manager = BotManager()
    assert manager is not None
    assert isinstance(manager.metadata, dict)


def test_upload_valid_bot():
    """Test uploading a valid bot"""
    manager = BotManager()

    # Upload a bot
    metadata = manager.upload_bot("test_bot.py", VALID_BOT_CODE.encode())

    assert metadata.name == "test_bot"
    assert metadata.type == "uploaded"
    assert metadata.upload_time is not None

    # Clean up
    if os.path.exists(metadata.file_path):
        os.remove(metadata.file_path)


def test_upload_duplicate_bot():
    """Test that uploading duplicate bot raises error"""
    manager = BotManager()

    # Upload first time
    metadata = manager.upload_bot("dup_bot.py", VALID_BOT_CODE.encode())

    # Try to upload again
    with pytest.raises(ValueError, match="already exists"):
        manager.upload_bot("dup_bot.py", VALID_BOT_CODE.encode())

    # Clean up
    if os.path.exists(metadata.file_path):
        os.remove(metadata.file_path)


def test_upload_invalid_extension():
    """Test that non-Python files are rejected"""
    manager = BotManager()

    with pytest.raises(ValueError, match="must be a Python file"):
        manager.upload_bot("test.txt", b"some content")


def test_load_bot_class():
    """Test loading a bot class"""
    manager = BotManager()

    # Upload and load a bot
    metadata = manager.upload_bot("loadable_bot.py", VALID_BOT_CODE.encode())
    bot_class = manager.load_bot_class("loadable_bot")

    assert bot_class is not None

    # Instantiate the bot
    bot_instance = bot_class(Board.BLACK, Board.WHITE)
    assert hasattr(bot_instance, 'select_move')

    # Clean up
    if os.path.exists(metadata.file_path):
        os.remove(metadata.file_path)


def test_load_nonexistent_bot():
    """Test loading a bot that doesn't exist"""
    manager = BotManager()

    with pytest.raises(ValueError, match="not found"):
        manager.load_bot_class("nonexistent_bot")


def test_bot_move_execution():
    """Test executing a bot move"""
    manager = BotManager()

    # Upload a simple bot
    metadata = manager.upload_bot("exec_bot.py", VALID_BOT_CODE.encode())
    bot_class = manager.load_bot_class("exec_bot")
    bot_instance = bot_class(Board.BLACK, Board.WHITE)

    # Create a simple board
    board = [[-1, -1], [-1, -1]]

    # Execute move
    move, error = manager.execute_bot_move(bot_instance, board, "exec_bot")

    assert error is None
    assert move is not None
    assert len(move) == 2

    # Clean up
    if os.path.exists(metadata.file_path):
        os.remove(metadata.file_path)


def test_bot_invalid_move_format():
    """Test bot returning invalid move format"""
    # Bot that returns invalid format
    bad_bot_code = '''
class BadBot:
    def __init__(self, my_color: int, opp_color: int):
        pass

    def select_move(self, board):
        return "invalid"  # Should return tuple
'''

    manager = BotManager()
    metadata = manager.upload_bot("bad_bot.py", bad_bot_code.encode())
    bot_class = manager.load_bot_class("bad_bot")
    bot_instance = bot_class(Board.BLACK, Board.WHITE)

    board = [[-1, -1], [-1, -1]]
    move, error = manager.execute_bot_move(bot_instance, board, "bad_bot")

    assert move is None
    assert error is not None
    assert "invalid move format" in error.lower()

    # Clean up
    if os.path.exists(metadata.file_path):
        os.remove(metadata.file_path)