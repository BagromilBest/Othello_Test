import React, { useState, useEffect, useRef, useCallback } from 'react';

const MainMenu = ({ bots, onStartGame, onBotsUpdated, apiUrl, apiError, onDismissError, isStartingGame = false }) => {
  const [boardSize, setBoardSize] = useState(8);
  const [blackPlayerType, setBlackPlayerType] = useState('human');
  const [blackBotName, setBlackBotName] = useState('');
  const [whitePlayerType, setWhitePlayerType] = useState('bot');
  const [whiteBotName, setWhiteBotName] = useState('');
  const [initTimeout, setInitTimeout] = useState(60);
  const [moveTimeout, setMoveTimeout] = useState(1);
  const [uploadError, setUploadError] = useState('');
  const [uploadSuccess, setUploadSuccess] = useState('');
  const [showManageBots, setShowManageBots] = useState(false);
  const [editingBot, setEditingBot] = useState(null);
  const [newBotName, setNewBotName] = useState('');
  const [manageError, setManageError] = useState('');
  const [manageSuccess, setManageSuccess] = useState('');

  // Modal ref for focus trapping
  const modalRef = useRef(null);
  const closeButtonRef = useRef(null);

  // Close modal handler
  const closeManageBots = useCallback(() => {
    setShowManageBots(false);
    setEditingBot(null);
    setManageError('');
    setManageSuccess('');
  }, []);

  // Handle Escape key to close modal
  useEffect(() => {
    const handleEscKey = (e) => {
      if (e.key === 'Escape' && showManageBots) {
        closeManageBots();
      }
    };

    if (showManageBots) {
      document.addEventListener('keydown', handleEscKey);
      // Focus the close button when modal opens
      closeButtonRef.current?.focus();
    }

    return () => {
      document.removeEventListener('keydown', handleEscKey);
    };
  }, [showManageBots, closeManageBots]);

  // Focus trapping for modal
  useEffect(() => {
    if (!showManageBots || !modalRef.current) return;

    const modal = modalRef.current;
    const focusableElements = modal.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstFocusable = focusableElements[0];
    const lastFocusable = focusableElements[focusableElements.length - 1];

    const handleTabKey = (e) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        // Shift + Tab
        if (document.activeElement === firstFocusable) {
          e.preventDefault();
          lastFocusable?.focus();
        }
      } else {
        // Tab
        if (document.activeElement === lastFocusable) {
          e.preventDefault();
          firstFocusable?.focus();
        }
      }
    };

    modal.addEventListener('keydown', handleTabKey);
    return () => modal.removeEventListener('keydown', handleTabKey);
  }, [showManageBots, bots, editingBot]);

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

  const handleDeleteBot = async (botName) => {
    if (!window.confirm(`Are you sure you want to delete bot "${botName}"?`)) {
      return;
    }

    setManageError('');
    setManageSuccess('');

    try {
      const response = await fetch(`${apiUrl}/api/bots/${encodeURIComponent(botName)}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setManageSuccess(`Bot "${botName}" deleted successfully!`);
        onBotsUpdated();
      } else {
        const error = await response.json();
        setManageError(error.detail || 'Delete failed');
      }
    } catch (error) {
      setManageError('Network error during delete');
    }
  };

  const handleStartRename = (bot) => {
    setEditingBot(bot.name);
    setNewBotName(bot.name);
    setManageError('');
    setManageSuccess('');
  };

  const handleCancelRename = () => {
    setEditingBot(null);
    setNewBotName('');
  };

  const handleSaveRename = async (oldName) => {
    const trimmedName = newBotName.trim();
    if (!trimmedName || trimmedName === oldName) {
      setEditingBot(null);
      return;
    }

    setManageError('');
    setManageSuccess('');

    try {
      const response = await fetch(
        `${apiUrl}/api/bots/${encodeURIComponent(oldName)}/rename`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ new_name: trimmedName }),
        }
      );

      if (response.ok) {
        setManageSuccess(`Bot renamed to "${trimmedName}" successfully!`);
        setEditingBot(null);
        setNewBotName('');
        onBotsUpdated();
      } else {
        const error = await response.json();
        setManageError(error.detail || 'Rename failed');
      }
    } catch (error) {
      setManageError('Network error during rename');
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
      init_timeout: initTimeout,
      move_timeout: moveTimeout,
    };

    onStartGame(config);
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* API Error Banner */}
      {apiError && (
        <div className="bg-red-600 text-white px-4 py-3 mb-4 rounded-lg shadow-md relative">
          <div className="flex items-start justify-between">
            <div className="flex items-center">
              <svg 
                className="w-5 h-5 mr-2 flex-shrink-0" 
                fill="currentColor" 
                viewBox="0 0 20 20"
              >
                <path 
                  fillRule="evenodd" 
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" 
                  clipRule="evenodd" 
                />
              </svg>
              <div>
                <p className="font-medium">Connection Error</p>
                <p className="text-sm mt-1">{apiError}</p>
              </div>
            </div>
            <button 
              onClick={onDismissError} 
              className="ml-4 text-red-200 hover:text-white"
              aria-label="Dismiss error"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path 
                  fillRule="evenodd" 
                  d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" 
                  clipRule="evenodd" 
                />
              </svg>
            </button>
          </div>
        </div>
      )}

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

        {/* Timeout Settings */}
        <div className="grid md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium mb-2">
              Bot Initialization Timeout (seconds)
            </label>
            <input
              type="number"
              min="1"
              max="300"
              value={initTimeout}
              onChange={(e) => setInitTimeout(parseFloat(e.target.value) || 60)}
              className="w-full bg-surface-lighter rounded px-3 py-2 text-white"
            />
            <p className="text-xs text-gray-400 mt-1">Default: 60s</p>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">
              Bot Move Timeout (seconds)
            </label>
            <input
              type="number"
              min="0.1"
              max="60"
              step="0.1"
              value={moveTimeout}
              onChange={(e) => setMoveTimeout(parseFloat(e.target.value) || 1)}
              className="w-full bg-surface-lighter rounded px-3 py-2 text-white"
            />
            <p className="text-xs text-gray-400 mt-1">Default: 1s</p>
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
            disabled={isStartingGame}
            className="w-full text-sm text-gray-400
              file:mr-4 file:py-2 file:px-4
              file:rounded file:border-0
              file:text-sm file:font-semibold
              file:bg-primary file:text-white
              hover:file:bg-primary-dark
              file:cursor-pointer
              disabled:opacity-50 disabled:cursor-not-allowed"
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
          disabled={isStartingGame}
          className="w-full btn-primary text-lg py-3 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isStartingGame ? (
            <>
              <span className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></span>
              Starting...
            </>
          ) : (
            'Start Game'
          )}
        </button>
      </div>

      {/* Available Bots List */}
      {bots.length > 0 && (
        <div className="card mt-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-semibold">Available Bots</h3>
            <button
              onClick={() => setShowManageBots(true)}
              className="btn-primary px-4 py-2 text-sm"
            >
              Manage Bots
            </button>
          </div>
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

      {/* Manage Bots Modal - Improved UI */}
      {showManageBots && (
        <div 
          className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50"
          onClick={(e) => {
            // Close when clicking the backdrop
            if (e.target === e.currentTarget) {
              closeManageBots();
            }
          }}
          role="dialog"
          aria-modal="true"
          aria-labelledby="manage-bots-title"
        >
          <div 
            ref={modalRef}
            className="bg-surface-light rounded-xl shadow-2xl p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto border border-surface-lighter"
          >
            {/* Header with prominent close button */}
            <div className="flex justify-between items-center mb-4">
              <h3 id="manage-bots-title" className="text-2xl font-semibold text-white">Manage Bots</h3>
              <button
                ref={closeButtonRef}
                onClick={closeManageBots}
                className="bg-red-600 hover:bg-red-700 text-white rounded-lg p-2 transition-colors focus:outline-none focus:ring-2 focus:ring-red-400"
                aria-label="Close modal"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>

            {manageError && (
              <p className="mb-3 text-sm text-red-400 bg-red-900/30 px-3 py-2 rounded-lg">{manageError}</p>
            )}
            {manageSuccess && (
              <p className="mb-3 text-sm text-green-400 bg-green-900/30 px-3 py-2 rounded-lg">{manageSuccess}</p>
            )}

            <div className="grid gap-3">
              {bots.map((bot) => (
                <div
                  key={bot.name}
                  className="bg-surface rounded-lg p-4"
                >
                  {editingBot === bot.name ? (
                    <div className="flex gap-2 items-center">
                      <input
                        type="text"
                        value={newBotName}
                        onChange={(e) => setNewBotName(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            handleSaveRename(bot.name);
                          } else if (e.key === 'Escape') {
                            handleCancelRename();
                          }
                        }}
                        className="flex-1 bg-surface-lighter rounded px-3 py-2 text-white"
                        placeholder="New bot name"
                        aria-label="New bot name"
                        autoFocus
                      />
                      <button
                        onClick={() => handleSaveRename(bot.name)}
                        className="btn-primary px-4 py-2"
                      >
                        Save
                      </button>
                      <button
                        onClick={handleCancelRename}
                        className="bg-surface-lighter hover:bg-surface px-4 py-2 rounded"
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <div className="flex justify-between items-center">
                      <div>
                        <div className="font-medium">{bot.name}</div>
                        <div className="text-sm text-gray-400">
                          {bot.type}
                          {bot.upload_time && ` • ${new Date(bot.upload_time).toLocaleDateString()}`}
                        </div>
                      </div>
                      {bot.type === 'uploaded' && (
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleStartRename(bot)}
                            className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm"
                          >
                            Rename
                          </button>
                          <button
                            onClick={() => handleDeleteBot(bot.name)}
                            className="bg-red-600 hover:bg-red-700 px-3 py-1 rounded text-sm"
                          >
                            Delete
                          </button>
                        </div>
                      )}
                      {bot.type === 'builtin' && (
                        <span className="text-xs text-gray-500 italic">Built-in</span>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Bottom close button for easier access */}
            <div className="mt-6 pt-4 border-t border-surface-lighter flex justify-end">
              <button
                onClick={closeManageBots}
                className="bg-primary hover:bg-primary-dark text-white font-medium px-6 py-2 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-primary-light"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MainMenu;