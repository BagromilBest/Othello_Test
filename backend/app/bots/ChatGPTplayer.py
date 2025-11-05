from typing import Optional, Tuple, Dict, List
import random

# ---------- Constants ----------
FULL = (1 << 64) - 1
FILE_A = 0x0101010101010101
FILE_H = 0x8080808080808080
NOT_FILE_A = FULL ^ FILE_A
NOT_FILE_H = FULL ^ FILE_H

WEIGHTS = [
    120, -20,  20,  5,  5,  20, -20, 120,
    -20, -40,  -5, -5, -5,  -5, -40, -20,
     20,  -5,  15,  3,  3,  15,  -5,  20,
      5,  -5,   3,  3,  3,   3,  -5,   5,
      5,  -5,   3,  3,  3,   3,  -5,   5,
     20,  -5,  15,  3,  3,  15,  -5,  20,
    -20, -40,  -5, -5, -5,  -5, -40, -20,
    120, -20,  20,  5,  5,  20, -20, 120
]

# ---------- Bit helpers ----------
def bit_at(r: int, c: int) -> int:
    return 1 << (r * 8 + c)

def bit_index(bit: int) -> int:
    return bit.bit_length() - 1

def index_to_rc(idx: int) -> Tuple[int, int]:
    return (idx // 8, idx % 8)

def shift_n(bb: int) -> int: return (bb >> 8) & FULL
def shift_s(bb: int) -> int: return (bb << 8) & FULL
def shift_e(bb: int) -> int: return ((bb & NOT_FILE_H) << 1) & FULL
def shift_w(bb: int) -> int: return (bb & NOT_FILE_A) >> 1
def shift_ne(bb: int) -> int: return (bb & NOT_FILE_H) >> 7
def shift_nw(bb: int) -> int: return (bb & NOT_FILE_A) >> 9
def shift_se(bb: int) -> int: return ((bb & NOT_FILE_H) << 9) & FULL
def shift_sw(bb: int) -> int: return ((bb & NOT_FILE_A) << 7) & FULL

DIRECTIONS = [
    shift_n, shift_s, shift_e, shift_w,
    shift_ne, shift_nw, shift_se, shift_sw
]


# ---------- MyPlayer ----------
class MyPlayer:
    """
    Reversi AI using bitboards and alpha-beta minimax.

    Compatible interface:
    - __init__(my_color, opp_color)
    - select_move(board) -> (row, col)
    """

    def __init__(self, my_color: int, opp_color: int):
        if my_color not in (0, 1) or opp_color not in (0, 1):
            raise ValueError("Colors must be 0 (black) or 1 (white).")

        self.my_color = my_color
        self.opp_color = opp_color
        self.is_black = (my_color == 0)
        self.max_depth = 5
        self.tt: Dict[Tuple[int, int, int], int] = {}

    # ---------- Board conversion ----------
    def _board_to_bits(self, board: List[List[int]]) -> Tuple[int, int]:
        black = 0
        white = 0
        for r in range(8):
            for c in range(8):
                val = board[r][c]
                if val == 0:
                    black |= bit_at(r, c)
                elif val == 1:
                    white |= bit_at(r, c)
        return black, white

    # ---------- Move generation ----------
    def _legal_moves_bits(self, player: int, opp: int) -> int:
        empty = ~(player | opp) & FULL
        moves = 0
        for shift in DIRECTIONS:
            t = shift(player) & opp
            for _ in range(6):
                t |= shift(t) & opp
            moves |= shift(t) & empty
        return moves

    def _compute_flips(self, move_bit: int, player: int, opp: int) -> int:
        flips = 0
        for shift in DIRECTIONS:
            x = shift(move_bit)
            captured = 0
            while x and (x & opp):
                captured |= x
                x = shift(x)
            if x & player:
                flips |= captured
        return flips

    # ---------- Evaluation ----------
    def _evaluate(self, player: int, opp: int) -> int:
        score = 0
        bb = player
        while bb:
            lsb = bb & -bb
            score += WEIGHTS[bit_index(lsb)]
            bb &= bb - 1
        bb = opp
        while bb:
            lsb = bb & -bb
            score -= WEIGHTS[bit_index(lsb)]
            bb &= bb - 1

        my_moves = self._legal_moves_bits(player, opp).bit_count()
        opp_moves = self._legal_moves_bits(opp, player).bit_count()
        mobility = 100 * (my_moves - opp_moves) // (my_moves + opp_moves + 1)
        discs = player.bit_count() - opp.bit_count()
        return score * 10 + mobility * 5 + discs * 2

    # ---------- Negamax ----------
    def _negamax(self, player: int, opp: int, depth: int, alpha: int, beta: int) -> int:
        key = (player, opp, depth)
        if key in self.tt:
            return self.tt[key]

        moves_bb = self._legal_moves_bits(player, opp)
        if depth == 0 or (moves_bb == 0 and self._legal_moves_bits(opp, player) == 0):
            val = self._evaluate(player, opp)
            self.tt[key] = val
            return val

        if moves_bb == 0:
            val = -self._negamax(opp, player, depth - 1, -beta, -alpha)
            self.tt[key] = val
            return val

        best = -10**9
        bb = moves_bb
        while bb:
            m = bb & -bb
            flips = self._compute_flips(m, player, opp)
            val = -self._negamax(opp & ~flips, player | flips | m, depth - 1, -beta, -alpha)
            best = max(best, val)
            alpha = max(alpha, val)
            if alpha >= beta:
                break
            bb &= bb - 1

        self.tt[key] = best
        return best

    # ---------- Root search ----------
    def _search_root(self, player: int, opp: int, depth: int) -> Optional[int]:
        moves_bb = self._legal_moves_bits(player, opp)
        if moves_bb == 0:
            return None
        best = -10**9
        best_move = None
        alpha = -10**9
        beta = 10**9

        bb = moves_bb
        while bb:
            m = bb & -bb
            flips = self._compute_flips(m, player, opp)
            val = -self._negamax(opp & ~flips, player | flips | m, depth - 1, -beta, -alpha)
            if val > best or (val == best and random.random() < 0.2):
                best = val
                best_move = m
            alpha = max(alpha, val)
            bb &= bb - 1
        return best_move

    # ---------- Public API ----------
    def select_move(self, board: List[List[int]]) -> Tuple[int, int]:
        """Return (row, col) for the next move, same format as RandomPlayer."""
        import time as time_module
        
        black, white = self._board_to_bits(board)
        player, opp = (black, white) if self.is_black else (white, black)

        # Time limit: 1 second
        time_limit = 1.0
        start_time = time_module.perf_counter()
        
        empties = 64 - (black | white).bit_count()
        
        # Iterative deepening with time management
        best_move_bit = None
        max_depth = 8 if empties <= 12 else 6 if empties <= 20 else self.max_depth
        
        for depth in range(1, max_depth + 1):
            # Check if we have time left
            elapsed = time_module.perf_counter() - start_time
            if elapsed >= time_limit * 0.8:  # Use 80% of time limit as safety margin
                break
                
            self.tt.clear()
            try:
                current_move = self._search_root(player, opp, depth)
                if current_move is not None:
                    best_move_bit = current_move
            except:
                # If anything goes wrong, use the best move we have so far
                break
                
            # Check time again after search
            elapsed = time_module.perf_counter() - start_time
            if elapsed >= time_limit * 0.9:  # Stop if we're at 90% of time
                break
        
        if best_move_bit is None:
            # No legal move — return a random empty square (to match RandomPlayer behavior)
            for r in range(8):
                for c in range(8):
                    if board[r][c] == -1:
                        return (r, c)
            return (0, 0)
        idx = bit_index(best_move_bit)
        return index_to_rc(idx)
