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

    def make_move(self, row: int, col: int, color: int) -> tuple[bool, list[tuple[int, int]]]:
        """
        Make a move and flip appropriate pieces.

        Args:
            row: Row index
            col: Column index
            color: Player color

        Returns:
            Tuple of (success, flipped_pieces)
            - success: True if the move was valid and made, False otherwise
            - flipped_pieces: List of (row, col) tuples of pieces that were flipped
        """
        if not self.is_valid_move(row, col, color):
            return False, []

        # Place the piece
        self.board.set_piece(row, col, color)

        # Flip pieces in all directions and collect all flipped positions
        opponent_color = 1 - color
        all_flipped = []

        for dr, dc in self.DIRECTIONS:
            if self._would_flip_in_direction(row, col, dr, dc, color, opponent_color):
                flipped = self._flip_pieces_in_direction(row, col, dr, dc, color, opponent_color)
                all_flipped.extend(flipped)

        return True, all_flipped

    def _flip_pieces_in_direction(self, row: int, col: int, dr: int, dc: int,
                                  color: int, opponent_color: int) -> list[tuple[int, int]]:
        """
        Flip opponent pieces in a specific direction.

        Args:
            row, col: Starting position
            dr, dc: Direction vector
            color: Player color
            opponent_color: Opponent color

        Returns:
            List of (row, col) tuples of pieces that were flipped
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
                return pieces_to_flip
            else:
                break

            r += dr
            c += dc

        return []

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

    def get_stable_pieces(self) -> list[tuple[int, int]]:
        """
        Get all stable pieces on the board.
        
        A stable piece is a piece that cannot be captured in any way.
        A piece is stable if in at least two perpendicular directions,
        all pieces are of the same color and stable, or it reaches the edge.
        
        Returns:
            List of (row, col) tuples representing stable pieces
        """
        stable = [[False for _ in range(self.board.size)] for _ in range(self.board.size)]
        stable_pieces = []
        
        # Mark pieces as stable iteratively until no new stable pieces are found
        changed = True
        while changed:
            changed = False
            for row in range(self.board.size):
                for col in range(self.board.size):
                    if stable[row][col]:
                        continue  # Already marked as stable
                    
                    piece = self.board.get_piece(row, col)
                    if piece == Board.EMPTY:
                        continue  # Empty cells are not stable
                    
                    # Check if this piece is stable
                    if self._is_piece_stable(row, col, piece, stable):
                        stable[row][col] = True
                        changed = True
        
        # Collect all stable pieces
        for row in range(self.board.size):
            for col in range(self.board.size):
                if stable[row][col]:
                    stable_pieces.append((row, col))
        
        return stable_pieces
    
    def _is_piece_stable(self, row: int, col: int, color: int, stable: list[list[bool]]) -> bool:
        """
        Check if a piece at (row, col) is stable.
        
        A piece is stable if in at least two perpendicular directions,
        all pieces along that direction (until the edge) are of the same color
        and are stable (or the direction leads to an edge).
        
        Args:
            row, col: Position of the piece
            color: Color of the piece
            stable: 2D array tracking which pieces are already marked as stable
            
        Returns:
            True if the piece is stable
        """
        # Check pairs of opposite directions
        # Horizontal/Vertical pairs: (N,S), (E,W), (NE,SW), (NW,SE)
        direction_pairs = [
            [(-1, 0), (1, 0)],    # North and South
            [(0, -1), (0, 1)],    # West and East
            [(-1, -1), (1, 1)],   # NW and SE
            [(-1, 1), (1, -1)]    # NE and SW
        ]
        
        stable_directions = 0
        
        for pair in direction_pairs:
            # Check if both directions in this pair are stable
            both_stable = True
            for dr, dc in pair:
                if not self._is_direction_stable(row, col, dr, dc, color, stable):
                    both_stable = False
                    break
            
            if both_stable:
                stable_directions += 1
        
        # A piece is stable if at least 2 perpendicular direction pairs are stable
        return stable_directions >= 2
    
    def _is_direction_stable(self, row: int, col: int, dr: int, dc: int, 
                            color: int, stable: list[list[bool]]) -> bool:
        """
        Check if a direction from a piece is stable.
        
        A direction is stable if all pieces along that direction are of the same color
        and are stable, or the direction leads to an edge.
        
        Args:
            row, col: Starting position
            dr, dc: Direction vector
            color: Expected color
            stable: 2D array tracking which pieces are marked as stable
            
        Returns:
            True if the direction is stable
        """
        r, c = row + dr, col + dc
        
        while self.board.is_valid_position(r, c):
            piece = self.board.get_piece(r, c)
            
            # If we encounter an empty cell or opponent piece, direction is not stable
            if piece != color:
                return False
            
            # If we encounter a piece of our color that's not stable, direction is not stable
            if not stable[r][c]:
                return False
            
            r += dr
            c += dc
        
        # We reached the edge with all pieces of the same color and stable
        return True