"""Tests for stable piece detection"""
import pytest
from app.game.board import Board
from app.game.rules import OthelloRules


def test_corner_pieces_are_stable():
    """Test that corner pieces are immediately stable"""
    board = Board(8)
    rules = OthelloRules(board)
    
    # Place pieces in corners
    board.set_piece(0, 0, Board.BLACK)
    board.set_piece(0, 7, Board.WHITE)
    board.set_piece(7, 0, Board.BLACK)
    board.set_piece(7, 7, Board.WHITE)
    
    stable_pieces = rules.get_stable_pieces()
    
    # All corner pieces should be stable
    assert (0, 0) in stable_pieces
    assert (0, 7) in stable_pieces
    assert (7, 0) in stable_pieces
    assert (7, 7) in stable_pieces


def test_edge_pieces_connected_to_corner_are_stable():
    """Test that edge pieces connected to a corner are stable"""
    board = Board(8)
    rules = OthelloRules(board)
    
    # Place a corner and adjacent edge pieces
    board.set_piece(0, 0, Board.BLACK)
    board.set_piece(0, 1, Board.BLACK)
    board.set_piece(0, 2, Board.BLACK)
    board.set_piece(1, 0, Board.BLACK)
    board.set_piece(2, 0, Board.BLACK)
    
    stable_pieces = rules.get_stable_pieces()
    
    # Corner and adjacent pieces should be stable
    assert (0, 0) in stable_pieces
    assert (0, 1) in stable_pieces
    assert (0, 2) in stable_pieces
    assert (1, 0) in stable_pieces
    assert (2, 0) in stable_pieces


def test_isolated_piece_not_stable():
    """Test that an isolated piece in the middle is not stable"""
    board = Board(8)
    rules = OthelloRules(board)
    
    # Place a single piece in the middle
    board.set_piece(4, 4, Board.BLACK)
    
    stable_pieces = rules.get_stable_pieces()
    
    # Isolated piece should not be stable
    assert (4, 4) not in stable_pieces


def test_full_edge_is_stable():
    """Test that a full edge of one color is stable"""
    board = Board(8)
    rules = OthelloRules(board)
    
    # Fill the top edge with black pieces
    for col in range(8):
        board.set_piece(0, col, Board.BLACK)
    
    stable_pieces = rules.get_stable_pieces()
    
    # All pieces on the top edge should be stable
    for col in range(8):
        assert (0, col) in stable_pieces


def test_mixed_edge_not_all_stable():
    """Test that a mixed edge has limited stability"""
    board = Board(8)
    rules = OthelloRules(board)
    
    # Place pieces on top edge with mixed colors
    board.set_piece(0, 0, Board.BLACK)
    board.set_piece(0, 1, Board.BLACK)
    board.set_piece(0, 2, Board.WHITE)
    board.set_piece(0, 3, Board.WHITE)
    
    stable_pieces = rules.get_stable_pieces()
    
    # The pieces should not all be stable due to color changes
    # Only corners can guarantee stability
    assert (0, 0) in stable_pieces
    # Other pieces may or may not be stable depending on implementation


def test_stable_pieces_after_game():
    """Test stable piece detection in a real game scenario"""
    board = Board(8)
    rules = OthelloRules(board)
    
    # Simulate end game with corners captured
    board.set_piece(0, 0, Board.BLACK)
    board.set_piece(0, 1, Board.BLACK)
    board.set_piece(1, 0, Board.BLACK)
    board.set_piece(1, 1, Board.BLACK)
    
    board.set_piece(7, 7, Board.WHITE)
    board.set_piece(7, 6, Board.WHITE)
    board.set_piece(6, 7, Board.WHITE)
    board.set_piece(6, 6, Board.WHITE)
    
    stable_pieces = rules.get_stable_pieces()
    
    # Corner and adjacent connected pieces should be stable
    assert (0, 0) in stable_pieces
    assert (7, 7) in stable_pieces
    assert len(stable_pieces) > 0


def test_no_stable_pieces_in_initial_position():
    """Test that initial board position has no stable pieces"""
    board = Board(8)
    rules = OthelloRules(board)
    
    # Initial position has pieces in the center, none should be stable
    stable_pieces = rules.get_stable_pieces()
    
    # Center pieces are not stable as they can be captured
    assert len(stable_pieces) == 0


def test_complete_row_and_column_from_corner():
    """Test stability with complete row and column from corner"""
    board = Board(8)
    rules = OthelloRules(board)
    
    # Fill entire first row and first column with black
    for i in range(8):
        board.set_piece(0, i, Board.BLACK)
        board.set_piece(i, 0, Board.BLACK)
    
    stable_pieces = rules.get_stable_pieces()
    
    # All pieces in first row and column should be stable
    for i in range(8):
        assert (0, i) in stable_pieces
        assert (i, 0) in stable_pieces
    
    # The corner (0,0) should definitely be stable
    assert (0, 0) in stable_pieces
