import React, { useState, useEffect, useRef, useCallback } from 'react';
import Board from './Board';
import ErrorAlert from './ErrorAlert';

const GameView = ({ onReturnToMenu, wsUrl, onInitStageChange, onInitComplete, onInitError }) => {
  const [gameState, setGameState] = useState(null);
  const [matchId, setMatchId] = useState(null);
  const [message, setMessage] = useState('');
  const [connected, setConnected] = useState(false);
  const [matchConfig, setMatchConfig] = useState(null);
  const [wsError, setWsError] = useState(null);
  const wsRef = useRef(null);
  const initReportedRef = useRef(false);
  const mountedRef = useRef(false);
  const connectingRef = useRef(false);

  // Store callbacks in refs to avoid stale closures
  const onInitStageChangeRef = useRef(onInitStageChange);
  const onInitCompleteRef = useRef(onInitComplete);
  const onInitErrorRef = useRef(onInitError);

  // Update refs when props change
  useEffect(() => {
    onInitStageChangeRef.current = onInitStageChange;
    onInitCompleteRef.current = onInitComplete;
    onInitErrorRef.current = onInitError;
  }, [onInitStageChange, onInitComplete, onInitError]);

  // Report initialization stage changes using ref
  const reportStage = useCallback((stage, previousStage) => {
    if (onInitStageChangeRef.current) {
      onInitStageChangeRef.current(stage, previousStage);
    }
  }, []);

  useEffect(() => {
    // Prevent double-mounting issues in React Strict Mode
    if (mountedRef.current || connectingRef.current) {
      return;
    }
    mountedRef.current = true;

    // Get match config from sessionStorage (set by MainMenu)
    const config = JSON.parse(sessionStorage.getItem('matchConfig') || 'null');
    if (config) {
      setMatchConfig(config);
      reportStage('connecting_websocket', 'starting');
      connectWebSocket(config);
    }

    return () => {
      // Only close if we're actually unmounting (not just Strict Mode re-run)
      // Check if we have an active connection before closing
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        console.log('[WS] Closing WebSocket on unmount');
        wsRef.current.close();
      }
      mountedRef.current = false;
    };
  }, []);

  const connectWebSocket = (config) => {
    // Guard against multiple connection attempts
    if (connectingRef.current || wsRef.current) {
      console.log('[WS] Already connecting or connected, skipping');
      return;
    }
    connectingRef.current = true;

    const clientId = Math.random().toString(36).substring(7);
    console.log('[WS] Attempting connection to:', `${wsUrl}/ws/${clientId}`);
    
    let ws;
    try {
      ws = new WebSocket(`${wsUrl}/ws/${clientId}`);
    } catch (error) {
      const errorMsg = `Failed to create WebSocket connection: ${error.message}`;
      console.error('[WS] Connection error:', error);
      setWsError(errorMsg);
      connectingRef.current = false;
      if (onInitErrorRef.current) {
        onInitErrorRef.current(errorMsg);
      }
      return;
    }

    ws.onopen = () => {
      console.log('[WS] WebSocket connected');
      connectingRef.current = false;
      setConnected(true);
      setMessage('Connected to server');
      setWsError(null);

      reportStage('creating_match', 'connecting_websocket');

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
      console.error('[WS] WebSocket error:', error);
      const errorMsg = 'WebSocket connection error. Check your network and try again.';
      setMessage('Connection error');
      setWsError(errorMsg);
      connectingRef.current = false;
      if (onInitErrorRef.current && !initReportedRef.current) {
        onInitErrorRef.current(errorMsg);
      }
    };

    ws.onclose = (event) => {
      console.log('[WS] WebSocket disconnected, code:', event.code);
      setConnected(false);
      setMessage('Disconnected from server');
      connectingRef.current = false;
      
      // Only report error if this is an unexpected close during initialization
      if (!initReportedRef.current && !gameState && onInitErrorRef.current) {
        const errorMsg = `WebSocket closed unexpectedly (code: ${event.code}). Please retry.`;
        setWsError(errorMsg);
        onInitErrorRef.current(errorMsg);
      }
    };

    wsRef.current = ws;
  };

  const handleWebSocketMessage = (data) => {
    console.log('[WS] Received:', data);

    switch (data.type) {
      case 'match_created':
        setMatchId(data.match_id);
        setMessage('Match created');
        reportStage('waiting_server', 'creating_match');
        break;

      case 'game_state':
        setGameState(data.state);
        if (data.state.message) {
          setMessage(data.state.message);
        }
        
        // Report initialization complete on first game state
        if (!initReportedRef.current && onInitCompleteRef.current) {
          initReportedRef.current = true;
          reportStage('ready', 'waiting_server');
          onInitCompleteRef.current();
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
        console.error('[WS] Server error:', data.message);
        if (onInitErrorRef.current && !initReportedRef.current) {
          onInitErrorRef.current(`Server error: ${data.message}`);
        }
        break;

      case 'bot_error':
        setMessage(`Bot Error: ${data.message}`);
        console.error('[WS] Bot error:', data.message);
        if (onInitErrorRef.current && !initReportedRef.current) {
          onInitErrorRef.current(`Bot initialization failed: ${data.message}`);
        }
        break;

      default:
        console.log('[WS] Unknown message type:', data.type);
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

  const handleTogglePause = () => {
    if (!matchId || !wsRef.current) {
      return;
    }

    wsRef.current.send(JSON.stringify({
      type: 'toggle_pause',
      match_id: matchId,
    }));
  };

  const handleDismissError = () => {
    setWsError(null);
  };

  if (!gameState) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px]">
        {wsError && (
          <div className="mb-4 max-w-md w-full">
            <ErrorAlert
              type="error"
              title="Connection Error"
              message={wsError}
              action="Retry"
              onAction={handleReturnToMenu}
              onDismiss={handleDismissError}
            />
          </div>
        )}
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
      {/* WebSocket Error Alert */}
      {wsError && (
        <div className="mb-4">
          <ErrorAlert
            type="error"
            title="Connection Error"
            message={wsError}
            onDismiss={handleDismissError}
          />
        </div>
      )}

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
          {gameState.black_init_time_ms != null && matchConfig?.black_player_type === 'bot' && (
            <p className="text-xs text-green-400 mt-1">
              Init: {gameState.black_init_time_ms.toFixed(2)}ms
            </p>
          )}
        </div>

        {/* Status */}
        <div className="card text-center">
          <h3 className="text-sm font-medium text-gray-400 mb-2">Status</h3>
          <p className="text-lg font-semibold">
            {gameState.game_over ? (
              <span className="text-green-400">{message}</span>
            ) : gameState.paused ? (
              <span className="text-yellow-400">⏸ Paused</span>
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
              {gameState.bot_thinking_time_ms != null && (
                <p className="text-xs text-blue-400 mt-1">
                  {/* Show thinking time for the player who just moved (previous player) */}
                  {gameState.current_player === 0
                    ? (matchConfig?.white_player_type === 'human' ? 'Human' : matchConfig?.white_bot_name)
                    : (matchConfig?.black_player_type === 'human' ? 'Human' : matchConfig?.black_bot_name)
                  } took: {gameState.bot_thinking_time_ms.toFixed(2)}ms
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
          {gameState.white_init_time_ms != null && matchConfig?.white_player_type === 'bot' && (
            <p className="text-xs text-green-400 mt-1">
              Init: {gameState.white_init_time_ms.toFixed(2)}ms
            </p>
          )}
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
          lastMove={gameState.last_move}
          lastFlipped={gameState.last_flipped}
          stablePieces={gameState.stable_pieces || []}
          paused={gameState.paused}
        />
      </div>

      {/* Controls */}
      <div className="flex justify-center gap-4 mt-6">
        {!gameState.game_over && (
          <button
            onClick={handleTogglePause}
            className={gameState.paused ? "btn-primary" : "btn-secondary"}
          >
            {gameState.paused ? '▶ Resume' : '⏸ Pause'}
          </button>
        )}
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