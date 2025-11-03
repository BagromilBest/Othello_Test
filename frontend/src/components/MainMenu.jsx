import React, { useState } from 'react';

const MainMenu = ({ bots, onStartGame, onBotsUpdated, apiUrl }) => {
  const [boardSize, setBoardSize] = useState(8);
  const [blackPlayerType, setBlackPlayerType] = useState('human');
  const [blackBotName, setBlackBotName] = useState('');
  const [whitePlayerType, setWhitePlayerType] = useState('bot');
  const [whiteBotName, setWhiteBotName] = useState('');
  const [uploadError, setUploadError] = useState('');
  const [uploadSuccess, setUploadSuccess] = useState('');

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploadError('');
    setUploadSuccess('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${apiUrl}/api/bots/upload`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setUploadSuccess(`Bot "${data.name}" uploaded successfully!`);
        onBotsUpdated();
        event.target.value = ''; // Reset file input
      } else {
        const error = await response.json();
        setUploadError(error.detail || 'Upload failed');
      }
    } catch (error) {
      setUploadError('Network error during upload');
    }
  };

  const handleStartGame = () => {
    // Validate configuration
    if (blackPlayerType === 'bot' && !blackBotName) {
      alert('Please select a bot for Black player');
      return;
    }
    if (whitePlayerType === 'bot' && !whiteBotName) {
      alert('Please select a bot for White player');
      return;
    }

    const config = {
      board_size: boardSize,
      black_player_type: blackPlayerType,
      black_bot_name: blackPlayerType === 'bot' ? blackBotName : null,
      white_player_type: whitePlayerType,
      white_bot_name: whitePlayerType === 'bot' ? whiteBotName : null,
    };

    onStartGame(config);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="card">
        <h2 className="text-3xl font-bold mb-6 text-center">Game Setup</h2>

        {/* Board Size */}
        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">
            Board Size: {boardSize} × {boardSize}
          </label>
          <input
            type="range"
            min="4"
            max="100"
            value={boardSize}
            onChange={(e) => setBoardSize(parseInt(e.target.value))}
            className="w-full h-2 bg-surface-lighter rounded-lg appearance-none cursor-pointer"
          />
          <div className="flex justify-between text-xs text-gray-400 mt-1">
            <span>4×4</span>
            <span>100×100</span>
          </div>
        </div>

        {/* Player Configuration */}
        <div className="grid md:grid-cols-2 gap-6 mb-6">
          {/* Black Player */}
          <div className="bg-surface rounded-lg p-4">
            <h3 className="text-xl font-semibold mb-4 flex items-center">
              <span className="w-6 h-6 bg-black rounded-full mr-2 border-2 border-white"></span>
              Black Player
            </h3>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Type</label>
              <select
                value={blackPlayerType}
                onChange={(e) => setBlackPlayerType(e.target.value)}
                className="w-full bg-surface-lighter rounded px-3 py-2 text-white"
              >
                <option value="human">Human</option>
                <option value="bot">Bot</option>
              </select>
            </div>
            {blackPlayerType === 'bot' && (
              <div>
                <label className="block text-sm font-medium mb-2">Select Bot</label>
                <select
                  value={blackBotName}
                  onChange={(e) => setBlackBotName(e.target.value)}
                  className="w-full bg-surface-lighter rounded px-3 py-2 text-white"
                >
                  <option value="">-- Choose a bot --</option>
                  {bots.map((bot) => (
                    <option key={bot.name} value={bot.name}>
                      {bot.name} ({bot.type})
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>

          {/* White Player */}
          <div className="bg-surface rounded-lg p-4">
            <h3 className="text-xl font-semibold mb-4 flex items-center">
              <span className="w-6 h-6 bg-white rounded-full mr-2 border-2 border-gray-400"></span>
              White Player
            </h3>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Type</label>
              <select
                value={whitePlayerType}
                onChange={(e) => setWhitePlayerType(e.target.value)}
                className="w-full bg-surface-lighter rounded px-3 py-2 text-white"
              >
                <option value="human">Human</option>
                <option value="bot">Bot</option>
              </select>
            </div>
            {whitePlayerType === 'bot' && (
              <div>
                <label className="block text-sm font-medium mb-2">Select Bot</label>
                <select
                  value={whiteBotName}
                  onChange={(e) => setWhiteBotName(e.target.value)}
                  className="w-full bg-surface-lighter rounded px-3 py-2 text-white"
                >
                  <option value="">-- Choose a bot --</option>
                  {bots.map((bot) => (
                    <option key={bot.name} value={bot.name}>
                      {bot.name} ({bot.type})
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>
        </div>

        {/* Bot Upload */}
        <div className="bg-surface rounded-lg p-4 mb-6">
          <h3 className="text-xl font-semibold mb-4">Upload New Bot</h3>
          <p className="text-sm text-gray-400 mb-3">
            Upload a Python file implementing the bot interface (see README for details)
          </p>
          <input
            type="file"
            accept=".py"
            onChange={handleFileUpload}
            className="w-full text-sm text-gray-400
              file:mr-4 file:py-2 file:px-4
              file:rounded file:border-0
              file:text-sm file:font-semibold
              file:bg-primary file:text-white
              hover:file:bg-primary-dark
              file:cursor-pointer"
          />
          {uploadError && (
            <p className="mt-2 text-sm text-red-400">{uploadError}</p>
          )}
          {uploadSuccess && (
            <p className="mt-2 text-sm text-green-400">{uploadSuccess}</p>
          )}
        </div>

        {/* Start Button */}
        <button
          onClick={handleStartGame}
          className="w-full btn-primary text-lg py-3"
        >
          Start Game
        </button>
      </div>

      {/* Available Bots List */}
      {bots.length > 0 && (
        <div className="card mt-6">
          <h3 className="text-xl font-semibold mb-4">Available Bots</h3>
          <div className="grid gap-2">
            {bots.map((bot) => (
              <div
                key={bot.name}
                className="bg-surface rounded px-4 py-2 flex justify-between items-center"
              >
                <span className="font-medium">{bot.name}</span>
                <span className="text-sm text-gray-400">
                  {bot.type}
                  {bot.upload_time && ` • ${new Date(bot.upload_time).toLocaleDateString()}`}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default MainMenu;