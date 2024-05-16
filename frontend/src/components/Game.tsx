// GamePage.tsx
import { useEffect, useState } from "react";
import { io, Socket } from "socket.io-client";
import WebSocketCall from "./WebSocketCall";

const GamePage: React.FC = () => {
  const [socket, setSocket] = useState<Socket | null>(null);

  useEffect(() => {
    // Establish the socket connection when the component mounts
    const newSocket = io(import.meta.env.VITE_BACKEND_URL,{
      transports: ['websocket']
    }); // Replace with your server URL and port

    // Event listeners
    newSocket.on("connect", () => {
      console.log("Connected to server");
    });

    newSocket.on("disconnect", () => {
      console.log("Disconnected from server");
    });

    setSocket(newSocket);

    // Clean up the socket connection when the component unmounts
    return () => {
      newSocket.disconnect();
    };
  }, []);

  return (
    <div>
      <h1>Game</h1>
      {socket && <WebSocketCall socket={socket} />}
    </div>
  );
};

export default GamePage;