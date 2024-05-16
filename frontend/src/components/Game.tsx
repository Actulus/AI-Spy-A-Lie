import React, { useEffect, useState, useRef } from "react";
import { io, Socket } from "socket.io-client";
import { useParams } from "react-router-dom";
import { useKindeAuth } from '@kinde-oss/kinde-auth-react';

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
    sid: string;
  }[];
}

export const Message: React.FC<MessageProps & SIDMapProps> = ({ message, sidMaps }) => {
  const getDisplayName = (sid: string) => {
    const map = sidMaps.find(map => map.sid === sid);
    return map ? map.name : sid;
  };

  if (message.type === 'join') return <p>{`${getDisplayName(message.sid)} just joined`}</p>;
  if (message.type === 'chat') return <p>{`${getDisplayName(message.sid)}: ${message.message}`}</p>;
  return null;
};

const GamePage: React.FC = () => {
  const { difficulty } = useParams<{ difficulty: string }>();
  const socket = useRef<Socket>();
  const { user } = useKindeAuth();

  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [messages, setMessages] = useState<Array<{ type: 'join' | 'chat'; sid: string; message?: string }>>([]);
  const [sidMaps, setSidMaps] = useState<{ name: string; sid: string }[]>([]);
  const [message, setMessage] = useState<string>('');

  const userName = `${user?.given_name} ${user?.family_name}`;
  const aiName = `${difficulty?.charAt(0).toUpperCase() + difficulty!.slice(1)}AI`;

  useEffect(() => {
    const socketInstance = io(import.meta.env.VITE_BACKEND_URL, {
      path: import.meta.env.VITE_REACT_APP_SOCKET_PATH,
      query: { room: difficulty },
    });

    socketInstance.on('connect', () => {
      setIsConnected(true);
    });

    socketInstance.on('disconnect', () => {
      setIsConnected(false);
    });

    socketInstance.on('join', (data: { sid: string }) => {
      setMessages((prevMessages) => [...prevMessages, { ...data, type: 'join' }]);
      if (data.sid.startsWith('ai_')) {
        setSidMaps((prevMaps) => [...prevMaps, { name: aiName, sid: data.sid }]);
      } else {
        setSidMaps((prevMaps) => [...prevMaps, { name: userName, sid: data.sid }]);
      }
    });

    socketInstance.on('chat', (data: { sid: string; message: string }) => {
      setMessages((prevMessages) => [...prevMessages, { ...data, type: 'chat' }]);
    });

    socket.current = socketInstance;

    return () => {
      socket.current?.disconnect();
    };
  }, [difficulty, userName, aiName]);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold">Game</h1>
      <h2 className="text-lg">Connection status: {isConnected ? 'connected' : 'disconnected'}</h2>
      <div className="h-64 overflow-y-scroll border border-black p-2 mt-4 flex flex-col">
        {messages.map((message, index) => (
          <Message message={message} key={index} sidMaps={sidMaps} />
        ))}
      </div>
      <input
        type="text"
        id="message"
        className="border p-1 mt-2"
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
        className="bg-blue-500 text-white p-2 mt-2"
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
    </div>
  );
};

export default GamePage;
