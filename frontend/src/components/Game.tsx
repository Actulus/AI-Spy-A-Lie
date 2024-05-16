import React, { useEffect, useState, useRef } from "react";
import { io, Socket } from "socket.io-client";
import { useParams } from "react-router-dom";
import { useKindeAuth } from '@kinde-oss/kinde-auth-react';
import AnswerButton from "./partials/AnswerButtons";
import RolledDiceFaces from "./partials/RolledDiceFaces";

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

export const Message: React.FC<MessageProps & SIDMapProps> = ({ message, sidMaps }) => {
  const getDisplayName = (sid: string) => {
    const map = sidMaps.find(map => map.sid === sid);
    return map ? map.name : sid;
  };

  const getDisplayPic = (sid: string) => {
    const map = sidMaps.find(map => map.sid === sid);
    return map ? map.pic : sid;
  }

  const isAI = sidMaps.some(map => map.sid === message.sid && map.isAI);

  if (message.type === 'join') return <p className="text-center text-dark-spring-green">{`${getDisplayName(message.sid)} just joined`}</p>;

  if (message.type === 'chat') {
    const messageClass = isAI ? "snap-center bg-tea-rose text-black self-start" : "snap-center bg-nyanza text-black self-end";

    return (
      <div className={`flex items-center ${isAI ? '' : 'justify-end'}`}>
        {isAI ? <img src={getDisplayPic(message.sid)} alt="user" className={`w-8 h-8 mx-1 rounded-full`} /> : null}
        <div className={`my-2 p-2 rounded-lg w-40 md:w-64 ${messageClass}`}>
          <p className={`text-xs ${isAI ? 'text-start' : 'text-end'}`}>{`${getDisplayName(message.sid)}`}</p>
          <p className={`${isAI ? 'text-start' : 'text-end'}`}>{`${message.message}`}</p>
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

  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [messages, setMessages] = useState<Array<{ type: 'join' | 'chat'; sid: string; message?: string }>>([]);
  const [sidMaps, setSidMaps] = useState<{ name: string; pic: string; sid: string; isAI: boolean }[]>([]);
  // const [message, setMessage] = useState<string>('');

  const endOfMessagesRef = useRef<HTMLDivElement | null>(null);

  const userName = `${user?.given_name} ${user?.family_name}`;
  const aiName = `${difficulty?.charAt(0).toUpperCase() + difficulty!.slice(1)}AI`;
  const userPic = user?.picture || "/cat_pfp.png"
  const aiPic = '/AI_Pic.png';

  useEffect(() => {
    const socketInstance = io(import.meta.env.VITE_BACKEND_URL, {
      path: import.meta.env.VITE_REACT_APP_SOCKET_PATH,
      query: { room: difficulty },
    });

    socketInstance.on('connect', () => {
      setIsConnected(true);
      setSidMaps(prevMaps => [...prevMaps, { name: userName, pic: userPic as string, sid: socketInstance.id as string, isAI: false }]);
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

  return (
    <div className="flex flex-col p-4">
      <h2 className="text-lg font-bold bg-spring-green w-fit p-2 rounded-lg">Connection status: {isConnected ? 'connected' : 'disconnected'}</h2>
      <div className="overflow-y-scroll snap-y h-[40rem] bg-spring-green border border-black shadow-lg rounded-lg p-2 mt-4 flex flex-col">
        {messages.map((message, index) => (
          <Message message={message} key={index} sidMaps={sidMaps} />
        ))}
        <div ref={endOfMessagesRef}></div>
      </div>
      {/* <div className="flex">
        <input
          type="text"
          id="message"
          className="border p-1 mt-2 mr-2 rounded-lg w-full"
          onChange={(event) => {
            const value = event.target.value.trim();
            setMessage(value);
          }}
          // on enter key 
          onKeyDown={(event) => {
            if (event.key === 'Enter') {
              if (message && message.length) {
                socket.current?.emit('chat', message);
              }
              const messageBox = document.getElementById('message') as HTMLInputElement;
              messageBox.value = '';
              setMessage('');
            }
          }
          }
        />
        <button
          className="bg-spring-green font-bold rounded-lg text-white p-2 mt-2"
          onClick={() => {
            if (message && message.length) {
              socket.current?.emit('chat', message);
            }
            const messageBox = document.getElementById('message') as HTMLInputElement;
            messageBox.value = '';
            setMessage('');
          }}
        >
          Send
        </button>
      </div> */}
      <div className="flex flex-col mt-2 items-center lg:flex-row lg:justify-between gap-2">
        <RolledDiceFaces rolledDice={[1, 2, 3, 4, 5]} />
        <AnswerButton onClick={(answer) => socket.current?.emit('chat', answer)} />
      </div>
    </div>
  );
};

export default GamePage;
