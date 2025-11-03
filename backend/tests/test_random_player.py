"""Tests for the random_player bot"""
import pytest
from app.bot_manager import BotManager
from app.game.board import Board


def test_random_player_available():
    """Test that random_player bot is available in the bot manager"""
    manager = BotManager()
    bots = manager.list_bots()
    
    # Find random_player in the list
    random_player = next((bot for bot in bots if bot.name == "random_player"), None)
    
    assert random_player is not None, "random_player bot should be available"
    assert random_player.type == "builtin", "random_player should be a builtin bot"
    assert random_player.file_path == "app/bots/random_player.py"


def test_random_player_can_be_loaded():
    """Test that random_player bot can be loaded"""
    manager = BotManager()
    bot_class = manager.load_bot_class("random_player")
    
    assert bot_class is not None
    assert bot_class.__name__ == "RandomPlayer"
    assert hasattr(bot_class, 'select_move')


def test_random_player_makes_moves():
    """Test that random_player can make valid moves"""
    manager = BotManager()
    bot_class = manager.load_bot_class("random_player")
    
    # Create bot instance for black player
    bot = bot_class(Board.BLACK, Board.WHITE)
    
    # Create initial board
    board = Board(8)
    board_state = board.get_board()
    
    # Execute move
    move, error = manager.execute_bot_move(bot, board_state, "random_player")
    
    assert error is None, f"Bot should not error: {error}"
    assert move is not None
    assert isinstance(move, tuple)
    assert len(move) == 2
    assert isinstance(move[0], int)
    assert isinstance(move[1], int)


def test_random_player_interface():
    """Test that random_player has the correct interface"""
    manager = BotManager()
    bot_class = manager.load_bot_class("random_player")
    
    # Create bot instance
    bot = bot_class(0, 1)
    
    # Check required attributes
    assert hasattr(bot, 'my_color')
    assert hasattr(bot, 'opp_color')
    assert hasattr(bot, 'select_move')
    
    # Check attributes have correct values
    assert bot.my_color == 0
    assert bot.opp_color == 1
