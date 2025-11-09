"""Main FastAPI application"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import asyncio

from .models import MatchConfig, BotMetadata, GameState, RenameBotRequest
from .bot_manager import bot_manager
from .websocket_handler import manager

app = FastAPI(title="Othello API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Othello API", "version": "1.0.0"}


@app.get("/api/bots", response_model=list[BotMetadata])
async def list_bots():
    """Get list of all available bots"""
    return bot_manager.list_bots()


@app.post("/api/bots/upload", response_model=BotMetadata)
async def upload_bot(request: Request, file: UploadFile = File(...)):
    """
    Upload a new bot file with security validation.

    The bot must be a Python file with a class implementing:
    - __init__(self, my_color: int, opp_color: int)
    - select_move(self, board: list[list[int]]) -> tuple[int, int]
    
    Security checks:
    - File must be a valid Python file (.py extension)
    - Only allowed imports (random, typing, time, math, etc.)
    - No dangerous imports (os, sys, subprocess, etc.)
    - No dangerous function calls or attributes
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    content = await file.read()

    # Gather request information for security logging
    request_info = {
        "ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown"),
        "timestamp": None  # Will be set by security logger
    }

    try:
        metadata = bot_manager.upload_bot(file.filename, content, request_info)
        return metadata
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/bots/{bot_name}")
async def delete_bot(bot_name: str):
    """
    Delete a bot.

    Args:
        bot_name: Name of the bot to delete

    Returns:
        Success message

    Raises:
        HTTPException: If bot not found or is builtin
    """
    try:
        bot_manager.delete_bot(bot_name)
        return {"message": f"Bot '{bot_name}' deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/api/bots/{bot_name}/rename", response_model=BotMetadata)
async def rename_bot(bot_name: str, request: RenameBotRequest):
    """
    Rename a bot.

    Args:
        bot_name: Current bot name
        request: Request body containing new_name

    Returns:
        Updated BotMetadata

    Raises:
        HTTPException: If bot not found, is builtin, or new name already exists
    """
    try:
        metadata = bot_manager.rename_bot(bot_name, request.new_name)
        return metadata
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/security/logs")
async def get_security_logs(limit: Optional[int] = 50):
    """
    Get security logs of flagged bot uploads.
    
    Args:
        limit: Maximum number of log entries to return (default: 50)
    
    Returns:
        List of security log entries
    """
    from .bot_security import security_logger
    return security_logger.get_security_log(limit=limit)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for real-time game communication.

    Messages from client:
    - create_match: {type: "create_match", config: MatchConfig}
    - play_move: {type: "play_move", match_id: str, row: int, col: int}
    - bot_move: {type: "bot_move", match_id: str}
    - get_state: {type: "get_state", match_id: str}

    Messages to client:
    - match_created: {type: "match_created", match_id: str}
    - game_state: {type: "game_state", state: GameState}
    - move_played: {type: "move_played", row: int, col: int}
    - match_end: {type: "match_end", winner: int, message: str}
    - error: {type: "error", message: str}
    """
    await manager.connect(websocket, client_id)

    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            message_type = data.get("type")

            if message_type == "create_match":
                # Create a new match
                try:
                    config = MatchConfig(**data.get("config", {}))
                    match = manager.create_match(config)

                    await manager.send_message(client_id, {
                        "type": "match_created",
                        "match_id": match.id
                    })

                    # Send initial state
                    state = match.get_state()
                    await manager.send_message(client_id, {
                        "type": "game_state",
                        "state": state.model_dump()
                    })

                    # If both players are bots, start auto-play
                    if config.black_player_type == "bot" and config.white_player_type == "bot":
                        asyncio.create_task(auto_play_match(client_id, match.id))
                    elif config.black_player_type == "bot":
                        # Black is bot and goes first
                        asyncio.create_task(execute_bot_turn(client_id, match.id))

                except Exception as e:
                    await manager.send_message(client_id, {
                        "type": "error",
                        "message": f"Failed to create match: {str(e)}"
                    })

            elif message_type == "play_move":
                # Human player makes a move
                match_id = data.get("match_id")
                row = data.get("row")
                col = data.get("col")

                match = manager.get_match(match_id)
                if not match:
                    await manager.send_message(client_id, {
                        "type": "error",
                        "message": "Match not found"
                    })
                    continue

                if match.paused:
                    await manager.send_message(client_id, {
                        "type": "error",
                        "message": "Game is paused"
                    })
                    continue

                success, error = match.make_move(row, col)

                if success:
                    await manager.send_message(client_id, {
                        "type": "move_played",
                        "row": row,
                        "col": col,
                        "player": 1 - match.current_player  # The player who just moved
                    })

                    state = match.get_state()
                    await manager.send_message(client_id, {
                        "type": "game_state",
                        "state": state.model_dump()
                    })

                    if match.game_over:
                        await manager.send_message(client_id, {
                            "type": "match_end",
                            "winner": match.winner,
                            "message": match.message
                        })
                    else:
                        # Check if next player is a bot
                        is_bot = (match.current_player == 0 and match.config.black_player_type == "bot") or \
                                 (match.current_player == 1 and match.config.white_player_type == "bot")

                        if is_bot and not match.paused:
                            asyncio.create_task(execute_bot_turn(client_id, match_id))
                else:
                    await manager.send_message(client_id, {
                        "type": "error",
                        "message": error or "Invalid move"
                    })

            elif message_type == "bot_move":
                # Manually trigger a bot move
                match_id = data.get("match_id")
                await execute_bot_turn(client_id, match_id)

            elif message_type == "get_state":
                # Get current game state
                match_id = data.get("match_id")
                match = manager.get_match(match_id)

                if match:
                    state = match.get_state()
                    await manager.send_message(client_id, {
                        "type": "game_state",
                        "state": state.model_dump()
                    })
                else:
                    await manager.send_message(client_id, {
                        "type": "error",
                        "message": "Match not found"
                    })

            elif message_type == "toggle_pause":
                # Toggle pause state
                match_id = data.get("match_id")
                match = manager.get_match(match_id)

                if match:
                    new_pause_state = match.toggle_pause()
                    state = match.get_state()
                    await manager.send_message(client_id, {
                        "type": "game_state",
                        "state": state.model_dump()
                    })
                    
                    # If we're resuming and it's a bot's turn, trigger the bot move
                    if not new_pause_state and not match.game_over:
                        is_bot = (match.current_player == 0 and match.config.black_player_type == "bot") or \
                                 (match.current_player == 1 and match.config.white_player_type == "bot")
                        
                        if is_bot:
                            asyncio.create_task(execute_bot_turn(client_id, match_id))
                else:
                    await manager.send_message(client_id, {
                        "type": "error",
                        "message": "Match not found"
                    })

    except WebSocketDisconnect:
        manager.disconnect(client_id)


async def execute_bot_turn(client_id: str, match_id: str, delay: float = 0.5):
    """
    Execute a bot's turn with optional delay.

    Args:
        client_id: WebSocket client ID
        match_id: Match ID
        delay: Delay before executing move (for visualization)
    """
    await asyncio.sleep(delay)

    match = manager.get_match(match_id)
    if not match or match.game_over or match.paused:
        return

    success, error = match.make_bot_move()

    # Send updated state
    state = match.get_state()
    await manager.send_message(client_id, {
        "type": "game_state",
        "state": state.model_dump()
    })

    if not success:
        await manager.send_message(client_id, {
            "type": "bot_error",
            "message": error or "Bot move failed"
        })

    if match.game_over:
        await manager.send_message(client_id, {
            "type": "match_end",
            "winner": match.winner,
            "message": match.message
        })


async def auto_play_match(client_id: str, match_id: str, move_delay: float = 1.0):
    """
    Auto-play a match between two bots.

    Args:
        client_id: WebSocket client ID
        match_id: Match ID
        move_delay: Delay between moves (seconds)
    """
    match = manager.get_match(match_id)
    if not match:
        return

    while not match.game_over:
        # Wait if paused
        if match.paused:
            await asyncio.sleep(0.5)
            continue
            
        await execute_bot_turn(client_id, match_id, move_delay)