import React, { useState, useEffect, useMemo } from 'react';

interface AnswerButtonsProps {
    onClick: (action: { type: string, quantity?: number, faceValue?: number }) => void;
    currentBid: { number: number, face: string } | null;
    previousBid: { number: number, face: string | undefined } | null;
    calledLiar: { status: boolean, caller: string };

}

const AnswerButtons = ({ onClick, currentBid, previousBid, calledLiar }: AnswerButtonsProps) => {
    const diceNumbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    const diceFaces = useMemo(() => ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅'], []);
    const [selectedNumber, setSelectedNumber] = useState<number | null>(null);
    const [selectedFace, setSelectedFace] = useState<string | null>(null);

    useEffect(() => {
        if (previousBid === null) {
            setSelectedNumber(1);
            setSelectedFace(diceFaces[0]);
        } else {
            if (currentBid) {
                setSelectedNumber(currentBid.number);
                const currentFaceIndex = diceFaces.indexOf(currentBid.face);
                if (currentFaceIndex === diceFaces.length - 1) {
                    setSelectedFace(diceFaces[0]);
                } else {
                    setSelectedFace(diceFaces[currentFaceIndex + 1]);
                }
            }
        }
    }, [currentBid, previousBid, diceFaces]);

    const disableNumber = (number: number) => {
        if (!previousBid || previousBid.number === 0) return false; // Allow any number if no previous bid or first bid
        return number <= previousBid.number; // Disable if the number is less than or equal to the previous bid's number
    };

    const disableFace = (face: string) => {
        if (!selectedNumber) return true; // Disable if no number is selected
        if (!previousBid || previousBid.face === undefined) return false; // Allow any face if no previous bid or first bid

        const selectedFaceIndex = diceFaces.indexOf(face);
        const previousFaceIndex = diceFaces.indexOf(previousBid.face);

        if (selectedNumber > previousBid.number) return false; // Allow if the number is greater than the previous bid's number
        if (selectedNumber === previousBid.number) {
            return selectedFaceIndex <= previousFaceIndex; // Disable if the face is less than or equal to the previous bid's face
        }
        return false;
    };

    const handleBidSubmit = () => {
        if (selectedNumber && selectedFace) {
            const faceValue = diceFaces.indexOf(selectedFace) + 1;  // Convert emoji to numeric value
            onClick({ type: 'bid', quantity: selectedNumber, faceValue });
        }
    };

    const handleCallLiarSubmit = () => {
        onClick({ type: 'challenge' });
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
                    className={`p-2 bg-carmine ${calledLiar.status ? 'opacity-50 cursor-not-allowed' : 'hover:bg-dark-red'} text-white font-bold rounded-lg`}>
                    Challenge
                </button>
            </div>
        </div>
    );
};

export default AnswerButtons;