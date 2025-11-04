# Othello/Reversi Web Application

A full-stack web application for playing Othello (Reversi) with support for human vs bot, bot vs bot, and human vs human matches. Features customizable board sizes (4×4 to 100×100) and the ability to upload custom bot implementations.

## Features

- 🎮 **Multiple Game Modes**: Human vs Bot, Bot vs Bot, Human vs Human
- 📏 **Variable Board Sizes**: Play on any board from 4×4 to 100×100
- 🤖 **Custom Bots**: Upload your own Python bot implementations
- ⚡ **Real-time Updates**: WebSocket-based live game state synchronization
- 🎨 **Modern UI**: Dark material design with TailwindCSS
- 🐳 **Docker Ready**: Full Docker Compose setup for easy deployment
- 🧪 **Tested**: Comprehensive pytest test suite

## Quick Start with Docker

### Prerequisites

- Docker and Docker Compose installed
- At least 2GB of available RAM

### Running the Application

1. **Clone the repository**
   ```bash
   git clone https://github.com/BagromilBest/Othello_Test.git
   cd Othello_Test
   ```

2. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   
   **Network Access**: The application can be accessed from other devices on the same network:
   - Find your machine's IP address (e.g., `192.168.1.100`)
   - Access from other devices: `http://<your-ip-address>` (e.g., `http://192.168.1.100`)
   - The frontend automatically connects to the backend using the same host

4. **Stop the application**
   ```bash
   docker-compose down
   ```

## Development Setup

### Backend

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Run tests**
   ```bash
   pytest
   ```

### Frontend

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Create environment file** (optional)
   
   For local development:
   ```bash
   echo "VITE_API_URL=http://localhost:8000" > .env
   echo "VITE_WS_URL=ws://localhost:8000" >> .env
   ```
   
   For network access during development (replace with your IP):
   ```bash
   echo "VITE_API_URL=http://192.168.1.100:8000" > .env
   echo "VITE_WS_URL=ws://192.168.1.100:8000" >> .env
   ```

4. **Run development server**
   ```bash
   npm run dev
   ```

5. **Build for production**
   ```bash
   npm run build
   ```

## Creating Custom Bots

### Bot Interface Requirements

All bots must implement the following Python interface:

```python
class MyPlayer:
    def __init__(self, my_color: int, opp_color: int):
        """
        Initialize your bot.
        
        Args:
            my_color: 0 for black, 1 for white
            opp_color: The opponent's color (0 or 1)
        """
        self.my_color = my_color
        self.opp_color = opp_color
    
    def select_move(self, board: list[list[int]]) -> tuple[int, int]:
        """
        Select a move given the current board state.
        
        Args:
            board: n×n 2D list where:
                   -1 = empty
                   0 = black piece
                   1 = white piece
        
        Returns:
            Tuple of (row, col) representing your move
        """
        # Your logic here
        return (row, col)
```

### Board Representation

- **Empty cell**: `-1`
- **Black piece**: `0`
- **White piece**: `1`
- **Board**: 2D list `board[row][col]`

### Bot Constraints

- **Time limit**: 2 seconds per move
- **Invalid moves**: Result in immediate loss
- **Exceptions**: Caught and result in loss
- **Return format**: Must return `tuple[int, int]`

### Example Bot

See `examples/random_player.py` for a complete working example that makes random valid moves.

### Uploading Bots

1. **Via Web Interface**:
   - Go to the main menu
   - Click "Choose File" under "Upload New Bot"
   - Select your `.py` file
   - Bot will appear in the available bots list

2. **Manual Installation** (built-in bots):
   - Place your `.py` file in `backend/app/bots/`
   - Restart the backend server
   - Bot will be automatically discovered

### Testing Your Bot

```python
# Test locally before uploading
from my_bot import MyPlayer

bot = MyPlayer(0, 1)  # Black player
board = [[-1, -1, ...], ...]  # Your test board
move = bot.select_move(board)
print(f"Bot selected: {move}")
```

## Game Rules

### Othello Basics

1. **Starting Position**: 4 pieces in the center (2 black, 2 white)
2. **Objective**: Have the most pieces when the game ends
3. **Valid Moves**: Must flip at least one opponent piece
4. **Flipping**: Capture opponent pieces between your new piece and existing pieces
5. **Turn Passing**: If no valid moves, turn passes to opponent
6. **Game End**: When board is full or neither player can move

### Variable Board Sizes

- This implementation supports any board size from 4×4 to 100×100
- Starting pieces are always placed in the center (adjusted for odd sizes)
- All standard Othello rules apply regardless of board size

## Architecture

### Backend (FastAPI)

```
backend/
├── app/
│   ├── main.py                 # FastAPI app & WebSocket handler
│   ├── models.py               # Pydantic models
│   ├── bot_manager.py          # Bot loading and execution
│   ├── websocket_handler.py    # WebSocket game management
│   ├── game/
│   │   ├── board.py            # Board representation
│   │   └── rules.py            # Game rules engine
│   └── bots/                   # Built-in bots directory
├── uploads/                    # Uploaded bots (persistent)
└── tests/                      # Pytest test suite
```

### Frontend (React + Vite)

```
frontend/
├── src/
│   ├── components/
│   │   ├── MainMenu.jsx        # Game setup interface
│   │   ├── GameView.jsx        # Main game container
│   │   └── Board.jsx           # Board rendering
│   ├── App.jsx                 # Root component
│   └── main.jsx                # Entry point
└── public/                     # Static assets
```

## API Endpoints

### REST API

- `GET /api/bots` - List all available bots
- `POST /api/bots/upload` - Upload a new bot file

### WebSocket

Connect to `/ws/{client_id}` for real-time game updates.

**Client → Server Messages**:
```json
{
  "type": "create_match",
  "config": {
    "board_size": 8,
    "black_player_type": "human",
    "black_bot_name": null,
    "white_player_type": "bot",
    "white_bot_name": "random_bot"
  }
}
```

```json
{
  "type": "play_move",
  "match_id": "uuid",
  "row": 2,
  "col": 3
}
```

**Server → Client Messages**:
```json
{
  "type": "game_state",
  "state": {
    "board": [[...]],
    "current_player": 0,
    "black_count": 4,
    "white_count": 1,
    "valid_moves": [[2,3], [3,2]],
    "game_over": false,
    "winner": null,
    "message": null
  }
}
```

## Security Considerations

⚠️ **WARNING**: This application executes uploaded Python code. In production:

1. **Sandbox uploaded bots** using:
   - Docker containers with resource limits
   - Separate processes with restricted permissions
   - Virtual machines for complete isolation

2. **Implement authentication** to track who uploads what

3. **Add code scanning** for malicious patterns

4. **Set resource limits**:
   - Memory usage per bot
   - CPU time restrictions
   - Network access blocking

5. **Current implementation** uses basic timeout controls but is NOT production-ready for untrusted code

### Recommended Security Enhancements

```python
# Example: Docker-based bot execution
import docker

client = docker.from_env()
container = client.containers.run(
    "python:3.11-slim",
    f"python bot.py",
    mem_limit="128m",
    cpu_quota=50000,
    network_disabled=True,
    timeout=2
)
```

## Troubleshooting

### Backend won't start
- Ensure Python 3.11+ is installed
- Check port 8000 is not in use
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Frontend shows connection error
- Verify backend is running on port 8000
- Check CORS settings in `backend/app/main.py`
- Ensure WebSocket URL is correct (check browser console)

### Cannot access from other devices on network
- Ensure both frontend (port 80) and backend (port 8000) are accessible
- Check firewall settings on the host machine
- Verify you're using the correct IP address of the host machine
- In production (Docker), the app automatically uses the current host
- In development, set environment variables with your machine's IP address

### Bot upload fails
- File must have `.py` extension
- Bot must implement required interface
- Check file size limits
- Verify uploads directory has write permissions

### Invalid move errors
- Bot must return `tuple[int, int]`
- Coordinates must be valid (within board bounds)
- Move must flip at least one opponent piece
- Check bot logic with `examples/random_player.py` as reference

### Docker build fails
- Ensure Docker and Docker Compose are up to date
- Check available disk space
- Try `docker-compose build --no-cache`

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `pytest backend/tests/`
5. Commit: `git commit -am 'Add feature'`
6. Push: `git push origin feature-name`
7. Create a Pull Request

## License

MIT License - feel free to use this project for learning and development.

## Acknowledgments

- Othello/Reversi game rules: [World Othello Federation](https://www.worldothello.org/)
- Built with FastAPI, React, and TailwindCSS
- Inspired by classic board game implementations

---

**Happy Gaming! 🎮**
