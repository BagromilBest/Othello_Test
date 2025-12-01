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

6. **Run tests**
   ```bash
   npm run test
   ```

## Running on a LAN / Accessing from Other Devices

When running the frontend in development mode (via `npm run dev`) and accessing it from another device on the same network (e.g., running Vite on a Raspberry Pi and connecting from a Mac), special consideration is needed for API/WebSocket URLs.

### The Problem

By default, the frontend in development mode uses `localhost` URLs (`http://localhost:8000` and `ws://localhost:8000`). When you access the dev server remotely (via the Pi's IP address), these URLs point to the client's loopback interface (e.g., your Mac), not the server running the backend (the Pi). This causes API/WebSocket connections to fail.

### Solutions

**Option 1: Automatic Detection (Recommended)**

The frontend now automatically detects when it's being accessed remotely in development mode and will:
- Construct API/WS URLs using the server's hostname (e.g., `http://192.168.1.50:8000`)
- Display a yellow warning banner indicating remote dev mode
- Log warnings to the browser console

No configuration is needed - just access the frontend via the server's IP address.

**Option 2: Explicit Configuration**

For more control, set environment variables in a `.env` file in the `frontend/` directory:

```bash
# frontend/.env
VITE_API_URL=http://192.168.1.100:8000
VITE_WS_URL=ws://192.168.1.100:8000
```

Replace `192.168.1.100` with your server's actual IP address.

**Option 3: Production Build**

Run a production build which automatically uses the current host:

```bash
cd frontend
npm run build
npm run preview
```

### Verification

1. Start the backend on your server (e.g., Raspberry Pi):
   ```bash
   cd backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. Start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. From another device, access `http://<server-ip>:5173`

4. You should see the game load successfully. If using automatic detection, a yellow warning banner will appear.

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

## Security Features

This application includes comprehensive security measures to protect against malicious bot uploads:

### Implemented Security Controls

1. **Code Validation (AST-based Analysis)**
   - All uploaded Python files are analyzed using Abstract Syntax Tree (AST) parsing
   - Syntax errors are detected and rejected
   - Invalid Python files are rejected before execution

2. **Import Restrictions**
   - **Allowed imports**: `random`, `typing`, `time`, `math`, `copy`, `collections`, `itertools`, `functools`, `dataclasses`, `enum`, `abc`
   - **Blocked dangerous imports**: `os`, `sys`, `subprocess`, `shutil`, `requests`, `urllib`, `socket`, `pickle`, `importlib`, and many others
   - Any attempt to import disallowed modules results in immediate rejection

3. **Dangerous Function Detection**
   - Blocks dangerous built-in functions: `eval()`, `exec()`, `compile()`, `__import__()`, `open()`, `input()`, etc.
   - Detects attempts to access dangerous attributes: `__dict__`, `__class__`, `__bases__`, `__globals__`, etc.
   - Prevents file operations and delete operations

4. **Security Logging & Quarantine**
   - All flagged uploads are logged with:
     - Timestamp
     - Uploader's IP address
     - User agent information
     - Specific violations detected
     - Line numbers of problematic code
   - Flagged files are automatically moved to a `quarantine/` directory for review
   - Security logs can be accessed via API endpoint: `GET /api/security/logs`

5. **Detailed Error Messages**
   - Users receive clear feedback about what caused their upload to be rejected
   - Error messages include:
     - Type of violation (dangerous import, disallowed function, etc.)
     - Specific line numbers where violations occur
     - Code snippets showing the problematic code

6. **File Validation**
   - Only `.py` files are accepted
   - File content must be valid UTF-8
   - Duplicate bot names are rejected

### Security API Endpoints

- `POST /api/bots/upload` - Upload bot with security validation
- `GET /api/security/logs?limit=50` - View security event logs (for administrators)

### Example Security Rejections

```python
# ❌ REJECTED - Dangerous import
import os
class Bot:
    def select_move(self, board):
        os.system("rm -rf /")  # Blocked!
        return (0, 0)

# ❌ REJECTED - eval() usage
class Bot:
    def select_move(self, board):
        eval("malicious_code")  # Blocked!
        return (0, 0)

# ✅ ACCEPTED - Safe bot
import random
class Bot:
    def select_move(self, board):
        return random.choice([(0, 0), (1, 1)])
```

### Additional Recommendations for Production

While the current implementation provides strong protection against common attack vectors:

1. **Run bots in isolated containers** using Docker with:
   - Limited memory (e.g., 128MB)
   - CPU quotas
   - No network access
   - Read-only file systems

2. **Implement user authentication** to track uploads

3. **Add rate limiting** on bot uploads

4. **Regular security audits** of the quarantine directory

5. **Consider using RestrictedPython** for an additional execution sandbox layer

### Monitoring & Review

Administrators should regularly:
- Review the `quarantine/` directory for flagged files
- Check `quarantine/security_log.json` for suspicious activity patterns
- Monitor for unusual upload patterns or repeated violations from the same IP

## Security Considerations (Legacy Notes)

⚠️ **NOTE**: The security features described above provide significant protection. The following legacy notes are kept for reference:

1. **Sandbox uploaded bots** - ✅ Implemented via AST validation and import restrictions

2. **Implement authentication** - Recommended for production

3. **Add code scanning** - ✅ Implemented via AST-based analysis

4. **Set resource limits**:
   - Memory usage per bot - Recommended via Docker
   - CPU time restrictions - ✅ 2-second timeout implemented
   - Network access blocking - ✅ Network libraries blocked

5. **Current implementation** now includes comprehensive security validation and is significantly safer than the original version

### Example: Docker-based bot execution (optional enhancement)

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
