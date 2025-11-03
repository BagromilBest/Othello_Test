"""Othello game rules and move validation"""
from .board import Board


class OthelloRules:
    """Implements Othello game rules for any board size"""

    # Eight directions: N, NE, E, SE, S, SW, W, NW
    DIRECTIONS = [
        (-1, 0), (-1, 1), (0, 1), (1, 1),
        (1, 0), (1, -1), (0, -1), (-1, -1)
    ]

    def __init__(self, board: Board):
        """
        Initialize rules for the given board.

        Args:
            board: The game board
        """
        self.board = board

    def get_valid_moves(self, color: int) -> list[tuple[int, int]]:
        """
        Get all valid moves for the given color.

        Args:
            color: Player color (0 = black, 1 = white)

        Returns:
            List of (row, col) tuples representing valid moves
        """
        valid_moves = []

        for row in range(self.board.size):
            for col in range(self.board.size):
                if self.is_valid_move(row, col, color):
                    valid_moves.append((row, col))

        return valid_moves

    def is_valid_move(self, row: int, col: int, color: int) -> bool:
        """
        Check if a move is valid for the given color.

        A move is valid if:
        1. The position is empty
        2. It flips at least one opponent piece

        Args:
            row: Row index
            col: Column index
            color: Player color

        Returns:
            True if the move is valid, False otherwise
        """
        # Position must be empty
        if not self.board.is_valid_position(row, col):
            return False

        if self.board.get_piece(row, col) != Board.EMPTY:
            return False

        # Must flip at least one piece
        opponent_color = 1 - color

        for dr, dc in self.DIRECTIONS:
            if self._would_flip_in_direction(row, col, dr, dc, color, opponent_color):
                return True

        return False

    def _would_flip_in_direction(self, row: int, col: int, dr: int, dc: int,
                                 color: int, opponent_color: int) -> bool:
        """
        Check if placing a piece would flip opponent pieces in a direction.

        Args:
            row, col: Starting position
            dr, dc: Direction vector
            color: Player color
            opponent_color: Opponent color

        Returns:
            True if pieces would be flipped in this direction
        """
        r, c = row + dr, col + dc
        found_opponent = False

        while self.board.is_valid_position(r, c):
            piece = self.board.get_piece(r, c)

            if piece == Board.EMPTY:
                return False
            elif piece == opponent_color:
                found_opponent = True
            elif piece == color:
                return found_opponent

            r += dr
            c += dc

        return False

    def make_move(self, row: int, col: int, color: int) -> bool:
        """
        Make a move and flip appropriate pieces.

        Args:
            row: Row index
            col: Column index
            color: Player color

        Returns:
            True if the move was valid and made, False otherwise
        """
        if not self.is_valid_move(row, col, color):
            return False

        # Place the piece
        self.board.set_piece(row, col, color)

        # Flip pieces in all directions
        opponent_color = 1 - color

        for dr, dc in self.DIRECTIONS:
            if self._would_flip_in_direction(row, col, dr, dc, color, opponent_color):
                self._flip_pieces_in_direction(row, col, dr, dc, color, opponent_color)

        return True

    def _flip_pieces_in_direction(self, row: int, col: int, dr: int, dc: int,
                                  color: int, opponent_color: int):
        """
        Flip opponent pieces in a specific direction.

        Args:
            row, col: Starting position
            dr, dc: Direction vector
            color: Player color
            opponent_color: Opponent color
        """
        r, c = row + dr, col + dc
        pieces_to_flip = []

        while self.board.is_valid_position(r, c):
            piece = self.board.get_piece(r, c)

            if piece == opponent_color:
                pieces_to_flip.append((r, c))
            elif piece == color:
                # Flip all collected pieces
                for flip_r, flip_c in pieces_to_flip:
                    self.board.set_piece(flip_r, flip_c, color)
                break
            else:
                break

            r += dr
            c += dc

    def is_game_over(self) -> tuple[bool, int]:
        """
        Check if the game is over.

        Game ends when:
        1. Board is full
        2. Neither player has valid moves

        Returns:
            Tuple of (is_over, winner)
            winner: 0 = black, 1 = white, -1 = draw
        """
        if self.board.is_full():
            return True, self._determine_winner()

        black_has_moves = len(self.get_valid_moves(Board.BLACK)) > 0
        white_has_moves = len(self.get_valid_moves(Board.WHITE)) > 0

        if not black_has_moves and not white_has_moves:
            return True, self._determine_winner()

        return False, -1

    def _determine_winner(self) -> int:
        """
        Determine the winner based on piece count.

        Returns:
            0 = black wins, 1 = white wins, -1 = draw
        """
        black_count, white_count = self.board.count_pieces()

        if black_count > white_count:
            return Board.BLACK
        elif white_count > black_count:
            return Board.WHITE
        else:
            return -1