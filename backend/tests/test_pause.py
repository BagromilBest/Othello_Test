"""Tests for game pause functionality"""
import pytest
from app.models import MatchConfig
from app.websocket_handler import Match


def test_pause_toggle():
    """Test that pause can be toggled on and off"""
    config = MatchConfig(
        board_size=8,
        black_player_type="human",
        white_player_type="human"
    )
    match = Match(config)
    
    # Initially not paused
    assert match.paused is False
    
    # Toggle pause on
    result = match.toggle_pause()
    assert result is True
    assert match.paused is True
    
    # Toggle pause off
    result = match.toggle_pause()
    assert result is False
    assert match.paused is False


def test_cannot_pause_finished_game():
    """Test that finished games cannot be paused"""
    config = MatchConfig(
        board_size=8,
        black_player_type="human",
        white_player_type="human"
    )
    match = Match(config)
    
    # Simulate game over
    match.game_over = True
    match.winner = 0
    
    # Try to toggle pause
    initial_pause_state = match.paused
    result = match.toggle_pause()
    
    # Pause state should not change
    assert result == initial_pause_state
    assert match.paused == initial_pause_state


def test_pause_state_in_game_state():
    """Test that pause state is included in game state"""
    config = MatchConfig(
        board_size=8,
        black_player_type="human",
        white_player_type="human"
    )
    match = Match(config)
    
    # Get initial state
    state = match.get_state()
    assert state.paused is False
    
    # Pause the game
    match.toggle_pause()
    
    # Get state again
    state = match.get_state()
    assert state.paused is True


def test_pause_with_bot_match():
    """Test pause functionality with bot players"""
    config = MatchConfig(
        board_size=8,
        black_player_type="bot",
        black_bot_name="random_player",
        white_player_type="bot",
        white_bot_name="random_player"
    )
    match = Match(config)
    
    # Should be able to pause bot matches
    assert match.paused is False
    match.toggle_pause()
    assert match.paused is True


def test_pause_does_not_affect_board_state():
    """Test that pausing does not change the board state"""
    config = MatchConfig(
        board_size=8,
        black_player_type="human",
        white_player_type="human"
    )
    match = Match(config)
    
    # Get initial board state
    initial_state = match.get_state()
    initial_board = initial_state.board
    initial_black_count = initial_state.black_count
    initial_white_count = initial_state.white_count
    
    # Pause the game
    match.toggle_pause()
    
    # Get state after pause
    paused_state = match.get_state()
    
    # Board should be unchanged
    assert paused_state.board == initial_board
    assert paused_state.black_count == initial_black_count
    assert paused_state.white_count == initial_white_count


def test_pause_persists_across_state_queries():
    """Test that pause state persists across multiple state queries"""
    config = MatchConfig(
        board_size=8,
        black_player_type="human",
        white_player_type="human"
    )
    match = Match(config)
    
    # Pause the game
    match.toggle_pause()
    
    # Query state multiple times
    for _ in range(5):
        state = match.get_state()
        assert state.paused is True
    
    # Unpause
    match.toggle_pause()
    
    # Query state again
    for _ in range(5):
        state = match.get_state()
        assert state.paused is False


def test_multiple_pause_toggles():
    """Test multiple consecutive pause toggles"""
    config = MatchConfig(
        board_size=8,
        black_player_type="human",
        white_player_type="human"
    )
    match = Match(config)
    
    # Toggle multiple times
    assert match.paused is False
    
    match.toggle_pause()
    assert match.paused is True
    
    match.toggle_pause()
    assert match.paused is False
    
    match.toggle_pause()
    assert match.paused is True
    
    match.toggle_pause()
    assert match.paused is False
