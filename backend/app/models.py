"""Data models for the Othello application"""
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime


class BotMetadata(BaseModel):
    """Metadata for an uploaded or built-in bot"""
    name: str
    type: Literal["builtin", "uploaded"]
    upload_time: Optional[str] = None
    file_path: str


class MatchConfig(BaseModel):
    """Configuration for a new match"""
    board_size: int = Field(ge=4, le=100, description="Board size (4-100)")
    black_player_type: Literal["human", "bot"]
    black_bot_name: Optional[str] = None
    white_player_type: Literal["human", "bot"]
    white_bot_name: Optional[str] = None
    init_timeout: float = Field(default=60.0, gt=0, description="Bot initialization timeout in seconds")
    move_timeout: float = Field(default=1.0, gt=0, description="Bot move timeout in seconds")


class MoveRequest(BaseModel):
    """Request to make a move"""
    match_id: str
    row: int
    col: int


class GameState(BaseModel):
    """Current state of the game"""
    board: list[list[int]]
    current_player: int  # 0 = black, 1 = white
    black_count: int
    white_count: int
    valid_moves: list[tuple[int, int]]
    game_over: bool
    winner: Optional[int] = None  # 0 = black, 1 = white, -1 = draw
    message: Optional[str] = None
    bot_thinking_time_ms: Optional[float] = None  # Time taken by bot to make last move in milliseconds
    last_move: Optional[tuple[int, int]] = None  # Position of last move
    last_flipped: Optional[list[tuple[int, int]]] = None  # Positions of stones flipped by last move
    black_init_time_ms: Optional[float] = None  # Time taken by black bot to initialize in milliseconds
    white_init_time_ms: Optional[float] = None  # Time taken by white bot to initialize in milliseconds


class RenameBotRequest(BaseModel):
    """Request to rename a bot"""
    new_name: str
