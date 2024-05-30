import React, { useEffect, useState, useRef, useCallback } from "react";
import { io, Socket } from "socket.io-client";
import { useParams } from "react-router-dom";
import { useKindeAuth } from '@kinde-oss/kinde-auth-react';
import RolledDiceFaces from "./partials/RolledDiceFaces";
import AnswerButtons from "./partials/AnswerButtons";

interface MessageProps {
  message: {
    type: 'join' | 'chat';
    sid: string;
    message?: string;
  };
}

interface SIDMapProps {
  sidMaps: {
    name: string;
    pic: string;
    sid: string;
    isAI: boolean;
  }[];
}

interface GameState {
  dice_count: { [key: number]: number };
  players: { [key: number]: number[] };
  current_bid: [number, number];
  current_player: number;
  last_action_was_challenge: boolean;
  player_names: { [key: number]: string };
}

const diceFaces = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅'];

export const Message: React.FC<MessageProps & SIDMapProps> = ({ message, sidMaps }) => {
  const getDisplayName = (sid: string) => sidMaps.find(map => map.sid === sid)?.name || sid;
  const getDisplayPic = (sid: string) => sidMaps.find(map => map.sid === sid)?.pic || sid;
  const isAI = sidMaps.some(map => map.sid === message.sid && map.isAI);

  if (message.type === 'join') return <p className="text-center text-dark-spring-green">{`${getDisplayName(message.sid)} just joined`}</p>;

  if (message.type === 'chat') {
    const messageClass = isAI ? "snap-center bg-tea-rose text-black self-start" : "snap-center bg-nyanza text-black self-end";

    return (
      <div className={`flex items-center ${isAI ? '' : 'justify-end'}`}>
        {isAI ? <img src={getDisplayPic(message.sid)} alt="user" className={`w-8 h-8 mx-1 rounded-full`} /> : null}
        <div className={`my-2 p-2 rounded-lg w-40 md:w-64 ${messageClass}`}>
          <p className={`text-xs ${isAI ? 'text-start' : 'text-end'}`}>{`${getDisplayName(message.sid)}`}</p>
          <p className={`${isAI ? 'text-start' : 'text-end'}`} style={{ whiteSpace: 'pre-line' }}>{`${message.message}`}</p>
        </div>
        {isAI ? null : <img src={getDisplayPic(message.sid)} alt="user" className={`w-8 h-8 mx-1 rounded-full`} />}
      </div>
    );
  }
  return null;
};

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

  const endOfMessagesRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const socketInstance = io(import.meta.env.VITE_BACKEND_URL, {
      path: import.meta.env.VITE_REACT_APP_SOCKET_PATH,
      query: { room: difficulty },
    });

    socketInstance.on('connect', () => {
      setIsConnected(true);
      setSidMaps(prevMaps => [...prevMaps, { name: userName, pic: userPic as string, sid: socketInstance.id as string, isAI: false }]);
      socketInstance.emit('player_names', { userName, aiName })
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
    });

    socket.current = socketInstance;

    return () => {
      socket.current?.disconnect();
    };
  }, [difficulty, userName, aiName, userPic, aiPic]);

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


  return (
    <div className="flex flex-col p-4">
      <h2 className="text-lg font-bold bg-spring-green w-fit p-2 rounded-lg">Connection status: {isConnected ? 'connected' : 'disconnected'}</h2>
      <div className="overflow-y-scroll snap-y h-[40rem] bg-spring-green border border-black shadow-lg rounded-lg p-2 mt-4 flex flex-col">
        {messages.map((message, index) => (
          <Message message={message} key={index} sidMaps={sidMaps} />
        ))}
        <div ref={endOfMessagesRef}></div>
      </div>
      <div className="flex flex-col mt-2 items-center lg:flex-row lg:justify-between gap-2">
        <RolledDiceFaces user="Your" rolledDice={gameState ? gameState.players[1].map(die => diceFaces[die - 1]) : []} />
        <AnswerButtons
          currentBid={convertBid(gameState?.current_bid || null )}
          previousBid={isFirstBid ? null : convertBid(gameState?.current_bid || null)} 
          calledLiar={{ status: gameState?.last_action_was_challenge || false, caller: '' }}
          onClick={handleUserAction}
        />
      </div>
    </div>
  );
};

export default GamePage;
