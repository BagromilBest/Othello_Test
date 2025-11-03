"""WebSocket handler for real-time game updates"""
import asyncio
import uuid
from typing import Dict, Optional
from fastapi import WebSocket
from .game.board import Board
from .game.rules import OthelloRules
from .models import MatchConfig, GameState
from .bot_manager import bot_manager


class Match:
    """Represents a single game match"""

    def __init__(self, config: MatchConfig):
        """Initialize a new match"""
        self.id = str(uuid.uuid4())
        self.config = config
        self.board = Board(config.board_size)
        self.rules = OthelloRules(self.board)
        self.current_player = Board.BLACK
        self.game_over = False
        self.winner: Optional[int] = None
        self.message: Optional[str] = None

        # Bot instances
        self.black_bot = None
        self.white_bot = None

        # Initialize bots if needed
        self._initialize_bots()

    def _initialize_bots(self):
        """Initialize bot players"""
        if self.config.black_player_type == "bot" and self.config.black_bot_name:
            try:
                bot_class = bot_manager.load_bot_class(self.config.black_bot_name)
                self.black_bot = bot_class(Board.BLACK, Board.WHITE)
            except Exception as e:
                print(f"Error loading black bot: {e}")

        if self.config.white_player_type == "bot" and self.config.white_bot_name:
            try:
                bot_class = bot_manager.load_bot_class(self.config.white_bot_name)
                self.white_bot = bot_class(Board.WHITE, Board.BLACK)
            except Exception as e:
                print(f"Error loading white bot: {e}")

    def get_state(self) -> GameState:
        """Get current game state"""
        valid_moves = [] if self.game_over else self.rules.get_valid_moves(self.current_player)
        black_count, white_count = self.board.count_pieces()

        return GameState(
            board=self.board.get_board(),
            current_player=self.current_player,
            black_count=black_count,
            white_count=white_count,
            valid_moves=valid_moves,
            game_over=self.game_over,
            winner=self.winner,
            message=self.message
        )

    def make_move(self, row: int, col: int) -> tuple[bool, Optional[str]]:
        """
        Make a move and update game state.

        Returns:
            Tuple of (success, error_message)
        """
        if self.game_over:
            return False, "Game is over"

        # Validate and make the move
        if not self.rules.is_valid_move(row, col, self.current_player):
            return False, f"Invalid move: ({row}, {col})"

        self.rules.make_move(row, col, self.current_player)

        # Switch player and check game state
        self._advance_turn()

        return True, None

    def make_bot_move(self) -> tuple[bool, Optional[str]]:
        """
        Execute a bot move for the current player.

        Returns:
            Tuple of (success, error_message)
        """
        if self.game_over:
            return False, "Game is over"

        # Get the current bot
        bot = self.black_bot if self.current_player == Board.BLACK else self.white_bot
        bot_name = self.config.black_bot_name if self.current_player == Board.BLACK else self.config.white_bot_name

        if bot is None:
            return False, "No bot configured for current player"

        # Execute bot move
        move, error = bot_manager.execute_bot_move(bot, self.board.get_board(), bot_name)

        if error:
            # Bot made an error - they lose
            self.game_over = True
            self.winner = 1 - self.current_player
            self.message = error
            return False, error

        row, col = move

        # Validate the move
        if not self.rules.is_valid_move(row, col, self.current_player):
            # Invalid move - bot loses
            self.game_over = True
            self.winner = 1 - self.current_player
            self.message = f"Bot '{bot_name}' made an invalid move ({row}, {col}) and lost"
            return False, self.message

        # Make the move
        self.rules.make_move(row, col, self.current_player)
        self._advance_turn()

        return True, None

    def _advance_turn(self):
        """Advance to next turn and check for game over"""
        # Check if game is over
        is_over, winner = self.rules.is_game_over()
        if is_over:
            self.game_over = True
            self.winner = winner
            if winner == -1:
                self.message = "Game ended in a draw"
            else:
                color_name = "Black" if winner == Board.BLACK else "White"
                self.message = f"{color_name} wins!"
            return

        # Switch player
        self.current_player = 1 - self.current_player

        # Check if current player has valid moves
        if len(self.rules.get_valid_moves(self.current_player)) == 0:
            # No valid moves, switch back
            self.current_player = 1 - self.current_player

            # Check again for game over
            if len(self.rules.get_valid_moves(self.current_player)) == 0:
                # Neither player can move
                is_over, winner = self.rules.is_game_over()
                self.game_over = True
                self.winner = winner
                if winner == -1:
                    self.message = "Game ended in a draw"
                else:
                    color_name = "Black" if winner == Board.BLACK else "White"
                    self.message = f"{color_name} wins!"


class ConnectionManager:
    """Manages WebSocket connections and game matches"""

    def __init__(self):
        """Initialize the connection manager"""
        self.active_connections: Dict[str, WebSocket] = {}
        self.matches: Dict[str, Match] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """Connect a new WebSocket client"""
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        """Disconnect a WebSocket client"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_message(self, client_id: str, message: dict):
        """Send a message to a specific client"""
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

    def create_match(self, config: MatchConfig) -> Match:
        """Create a new match"""
        match = Match(config)
        self.matches[match.id] = match
        return match

    def get_match(self, match_id: str) -> Optional[Match]:
        """Get a match by ID"""
        return self.matches.get(match_id)


# Global connection manager
manager = ConnectionManager()