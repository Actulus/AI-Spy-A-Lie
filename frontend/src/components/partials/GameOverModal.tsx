import React from 'react';

interface GameOverModalProps {
  winner: string;
  onPlayAgain: () => void;
  onGoHome: () => void;
}

const GameOverModal: React.FC<GameOverModalProps> = ({ winner, onPlayAgain, onGoHome }) => {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white p-4 rounded-lg shadow-lg">
        <h2 className="text-2xl font-bold mb-4">Game Over</h2>
        <p className="mb-4">{winner} wins!</p>
        <div className="flex justify-end space-x-2">
          <button onClick={onPlayAgain} className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded">
            Play Again
          </button>
          <button onClick={onGoHome} className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded">
            Go Home
          </button>
        </div>
      </div>
    </div>
  );
};

export default GameOverModal;
