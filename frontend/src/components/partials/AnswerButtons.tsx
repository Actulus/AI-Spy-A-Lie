import React, { useState, useEffect } from 'react';

interface AnswerButtonsProps {
    onClick: (answer: string) => void;
    currentBid: { number: number, face: string } | null;
    previousBid: { number: number, face: string } | null;
    calledLiar: {status: boolean, caller: string};
    
}

const AnswerButtons = ({ onClick, currentBid, previousBid, calledLiar }: AnswerButtonsProps) => {
    const diceNumbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    const diceFaces = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅'];
    const [selectedNumber, setSelectedNumber] = useState<number | null>(null);
    const [selectedFace, setSelectedFace] = useState<string | null>(null);

    useEffect(() => {
        setSelectedNumber(null);
        setSelectedFace(null);
    }, [previousBid]);

    const disableNumber = (number: number) => {
        if (!previousBid) return false;
        return number < previousBid.number;
    };

    const disableFace = (face: string) => {
        if (!selectedNumber) return true;
        if (selectedNumber > (previousBid?.number || 0)) return false;
        if (previousBid && selectedNumber === previousBid.number) {
            return diceFaces.indexOf(face) <= diceFaces.indexOf(previousBid.face);
        }
        return false;
    };

    const handleBidSubmit = () => {
        if (selectedNumber && selectedFace) {
            onClick(`Number of dice: ${selectedNumber}, Dice face: ${selectedFace}`);
        }
    };

    const handleCallLiarSubmit = () => {
        onClick('Call Liar');
    };

    return (
        <div className="flex flex-col lg:flex-row justify-center items-center gap-2">
            <div className="flex flex-col items-center">
                <p className="text-white text-2xl">Number</p>
                <div className="flex flex-wrap outline outline-white rounded-lg">
                    {diceNumbers.map((number, index) => (
                        <button
                            key={index}
                            onClick={() => setSelectedNumber(number)}
                            disabled={disableNumber(number)}
                            className={`m-2 p-2 ${selectedNumber === number ? 'bg-spring-green' : 'bg-nyanza'} ${disableNumber(number) ? 'opacity-50 cursor-not-allowed' : 'text-black'} rounded-lg`}>
                            {number}
                        </button>
                    ))}
                </div>
            </div>
            <div className="flex flex-col items-center">
                <p className="text-white text-2xl">Face</p>
                <div className="flex flex-wrap outline outline-white rounded-lg">
                    {diceFaces.map((face, index) => (
                        <button
                            key={index}
                            onClick={() => setSelectedFace(face)}
                            disabled={disableFace(face)}
                            className={`m-2 p-2 ${selectedFace === face ? 'bg-spring-green' : 'bg-nyanza'} ${disableFace(face) ? 'opacity-50 cursor-not-allowed' : 'text-black'} rounded-lg`}>
                            {face}
                        </button>
                    ))}
                </div>
            </div>
            <div className='flex lg:flex-col m-2 mt-5 gap-2'>
                <button
                    onClick={handleBidSubmit}
                    disabled={!selectedNumber || !selectedFace || disableFace(selectedFace)}
                    className={`p-2 bg-spring-green ${(!selectedNumber || !selectedFace || disableFace(selectedFace)) ? 'opacity-50 cursor-not-allowed' : 'hover:bg-light-spring-green'} text-white font-bold rounded-lg`}>
                    Submit Bid
                </button>
                <button
                    onClick={handleCallLiarSubmit}
                    disabled={calledLiar.status}
                    className={`p-2 bg-carmine ${calledLiar ? 'opacity-50 cursor-not-allowed' : 'hover:bg-dark-red'} text-white font-bold rounded-lg`}>
                    Call Liar
                </button>
            </div>
        </div>
    );
};

export default AnswerButtons;