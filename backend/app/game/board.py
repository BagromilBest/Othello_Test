"""Board representation and basic operations for Othello"""


class Board:
    """Represents an n×n Othello board"""

    EMPTY = -1
    BLACK = 0
    WHITE = 1

    def __init__(self, size: int):
        """
        Initialize a board of given size.

        Args:
            size: Board dimension (n for n×n board)
        """
        if size < 4 or size > 100:
            raise ValueError("Board size must be between 4 and 100")

        self.size = size
        self.board = [[self.EMPTY for _ in range(size)] for _ in range(size)]
        self._initialize_starting_position()

    def _initialize_starting_position(self):
        """
        Place initial four pieces in the center.
        For odd-sized boards, place them slightly off-center.
        """
        mid = self.size // 2

        # Standard Othello starting position
        self.board[mid - 1][mid - 1] = self.WHITE
        self.board[mid - 1][mid] = self.BLACK
        self.board[mid][mid - 1] = self.BLACK
        self.board[mid][mid] = self.WHITE

    def get_board(self) -> list[list[int]]:
        """Return a copy of the current board state"""
        return [row[:] for row in self.board]

    def get_piece(self, row: int, col: int) -> int:
        """Get the piece at the given position"""
        if not self.is_valid_position(row, col):
            return self.EMPTY
        return self.board[row][col]

    def set_piece(self, row: int, col: int, color: int):
        """Place a piece at the given position"""
        if self.is_valid_position(row, col):
            self.board[row][col] = color

    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if position is within board bounds"""
        return 0 <= row < self.size and 0 <= col < self.size

    def count_pieces(self) -> tuple[int, int]:
        """
        Count pieces on the board.

        Returns:
            Tuple of (black_count, white_count)
        """
        black_count = 0
        white_count = 0

        for row in self.board:
            for cell in row:
                if cell == self.BLACK:
                    black_count += 1
                elif cell == self.WHITE:
                    white_count += 1

        return black_count, white_count

    def is_full(self) -> bool:
        """Check if the board is completely filled"""
        for row in self.board:
            if self.EMPTY in row:
                return False
        return True

    def copy(self) -> 'Board':
        """Create a deep copy of the board"""
        new_board = Board.__new__(Board)
        new_board.size = self.size
        new_board.board = self.get_board()
        return new_board