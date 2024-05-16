import React, { useEffect, useState, useRef } from "react";
import { io, Socket } from "socket.io-client";

// Define the types for the message
interface MessageProps {
  message: {
    type: 'join' | 'chat';
    sid: string;
    message?: string;
  };
}

// Message component with type annotations
export const Message: React.FC<MessageProps> = ({ message }) => {
  if (message.type === 'join') return <p>{`${message.sid} just joined`}</p>;
  if (message.type === 'chat') return <p>{`${message.sid}: ${message.message}`}</p>;
  return null;
};

const GamePage: React.FC = () => {
  const socket = useRef<Socket>();

  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [messages, setMessages] = useState<Array<{ type: 'join' | 'chat'; sid: string; message?: string }>>([]);
  const [message, setMessage] = useState<string>('');

  useEffect(() => {
    socket.current = io(import.meta.env.VITE_BACKEND_URL, {
      path: import.meta.env.VITE_REACT_APP_SOCKET_PATH,
    });

    socket.current.on('connect', () => {
      setIsConnected(true);
    });

    socket.current.on('disconnect', () => {
      setIsConnected(false);
    });

    socket.current.on('join', (data: { sid: string }) => {
      setMessages((prevMessages) => [...prevMessages, { ...data, type: 'join' }]);
    });

    socket.current.on('chat', (data: { sid: string; message: string }) => {
      setMessages((prevMessages) => [...prevMessages, { ...data, type: 'chat' }]);
    });

    return () => {
      socket.current?.disconnect();
    };
  }, []);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold">Game</h1>
      <h2 className="text-lg">Connection status: {isConnected ? 'connected' : 'disconnected'}</h2>
      <div className="h-64 overflow-y-scroll border border-black p-2 mt-4 flex flex-col">
        {messages.map((message, index) => (
          <Message message={message} key={index} />
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
