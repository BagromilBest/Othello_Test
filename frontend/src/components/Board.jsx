import React from 'react';

const Board = ({ board, validMoves, onCellClick, gameOver, currentPlayerType }) => {
  const size = board.length;

  // Calculate cell size based on board size
  const getCellSize = () => {
    if (size <= 8) return 'w-16 h-16';
    if (size <= 12) return 'w-12 h-12';
    if (size <= 20) return 'w-8 h-8';
    return 'w-6 h-6';
  };

  const cellSize = getCellSize();

  const isValidMove = (row, col) => {
    return validMoves.some(([r, c]) => r === row && c === col);
  };

  const renderCell = (row, col) => {
    const piece = board[row][col];
    const valid = !gameOver && currentPlayerType === 'human' && isValidMove(row, col);

    return (
      <div
        key={`${row}-${col}`}
        className={`
          ${cellSize}
          border border-surface-lighter
          flex items-center justify-center
          ${valid ? 'cursor-pointer hover:bg-surface-lighter' : ''}
          ${piece === -1 ? 'bg-green-800' : 'bg-green-700'}
          transition-colors duration-200
          relative
        `}
        onClick={() => onCellClick(row, col)}
      >
        {/* Piece */}
        {piece === 0 && (
          <div className="w-[85%] h-[85%] bg-black rounded-full border-2 border-gray-700 shadow-lg animate-[scale-in_0.2s_ease-out]"></div>
        )}
        {piece === 1 && (
          <div className="w-[85%] h-[85%] bg-white rounded-full border-2 border-gray-300 shadow-lg animate-[scale-in_0.2s_ease-out]"></div>
        )}

        {/* Valid move indicator */}
        {valid && (
          <div className="w-1/3 h-1/3 bg-yellow-400 rounded-full opacity-50 hover:opacity-75 transition-opacity"></div>
        )}
      </div>
    );
  };

  return (
    <div className="flex items-center justify-center p-4">
      <div className="inline-block bg-surface-lighter p-2 rounded-lg shadow-2xl">
        <div
          className="grid gap-0"
          style={{
            gridTemplateColumns: `repeat(${size}, minmax(0, 1fr))`,
            maxWidth: size <= 8 ? '512px' : size <= 12 ? '576px' : '640px'
          }}
        >
          {board.map((row, rowIndex) =>
            row.map((_, colIndex) => renderCell(rowIndex, colIndex))
          )}
        </div>
      </div>
    </div>
  );
};

// Add scale-in animation to index.css
const style = document.createElement('style');
style.textContent = `
  @keyframes scale-in {
    from {
      transform: scale(0);
    }
    to {
      transform: scale(1);
    }
  }
`;
document.head.appendChild(style);

export default Board;