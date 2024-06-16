import React, { useEffect, useState, useRef, useCallback } from "react";
import { io, Socket } from "socket.io-client";
import { useParams } from "react-router-dom";
import { useKindeAuth } from '@kinde-oss/kinde-auth-react';
import RolledDiceFaces from "./partials/RolledDiceFaces";
import AnswerButtons from "./partials/AnswerButtons";
import GameOverModal from "./partials/GameOverModal";
import { Message } from "./partials/Message";
import TutorialPopUpModal from "./partials/TutorialPopUpModal";

interface GameState {
  dice_count: { [key: number]: number };
  players: { [key: number]: number[] };
  current_bid: [number, number];
  current_player: number;
  last_action_was_challenge: boolean;
  player_names: { [key: number]: string };
  scores: { [key: number]: number };
}

const diceFaces = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅'];

const GamePage: React.FC = () => {
  const { difficulty } = useParams<{ difficulty: string }>();
  const socket = useRef<Socket>();
  const { user } = useKindeAuth();

  const userName = `${user?.given_name} ${user?.family_name}`;
  const aiName = `${difficulty?.charAt(0).toUpperCase() + difficulty!.slice(1)}AI`;
  const userPic = user?.picture || "/cat_pfp.png";
  const aiPic = '/AI_Pic.png';

  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [messages, setMessages] = useState<Array<{ type: 'join' | 'chat'; sid: string; message?: string }>>([]);
  const [sidMaps, setSidMaps] = useState<{ name: string; pic: string; sid: string; isAI: boolean }[]>([]);
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [isFirstBid, setIsFirstBid] = useState<boolean>(true);

  const [isGameOver, setIsGameOver] = useState<boolean>(false);
  const [winner, setWinner] = useState<string | null>(null);

  const endOfMessagesRef = useRef<HTMLDivElement | null>(null);

  const isTutorialMode = difficulty === 'tutorial';
  const [isTutorialModalOpen, setIsTutorialModalOpen] = useState(isTutorialMode);
  const [currentStep, setCurrentStep] = useState(0)

  const steps = [
    { title: 'Score', description: 'Here you can see your score.', highlight: 'score' },
    { title: 'Connection status', description: 'Here you can see your connection status.', highlight: 'status' },
    { title: 'Messages', description: 'Here you can see the gameplay.', highlight: 'messages' },
    { title: 'Dices', description: 'Here you can see your dices.', highlight: 'dice' },
    { title: 'Action', description: 'Here you can make your choice of either making a bid or challenging the opponent. When making a bid make sure that you choose the number of dices first and then the face.', highlight: 'answer-buttons' },
  ];

  const scoreRef = useRef<HTMLDivElement>(null);
  const statusRef = useRef<HTMLDivElement>(null);
  const messagesRef = useRef<HTMLDivElement>(null);
  const diceRef = useRef<HTMLDivElement>(null);
  const answerButtonsRef = useRef<HTMLDivElement>(null);

  const highlightRefs: { [key: string]: React.RefObject<HTMLElement> } = {
    score: scoreRef,
    status: statusRef,
    messages: messagesRef,
    dice: diceRef,
    'answer-buttons': answerButtonsRef,
  };

  const handleGameOver = useCallback(({ roomSocketId, kindeUUID, userScore, AIBotType, AIScore   }: {
    roomSocketId: string,
    kindeUUID: string,
    userScore: number,
    AIBotType: string,
    AIScore: number,
  }) => {
    setIsGameOver(true);

    fetch(`${import.meta.env.VITE_BACKEND_URL}/api/match`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
          "socket_id": roomSocketId,
          "users": [{"kinde_uuid": kindeUUID, "score": userScore}],
          "ai_opponents": [{"ai_type": AIBotType, "score": AIScore}],
        }),
    })
      .then(response => response.json())
      .catch((error) => {
        console.error('Error:', error);
      });
  }, [setIsGameOver]);

  useEffect(() => {
    const connectSocket = () => {
      const socketInstance = io(import.meta.env.VITE_BACKEND_URL, {
        path: import.meta.env.VITE_REACT_APP_SOCKET_PATH,
        query: { room: difficulty },
      });

      socketInstance.on('connect', () => {
        setIsConnected(true);
        setSidMaps([{ name: userName, pic: userPic as string, sid: socketInstance.id as string, isAI: false }]);
        socketInstance.emit('player_names', { userName, aiName });
      });

      socketInstance.on('disconnect', () => {
        setIsConnected(false);
      });

      socketInstance.on('join', (data: { sid: string }) => {
        setMessages(prevMessages => [...prevMessages, { ...data, type: 'join' }]);
        if (data.sid.startsWith('ai_')) {
          setSidMaps(prevMaps => [...prevMaps, { name: aiName, pic: aiPic, sid: data.sid, isAI: true }]);
        } else if (data.sid !== socketInstance.id) {
          setSidMaps(prevMaps => [...prevMaps, { name: `User ${data.sid.slice(-4)}`, pic: userPic, sid: data.sid, isAI: false }]);
        }
      });

      socketInstance.on('chat', (data: { sid: string; message: string }) => {
        setMessages(prevMessages => [...prevMessages, { ...data, type: 'chat' }]);
      });

      socketInstance.on('game_update', (data: GameState) => {
        setGameState(data);

        if (data.dice_count[1] === 0 || data.dice_count[2] === 0) {
          const winner = data.dice_count[1] === 0 ? data.player_names[2] : data.player_names[1];
          setWinner(winner);
          handleGameOver({
            roomSocketId: socketInstance.id!,
            kindeUUID: user!.id!,
            userScore: data.scores[1],
            AIBotType: difficulty!,
            AIScore: data.scores[2],
          });
        }
      });

      socketInstance.on('game_over', (data: { winner: string }) => {
        setIsGameOver(true);
        setWinner(data.winner);
      });

      socket.current = socketInstance;
    };

    connectSocket();

    return () => {
      if (socket.current) {
        socket.current.disconnect();
      }
    };
  }, [difficulty, userName, aiName, userPic, aiPic, handleGameOver, user]);


  useEffect(() => {
    if (endOfMessagesRef.current) {
      endOfMessagesRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleUserAction = (action: { type: string, quantity?: number, faceValue?: number }) => {
    if (socket.current) {
      if (action.type === 'bid' && action.quantity !== undefined && action.faceValue !== undefined) {
        const message = `bid ${action.quantity} ${action.faceValue}`;
        socket.current.emit('chat', message);
      } else if (action.type === 'challenge') {
        socket.current.emit('chat', 'challenge');
      }
    }
    setIsFirstBid(false);
  };

  // Helper function to convert bid tuple to the expected format
  const convertBid = (bid: [number, number] | null) => {
    if (!bid) return null;
    return { number: bid[0], face: bid[1] !== 0 ? diceFaces[bid[1] - 1] : '⚀' }; // Convert face value to emoji
  };

  const handlePlayAgain = async () => {
    // Reset the game state
    setIsGameOver(false);
    setIsFirstBid(true);
    setMessages([]);
    setGameState(null);
    setWinner(null);

    // Disconnect the current socket
    if (socket.current) {
      await socket.current.disconnect();
    }

    // Establish a new socket connection after a short delay
    setTimeout(() => {
      const socketInstance = io(import.meta.env.VITE_BACKEND_URL, {
        path: import.meta.env.VITE_REACT_APP_SOCKET_PATH,
        query: { room: difficulty },
      });

      socketInstance.on('connect', () => {
        setIsConnected(true);
        setSidMaps([{ name: userName, pic: userPic as string, sid: socketInstance.id as string, isAI: false }]);
        socketInstance.emit('player_names', { userName, aiName });
      });

      socketInstance.on('disconnect', () => {
        setIsConnected(false);
      });

      socketInstance.on('join', (data: { sid: string }) => {
        setMessages(prevMessages => [...prevMessages, { ...data, type: 'join' }]);
        if (data.sid.startsWith('ai_')) {
          setSidMaps(prevMaps => [...prevMaps, { name: aiName, pic: aiPic, sid: data.sid, isAI: true }]);
        } else if (data.sid !== socketInstance.id) {
          setSidMaps(prevMaps => [...prevMaps, { name: `User ${data.sid.slice(-4)}`, pic: userPic, sid: data.sid, isAI: false }]);
        }
      });

      socketInstance.on('chat', (data: { sid: string; message: string }) => {
        setMessages(prevMessages => [...prevMessages, { ...data, type: 'chat' }]);
      });

      socketInstance.on('game_update', (data: GameState) => {
        setGameState(data);

        if (data.dice_count[1] === 0 || data.dice_count[2] === 0) {
          const winner = data.dice_count[1] === 0 ? data.player_names[2] : data.player_names[1];
          setWinner(winner);
          handleGameOver({
            roomSocketId: socketInstance.id!,
            kindeUUID: user!.id!,
            userScore: data.scores[1],
            AIBotType: difficulty!,
            AIScore: data.scores[2],
          });
        }
      });

      socketInstance.on('game_over', (data: { winner: string }) => {
        setIsGameOver(true);
        setWinner(data.winner);
      });

      socket.current = socketInstance;
    }, 100);
  };


  const handleGoHome = () => {
    window.location.href = '/home';
  };

  const handleCloseModal = () => {
    setIsGameOver(false);
  }

  const handleNextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePreviousStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  return (
    <div className="relative flex flex-col p-4">
      {isTutorialMode && (
        <TutorialPopUpModal
          steps={steps}
          isOpen={isTutorialModalOpen}
          onClose={() => setIsTutorialModalOpen(false)}
          currentStep={currentStep}
          handleNextStep={handleNextStep}
          handlePreviousStep={handlePreviousStep}
          highlightRef={highlightRefs[steps[currentStep].highlight]}
        />
      )}
      <div className="flex justify-between gap-1">
        <div ref={scoreRef} className={`flex flex-col bg-spring-green rounded-lg p-2 w-fit h-fit text-lg font-bold`}>
          <h3 className="text-xl font-bold">Your score: {gameState?.scores[1]}</h3>
          <h3 className="text-xl font-bold">AI score: {gameState?.scores[2]}</h3>
          <h3 className="text-xl font-bold">AI dice count: {gameState?.players[2].length}</h3>
        </div>
        <h2 ref={statusRef} className={`text-lg font-bold bg-spring-green w-fit h-fit p-2 rounded-lg`}>Connection status: {isConnected ? 'connected' : 'disconnected'}</h2>
      </div>
      <div ref={messagesRef} className={`overflow-y-scroll snap-y h-[20rem] lg:h-[30rem] bg-spring-green border border-black shadow-lg rounded-lg p-2 mt-4 flex flex-col`}>
        {messages.map((message, index) => (
          <Message message={message} key={index} sidMaps={sidMaps} />
        ))}
        <div ref={endOfMessagesRef}></div>
      </div>
      <div className="flex flex-col mt-2 items-center lg:flex-row lg:justify-between gap-2">
        <RolledDiceFaces
          ref={diceRef}
          user="Your"
          rolledDice={gameState ? gameState.players[1].map(die => diceFaces[die - 1]) : []}
        />
        <AnswerButtons
          ref={answerButtonsRef}
          currentBid={convertBid(gameState?.current_bid || null)}
          previousBid={isFirstBid ? null : convertBid(gameState?.current_bid || null)}
          calledLiar={{ status: isFirstBid ? true : gameState?.last_action_was_challenge || false, caller: '' }}
          onClick={handleUserAction}
        />
      </div>
      {isGameOver && (
        <GameOverModal
          winner={winner ?? ""}
          onPlayAgain={handlePlayAgain}
          onGoHome={handleGoHome}
          onClose={handleCloseModal}
        />
      )}
    </div>
  );
};

export default GamePage;
