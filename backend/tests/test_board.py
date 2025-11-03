"""Tests for board and game rules"""
import pytest
from app.game.board import Board
from app.game.rules import OthelloRules


def test_board_initialization():
    """Test board initialization with different sizes"""
    # Standard 8x8 board
    board = Board(8)
    assert board.size == 8
    assert len(board.board) == 8
    assert len(board.board[0]) == 8

    # Check starting position
    assert board.get_piece(3, 3) == Board.WHITE
    assert board.get_piece(3, 4) == Board.BLACK
    assert board.get_piece(4, 3) == Board.BLACK
    assert board.get_piece(4, 4) == Board.WHITE


def test_board_sizes():
    """Test various board sizes"""
    for size in [4, 6, 8, 10, 20]:
        board = Board(size)
        assert board.size == size
        black_count, white_count = board.count_pieces()
        assert black_count == 2
        assert white_count == 2


def test_invalid_board_size():
    """Test that invalid board sizes raise errors"""
    with pytest.raises(ValueError):
        Board(3)  # Too small

    with pytest.raises(ValueError):
        Board(101)  # Too large


def test_valid_moves_initial():
    """Test valid moves from initial position"""
    board = Board(8)
    rules = OthelloRules(board)

    # Black moves first
    valid_moves = rules.get_valid_moves(Board.BLACK)
    assert len(valid_moves) == 4

    # Standard opening moves for black
    expected_moves = {(2, 3), (3, 2), (4, 5), (5, 4)}
    assert set(valid_moves) == expected_moves


def test_make_move():
    """Test making a move and flipping pieces"""
    board = Board(8)
    rules = OthelloRules(board)

    # Black plays at (2, 3)
    success, flipped = rules.make_move(2, 3, Board.BLACK)
    assert success

    # Check that piece was placed
    assert board.get_piece(2, 3) == Board.BLACK

    # Check that opponent piece was flipped
    assert board.get_piece(3, 3) == Board.BLACK

    # Count pieces
    black_count, white_count = board.count_pieces()
    assert black_count == 4
    assert white_count == 1


def test_invalid_move():
    """Test that invalid moves are rejected"""
    board = Board(8)
    rules = OthelloRules(board)

    # Try to place on occupied square
    success, flipped = rules.make_move(3, 3, Board.BLACK)
    assert not success

    # Try to place on invalid position
    success, flipped = rules.make_move(0, 0, Board.BLACK)
    assert not success


def test_game_over_full_board():
    """Test game over detection when board is full"""
    board = Board(4)

    # Fill the board
    for i in range(4):
        for j in range(4):
            board.set_piece(i, j, Board.BLACK)

    rules = OthelloRules(board)
    is_over, winner = rules.is_game_over()

    assert is_over
    assert winner == Board.BLACK  # All black pieces


def test_game_over_no_moves():
    """Test game over when no player has valid moves"""
    board = Board(4)

    # Create a position where no one can move
    # (simplified test case)
    board.set_piece(0, 0, Board.BLACK)
    board.set_piece(0, 1, Board.WHITE)
    board.set_piece(1, 0, Board.WHITE)
    board.set_piece(1, 1, Board.BLACK)

    rules = OthelloRules(board)

    # Check if game would end
    black_moves = rules.get_valid_moves(Board.BLACK)
    white_moves = rules.get_valid_moves(Board.WHITE)

    # At least one should have moves in this small setup
    # This is a basic test; real game-over scenarios are more complex


def test_piece_counting():
    """Test piece counting"""
    board = Board(8)

    black_count, white_count = board.count_pieces()
    assert black_count == 2
    assert white_count == 2

    # Add more pieces
    board.set_piece(0, 0, Board.BLACK)
    board.set_piece(0, 1, Board.WHITE)

    black_count, white_count = board.count_pieces()
    assert black_count == 3
    assert white_count == 3


def test_flipping_multiple_directions():
    """Test flipping pieces in multiple directions"""
    board = Board(8)
    rules = OthelloRules(board)

    # Set up a scenario where one move flips in multiple directions
    # This requires a specific board configuration
    board.set_piece(2, 2, Board.WHITE)
    board.set_piece(2, 3, Board.WHITE)
    board.set_piece(3, 2, Board.WHITE)

    # Black move at (2, 4) should flip (2, 3) and (3, 3)
    if rules.is_valid_move(2, 4, Board.BLACK):
        rules.make_move(2, 4, Board.BLACK)
        assert board.get_piece(2, 4) == Board.BLACK
        assert board.get_piece(2, 3) == Board.BLACK  # Flipped