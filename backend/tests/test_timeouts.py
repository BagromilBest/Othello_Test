"""Tests for bot initialization and move timeouts"""
import pytest
import time
from app.bot_manager import bot_manager
from app.websocket_handler import Match
from app.models import MatchConfig


class SlowInitBot:
    """A bot that takes time to initialize"""
    def __init__(self, my_color: int, opp_color: int, init_delay: float = 0):
        time.sleep(init_delay)
        self.my_color = my_color
        self.opp_color = opp_color

    def select_move(self, board):
        return (0, 0)


class SlowMoveBot:
    """A bot that takes time to make moves"""
    def __init__(self, my_color: int, opp_color: int):
        self.my_color = my_color
        self.opp_color = opp_color

    def select_move(self, board, move_delay: float = 0):
        time.sleep(move_delay)
        # Find a valid move
        for row in range(len(board)):
            for col in range(len(board[0])):
                if board[row][col] == -1:
                    return (row, col)
        return (0, 0)


def test_bot_initialization_success():
    """Test successful bot initialization with timing"""
    bot_instance, error, init_time_ms = bot_manager.initialize_bot(
        SlowInitBot, 0, 1, "test_bot", timeout=5.0
    )
    
    assert bot_instance is not None
    assert error is None
    assert init_time_ms is not None
    assert init_time_ms >= 0


def test_bot_initialization_timeout():
    """Test bot initialization timeout"""
    # Create a bot class that will timeout
    class TimeoutBot:
        def __init__(self, my_color, opp_color):
            time.sleep(2)  # Sleep for 2 seconds
    
    bot_instance, error, init_time_ms = bot_manager.initialize_bot(
        TimeoutBot, 0, 1, "timeout_bot", timeout=1.0
    )
    
    assert bot_instance is None
    assert error is not None
    assert "exceeded" in error.lower()
    assert "time limit" in error.lower()
    assert init_time_ms is None


def test_bot_move_with_custom_timeout():
    """Test bot move execution with custom timeout"""
    bot = SlowMoveBot(0, 1)
    board = [[-1, -1], [-1, -1]]
    
    move, error, exec_time_ms = bot_manager.execute_bot_move(
        bot, board, "test_bot", timeout=2.0
    )
    
    assert move is not None
    assert error is None
    assert exec_time_ms is not None
    assert exec_time_ms >= 0


def test_bot_move_timeout():
    """Test bot move timeout - bot should finish within 4x timeout and return move with error (bot loses)"""
    class TimeoutMoveBot:
        def __init__(self, my_color, opp_color):
            self.my_color = my_color
            self.opp_color = opp_color
        
        def select_move(self, board):
            time.sleep(2)  # Sleep for 2 seconds
            return (0, 0)
    
    bot = TimeoutMoveBot(0, 1)
    board = [[-1, -1], [-1, -1]]
    
    move, error, exec_time_ms = bot_manager.execute_bot_move(
        bot, board, "timeout_bot", timeout=1.0
    )
    
    # Bot should complete within 4x timeout (4 seconds), so it should return a move
    assert move is not None
    assert error is not None  # But there should be an error message (bot lost)
    assert "lost:" in error.lower() and "time limit" in error.lower()
    assert exec_time_ms is not None  # And we should have execution time
    assert exec_time_ms >= 2000  # At least 2 seconds (2000ms)


def test_bot_move_hard_timeout():
    """Test bot move exceeds maximum timeout (4x limit)"""
    class VerySlowBot:
        def __init__(self, my_color, opp_color):
            self.my_color = my_color
            self.opp_color = opp_color
        
        def select_move(self, board):
            time.sleep(10)  # Sleep for 10 seconds (way over 4x timeout)
            return (0, 0)
    
    bot = VerySlowBot(0, 1)
    board = [[-1, -1], [-1, -1]]
    
    move, error, exec_time_ms = bot_manager.execute_bot_move(
        bot, board, "very_slow_bot", timeout=1.0
    )
    
    # Bot should be terminated after 4x timeout (4 seconds)
    assert move is None
    assert error is not None
    assert "maximum time limit" in error.lower()
    assert exec_time_ms is None


def test_match_with_custom_timeouts():
    """Test match creation with custom timeout values"""
    config = MatchConfig(
        board_size=8,
        black_player_type="human",
        white_player_type="human",
        init_timeout=30.0,
        move_timeout=2.0
    )
    
    match = Match(config)
    
    assert match.config.init_timeout == 30.0
    assert match.config.move_timeout == 2.0


def test_match_default_timeouts():
    """Test match creation with default timeout values"""
    config = MatchConfig(
        board_size=8,
        black_player_type="human",
        white_player_type="human"
    )
    
    match = Match(config)
    
    assert match.config.init_timeout == 60.0  # Default
    assert match.config.move_timeout == 1.0  # Default


def test_initialization_time_tracking():
    """Test that initialization time is tracked"""
    config = MatchConfig(
        board_size=8,
        black_player_type="bot",
        black_bot_name="random_player",
        white_player_type="human",
        init_timeout=60.0,
        move_timeout=1.0
    )
    
    match = Match(config)
    state = match.get_state()
    
    # Black bot should have initialization time
    assert state.black_init_time_ms is not None
    assert state.black_init_time_ms >= 0
    
    # White is human, should not have init time
    assert state.white_init_time_ms is None
