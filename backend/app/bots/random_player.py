"""
Example bot that makes random valid moves.

This demonstrates the required bot interface:
- __init__(my_color, opp_color)
- select_move(board) -> (row, col)
"""
import random


class RandomPlayer:
    """A simple bot that selects random valid moves"""

    def __init__(self, my_color: int, opp_color: int):
        """
        Initialize the random player.

        Args:
            my_color: 0 for black, 1 for white
            opp_color: The opponent's color (0 or 1)
        """
        self.my_color = my_color
        self.opp_color = opp_color

    def select_move(self, board: list[list[int]]) -> tuple[int, int]:
        """
        Select a random valid move.

        Args:
            board: n×n 2D list where:
                   -1 = empty
                   0 = black
                   1 = white

        Returns:
            Tuple of (row, col) representing the selected move
        """
        valid_moves = self._get_valid_moves(board)

        if not valid_moves:
            # No valid moves (shouldn't happen in a real game)
            # Return any empty position
            n = len(board)
            for i in range(n):
                for j in range(n):
                    if board[i][j] == -1:
                        return (i, j)
            return (0, 0)  # Fallback

        return random.choice(valid_moves)

    def _get_valid_moves(self, board: list[list[int]]) -> list[tuple[int, int]]:
        """Find all valid moves for the current player"""
        n = len(board)
        valid_moves = []

        for row in range(n):
            for col in range(n):
                if board[row][col] == -1:  # Empty cell
                    if self._is_valid_move(board, row, col):
                        valid_moves.append((row, col))

        return valid_moves

    def _is_valid_move(self, board: list[list[int]], row: int, col: int) -> bool:
        """Check if a move is valid (would flip at least one opponent piece)"""
        n = len(board)
        directions = [
            (-1, 0), (-1, 1), (0, 1), (1, 1),
            (1, 0), (1, -1), (0, -1), (-1, -1)
        ]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            found_opponent = False

            while 0 <= r < n and 0 <= c < n:
                if board[r][c] == -1:  # Empty
                    break
                elif board[r][c] == self.opp_color:
                    found_opponent = True
                elif board[r][c] == self.my_color:
                    if found_opponent:
                        return True
                    break

                r += dr
                c += dc

        return False
