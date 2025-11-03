import React, { useState, useEffect, useRef } from 'react';
import Board from './Board';

const GameView = ({ onReturnToMenu, wsUrl }) => {
  const [gameState, setGameState] = useState(null);
  const [matchId, setMatchId] = useState(null);
  const [message, setMessage] = useState('');
  const [connected, setConnected] = useState(false);
  const [matchConfig, setMatchConfig] = useState(null);
  const wsRef = useRef(null);

  useEffect(() => {
    // Get match config from sessionStorage (set by MainMenu)
    const config = JSON.parse(sessionStorage.getItem('matchConfig') || 'null');
    if (config) {
      setMatchConfig(config);
      connectWebSocket(config);
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = (config) => {
    const clientId = Math.random().toString(36).substring(7);
    const ws = new WebSocket(`${wsUrl}/ws/${clientId}`);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setConnected(true);
      setMessage('Connected to server');

      // Create a new match
      ws.send(JSON.stringify({
        type: 'create_match',
        config: config,
      }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setMessage('Connection error');
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
      setMessage('Disconnected from server');
    };

    wsRef.current = ws;
  };

  const handleWebSocketMessage = (data) => {
    console.log('Received:', data);

    switch (data.type) {
      case 'match_created':
        setMatchId(data.match_id);
        setMessage('Match created');
        break;

      case 'game_state':
        setGameState(data.state);
        if (data.state.message) {
          setMessage(data.state.message);
        }
        break;

      case 'move_played':
        setMessage(`Move played: (${data.row}, ${data.col})`);
        break;

      case 'match_end':
        const winnerText = data.winner === -1
          ? 'Draw!'
          : data.winner === 0
            ? 'Black wins!'
            : 'White wins!';
        setMessage(data.message || winnerText);
        break;

      case 'error':
        setMessage(`Error: ${data.message}`);
        break;

      case 'bot_error':
        setMessage(`Bot Error: ${data.message}`);
        break;

      default:
        console.log('Unknown message type:', data.type);
    }
  };

  const handleCellClick = (row, col) => {
    if (!gameState || gameState.game_over || !wsRef.current) {
      return;
    }

    // Check if it's a human player's turn
    const currentPlayerType = gameState.current_player === 0
      ? matchConfig?.black_player_type
      : matchConfig?.white_player_type;

    if (currentPlayerType !== 'human') {
      return; // It's a bot's turn
    }

    // Check if the move is valid
    const isValid = gameState.valid_moves.some(
      ([r, c]) => r === row && c === col
    );

    if (!isValid) {
      setMessage('Invalid move!');
      return;
    }

    // Send the move
    wsRef.current.send(JSON.stringify({
      type: 'play_move',
      match_id: matchId,
      row: row,
      col: col,
    }));
  };

  const handleReturnToMenu = () => {
    sessionStorage.removeItem('matchConfig');
    onReturnToMenu();
  };

  if (!gameState) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-400">Initializing game...</p>
        </div>
      </div>
    );
  }

  const currentPlayerColor = gameState.current_player === 0 ? 'Black' : 'White';
  const currentPlayerType = gameState.current_player === 0
    ? matchConfig?.black_player_type
    : matchConfig?.white_player_type;

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header with scores */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {/* Black Score */}
        <div className="card text-center">
          <div className="flex items-center justify-center mb-2">
            <span className="w-8 h-8 bg-black rounded-full mr-2 border-2 border-white"></span>
            <h3 className="text-xl font-semibold">Black</h3>
          </div>
          <p className="text-3xl font-bold text-primary">{gameState.black_count}</p>
          <p className="text-sm text-gray-400 mt-1">
            {matchConfig?.black_player_type === 'human' ? 'Human' : matchConfig?.black_bot_name}
          </p>
        </div>

        {/* Status */}
        <div className="card text-center">
          <h3 className="text-sm font-medium text-gray-400 mb-2">Status</h3>
          <p className="text-lg font-semibold">
            {gameState.game_over ? (
              <span className="text-green-400">{message}</span>
            ) : (
              <>
                <span className={gameState.current_player === 0 ? 'text-white' : 'text-gray-300'}>
                  {currentPlayerColor}'s Turn
                </span>
                <span className="block text-sm text-gray-400 mt-1">
                  ({currentPlayerType})
                </span>
              </>
            )}
          </p>
          {!gameState.game_over && (
            <>
              <p className="text-xs text-gray-500 mt-2">
                Valid moves: {gameState.valid_moves.length}
              </p>
              {gameState.bot_thinking_time_ms !== null && gameState.bot_thinking_time_ms !== undefined && (
                <p className="text-xs text-blue-400 mt-1">
                  Bot thinking: {gameState.bot_thinking_time_ms.toFixed(2)}ms
                </p>
              )}
            </>
          )}
        </div>

        {/* White Score */}
        <div className="card text-center">
          <div className="flex items-center justify-center mb-2">
            <span className="w-8 h-8 bg-white rounded-full mr-2 border-2 border-gray-400"></span>
            <h3 className="text-xl font-semibold">White</h3>
          </div>
          <p className="text-3xl font-bold text-primary">{gameState.white_count}</p>
          <p className="text-sm text-gray-400 mt-1">
            {matchConfig?.white_player_type === 'human' ? 'Human' : matchConfig?.white_bot_name}
          </p>
        </div>
      </div>

      {/* Game Board */}
      <div className="card">
        <Board
          board={gameState.board}
          validMoves={gameState.valid_moves}
          onCellClick={handleCellClick}
          gameOver={gameState.game_over}
          currentPlayerType={currentPlayerType}
        />
      </div>

      {/* Controls */}
      <div className="flex justify-center gap-4 mt-6">
        <button
          onClick={handleReturnToMenu}
          className="btn-secondary"
        >
          Return to Menu
        </button>
      </div>

      {/* Message Display */}
      {message && (
        <div className="mt-4 text-center">
          <p className="text-sm text-gray-300 bg-surface-lighter rounded px-4 py-2 inline-block">
            {message}
          </p>
        </div>
      )}

      {/* Connection Status */}
      <div className="mt-4 text-center">
        <p className="text-xs text-gray-500">
          <span className={`inline-block w-2 h-2 rounded-full mr-2 ${connected ? 'bg-green-500' : 'bg-red-500'}`}></span>
          {connected ? 'Connected' : 'Disconnected'}
        </p>
      </div>
    </div>
  );
};

export default GameView;