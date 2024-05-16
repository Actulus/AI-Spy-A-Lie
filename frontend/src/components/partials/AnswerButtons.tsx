import React, { useState } from 'react';

interface AnswerButtonsProps {
    onClick: (answer: string) => void;
}

const AnswerButtons = ({ onClick }: AnswerButtonsProps) => {
    const diceNumbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    const diceFaces = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅'];
    const [selectedNumber, setSelectedNumber] = useState<number | null>(null);
    const [selectedFace, setSelectedFace] = useState<string | null>(null);

    const handleBidSubmit = () => {
        if (selectedNumber && selectedFace) {
            // Format the answer to include both selected number and face
            onClick(`Number of dice: ${selectedNumber}, Dice face: ${selectedFace}`);
        } 
    };

    const handleCallLiarSubmit = () => {
        onClick('Call Liar');
    }

    return (
        <div className="flex flex-col lg:flex-row justify-center items-center">
            <div className="flex flex-col items-center">
                <p className="text-white text-2xl">Number</p>
                <div className="flex flex-wrap outline outline-white rounded-lg">
                    {diceNumbers.map((number, index) => (
                        <button
                            key={index}
                            onClick={() => setSelectedNumber(number)}
                            className={`m-2 p-2 ${selectedNumber === number ? 'bg-spring-green' : 'bg-nyanza'} text-black rounded-lg`}>
                            {number}
                        </button>
                    ))}
                </div>
            </div>
            <div className="flex flex-col items-center ml-2">
                <p className="text-white text-2xl">Face</p>
                <div className="flex flex-wrap outline outline-white rounded-lg">
                    {diceFaces.map((face, index) => (
                        <button
                            key={index}
                            onClick={() => setSelectedFace(face)}
                            className={`m-2 p-2 ${selectedFace === face ? 'bg-spring-green' : 'bg-nyanza'} text-black rounded-lg`}>
                            {face}
                        </button>
                    ))}
                </div>
            </div>
            <div className='flex lg:flex-col m-2 mt-5 gap-2'>
                <button
                    onClick={handleBidSubmit}
                    disabled={!selectedNumber || !selectedFace} // Disable button until both selections are made
                    className={`p-2 bg-spring-green ${(!selectedNumber || !selectedFace) ? 'opacity-50 cursor-not-allowed' : 'hover:bg-light-spring-green'} text-white font-bold rounded-lg`}>
                    Submit Bid
                </button>
                <button
                    onClick={handleCallLiarSubmit}
                    className={`p-2 bg-carmine text-white font-bold rounded-lg`}>
                    Call Liar
                </button>
            </div>
        </div>
    );
};

export default AnswerButtons;
