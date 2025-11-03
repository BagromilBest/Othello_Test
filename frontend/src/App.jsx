import React, { useState, useEffect } from 'react';
import MainMenu from './components/MainMenu';
import GameView from './components/GameView';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

function App() {
  const [gameState, setGameState] = useState('menu'); // 'menu' | 'playing'
  const [matchId, setMatchId] = useState(null);
  const [websocket, setWebsocket] = useState(null);
  const [bots, setBots] = useState([]);

  // Fetch available bots on mount
  useEffect(() => {
    fetchBots();
  }, []);

  const fetchBots = async () => {
    try {
      const response = await fetch(`${API_URL}/api/bots`);
      const data = await response.json();
      setBots(data);
    } catch (error) {
      console.error('Failed to fetch bots:', error);
    }
  };

  const startGame = (config) => {
    setGameState('playing');
    // WebSocket connection will be established in GameView
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