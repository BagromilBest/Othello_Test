import React, { useState, useEffect, useCallback } from 'react';
import MainMenu from './components/MainMenu';
import GameView from './components/GameView';
import NetworkWarning from './components/NetworkWarning';
import InitializationProgress, { INIT_STAGES } from './components/InitializationProgress';
import ErrorAlert from './components/ErrorAlert';
import { getApiUrl, getWsUrl } from './utils/network';
import { startStage, endStage, clearTimings, logTimingSummary, STAGES } from './utils/timing';

const API_URL = getApiUrl();
const WS_URL = getWsUrl();

// Max retries for network operations
const MAX_RETRIES = 3;
const RETRY_DELAY_BASE = 1000; // 1 second base delay

function App() {
  const [gameState, setGameState] = useState('menu'); // 'menu' | 'initializing' | 'playing'
  const [matchId, setMatchId] = useState(null);
  const [websocket, setWebsocket] = useState(null);
  const [bots, setBots] = useState([]);
  const [apiError, setApiError] = useState(null);
  
  // Initialization state
  const [initStage, setInitStage] = useState('starting');
  const [initError, setInitError] = useState(null);
  const [stageDurations, setStageDurations] = useState({});
  const [pendingConfig, setPendingConfig] = useState(null);

  // Fetch available bots on mount
  useEffect(() => {
    fetchBots();
  }, []);

  // Helper function for exponential backoff retry
  const withRetry = async (operation, maxRetries = MAX_RETRIES) => {
    let lastError;
    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        return await operation();
      } catch (error) {
        lastError = error;
        if (attempt < maxRetries - 1) {
          const delay = RETRY_DELAY_BASE * Math.pow(2, attempt);
          console.warn(`[Retry] Attempt ${attempt + 1} failed, retrying in ${delay}ms...`, error.message);
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }
    throw lastError;
  };

  const fetchBots = async () => {
    try {
      setApiError(null);
      const response = await withRetry(async () => {
        const res = await fetch(`${API_URL}/api/bots`);
        if (!res.ok) {
          throw new Error(`HTTP error: ${res.status}`);
        }
        return res;
      });
      const data = await response.json();
      setBots(data);
    } catch (error) {
      console.error('Failed to fetch bots:', error);
      setApiError(`Failed to connect to backend at ${API_URL}. ${error.message}`);
    }
  };

  const startGame = useCallback((config) => {
    // Clear previous timing data
    clearTimings();
    setStageDurations({});
    setInitError(null);
    
    // Record start time
    startStage(STAGES.START_GAME_CLICK);
    
    // Store config in sessionStorage so GameView can access it
    try {
      sessionStorage.setItem('matchConfig', JSON.stringify(config));
      setPendingConfig(config);
      setInitStage('starting');
      setGameState('initializing');
    } catch (error) {
      console.error('Failed to store game config:', error);
      setInitError('Failed to start game. Please try again.');
    }
  }, []);

  // Update stage and record duration
  const updateInitStage = useCallback((newStage, previousStage) => {
    if (previousStage) {
      const duration = endStage(previousStage);
      if (duration !== null) {
        setStageDurations(prev => ({ ...prev, [previousStage]: duration }));
      }
    }
    if (newStage) {
      startStage(newStage);
    }
    setInitStage(newStage);
  }, []);

  // Called by GameView when initialization is complete
  const handleInitComplete = useCallback(() => {
    // Record final stage duration using STAGES constant
    const finalStage = STAGES.WEBSOCKET_CONNECT;
    const duration = endStage(finalStage);
    if (duration !== null) {
      setStageDurations(prev => ({ ...prev, [finalStage]: duration }));
    }
    
    // Log timing summary
    logTimingSummary();
    
    // Transition to playing state
    setGameState('playing');
  }, []);

  // Called by GameView on initialization error
  const handleInitError = useCallback((error) => {
    console.error('[Init] Error:', error);
    setInitError(error);
  }, []);

  const handleRetryInit = useCallback(() => {
    if (pendingConfig) {
      startGame(pendingConfig);
    }
  }, [pendingConfig, startGame]);

  const handleCancelInit = useCallback(() => {
    sessionStorage.removeItem('matchConfig');
    setPendingConfig(null);
    setInitStage('starting');
    setInitError(null);
    setGameState('menu');
    clearTimings();
    setStageDurations({});
  }, []);

  const returnToMenu = useCallback(() => {
    if (websocket) {
      websocket.close();
      setWebsocket(null);
    }
    setMatchId(null);
    setPendingConfig(null);
    setInitStage('starting');
    setInitError(null);
    setGameState('menu');
    clearTimings();
    setStageDurations({});
  }, [websocket]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="container mx-auto px-4 py-8">
        <NetworkWarning />
        <header className="text-center mb-8">
          <h1 className="text-5xl font-bold text-white mb-2">Othello</h1>
          <p className="text-gray-400">Classic strategy board game</p>
        </header>

        {gameState === 'menu' && (
          <MainMenu
            bots={bots}
            onStartGame={startGame}
            onBotsUpdated={fetchBots}
            apiUrl={API_URL}
            apiError={apiError}
            onDismissError={() => setApiError(null)}
            isStartingGame={false}
          />
        )}

        {gameState === 'initializing' && (
          <>
            <MainMenu
              bots={bots}
              onStartGame={startGame}
              onBotsUpdated={fetchBots}
              apiUrl={API_URL}
              apiError={apiError}
              onDismissError={() => setApiError(null)}
              isStartingGame={true}
            />
            <InitializationProgress
              currentStage={initStage}
              error={initError}
              onRetry={handleRetryInit}
              onCancel={handleCancelInit}
              stageDurations={stageDurations}
            />
            {/* Hidden GameView for initialization */}
            <div className="hidden">
              <GameView
                onReturnToMenu={returnToMenu}
                wsUrl={WS_URL}
                onInitStageChange={updateInitStage}
                onInitComplete={handleInitComplete}
                onInitError={handleInitError}
              />
            </div>
          </>
        )}

        {gameState === 'playing' && (
          <GameView
            onReturnToMenu={returnToMenu}
            wsUrl={WS_URL}
          />
        )}
      </div>
    </div>
  );
}

export default App;