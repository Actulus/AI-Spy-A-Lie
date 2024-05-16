// websocketcall.tsx
import { useEffect, useState } from "react";
import { Socket } from "socket.io-client";

interface WebSocketCallProps {
  socket: Socket;
}

export default function WebSocketCall({ socket }: WebSocketCallProps) {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<string[]>([]);

  const handleText = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputMessage = e.target.value;
    setMessage(inputMessage);
  };

  const handleSubmit = () => {
    if (!message) {
      return;
    }

    socket.emit("data", message);
    setMessage("");
  };

  useEffect(() => {
    // Event listener for the "data" event from the server
    socket.on("data", (data) => {
      setMessages((prevMessages) => [...prevMessages, data.data]);
    });

    // Clean up the event listener when the component unmounts
    return () => {
      socket.off("data");
    };
  }, [socket]);

  return (
    <div>
      <h2>WebSocket Communication</h2>
      <input type="text" value={message} onChange={handleText} />
      <button onClick={handleSubmit}>Send</button>
      <ul>
        {messages.map((msg, index) => (
          <li key={index}>{msg}</li>
        ))}
      </ul>
    </div>
  );
}