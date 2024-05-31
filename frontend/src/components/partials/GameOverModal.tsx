import React from 'react';

interface GameOverModalProps {
  winner: string;
  onPlayAgain: () => void;
  onGoHome: () => void;
  onClose: () => void;
}

const GameOverModal: React.FC<GameOverModalProps> = ({ winner, onPlayAgain, onGoHome, onClose }) => {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-nyanza p-4 rounded-lg shadow-lg">
        <div className='flex'>
          <h2 className="text-2xl font-bold mb-4">Game Over</h2>
          <button onClick={onClose} className="ml-auto self-start">
            <svg className="h-6 w-6 hover:bg-gray-300" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <p className="mb-4">{winner} wins!</p>
        <div className="flex justify-end space-x-2">
          <button onClick={onPlayAgain} className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded shadow-lg">
            Play Again
          </button>
          <button onClick={onGoHome} className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded shadow-lg">
            Go Home
          </button>
        </div>
      </div>
    </div>
  );
};

export default GameOverModal;
