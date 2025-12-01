import React, { useState, useEffect } from 'react';
import MainMenu from './components/MainMenu';
import GameView from './components/GameView';
import NetworkWarning from './components/NetworkWarning';
import { getApiUrl, getWsUrl } from './utils/network';

const API_URL = getApiUrl();
const WS_URL = getWsUrl();

function App() {
  const [gameState, setGameState] = useState('menu'); // 'menu' | 'playing'
  const [matchId, setMatchId] = useState(null);
  const [websocket, setWebsocket] = useState(null);
  const [bots, setBots] = useState([]);
  const [apiError, setApiError] = useState(null);

  // Fetch available bots on mount
  useEffect(() => {
    fetchBots();
  }, []);

  const fetchBots = async () => {
    try {
      setApiError(null);
      const response = await fetch(`${API_URL}/api/bots`);
      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }
      const data = await response.json();
      setBots(data);
    } catch (error) {
      console.error('Failed to fetch bots:', error);
      setApiError(`Failed to connect to backend at ${API_URL}. ${error.message}`);
    }
  };

  const startGame = (config) => {
    // Store config in sessionStorage so GameView can access it
    try {
      sessionStorage.setItem('matchConfig', JSON.stringify(config));
      setGameState('playing');
      // WebSocket connection will be established in GameView
    } catch (error) {
      console.error('Failed to store game config:', error);
      alert('Failed to start game. Please try again.');
    }
  };

  const returnToMenu = () => {
    if (websocket) {
      websocket.close();
      setWebsocket(null);
    }
    setMatchId(null);
    setGameState('menu');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="container mx-auto px-4 py-8">
        <NetworkWarning />
        <header className="text-center mb-8">
          <h1 className="text-5xl font-bold text-white mb-2">Othello</h1>
          <p className="text-gray-400">Classic strategy board game</p>
        </header>

        {gameState === 'menu' ? (
          <MainMenu
            bots={bots}
            onStartGame={startGame}
            onBotsUpdated={fetchBots}
            apiUrl={API_URL}
            apiError={apiError}
            onDismissError={() => setApiError(null)}
          />
        ) : (
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