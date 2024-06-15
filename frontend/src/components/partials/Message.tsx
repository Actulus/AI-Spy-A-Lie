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
    const getDisplayName = (sid: string) => sidMaps.find(map => map.sid === sid)?.name || sid;
    const getDisplayPic = (sid: string) => sidMaps.find(map => map.sid === sid)?.pic || sid;
    const isAI = sidMaps.some(map => map.sid === message.sid && map.isAI);
  
    if (message.type === 'join') return <p className="text-lg text-center text-dark-spring-green">{`${getDisplayName(message.sid)} just joined`}</p>;
  
    if (message.type === 'chat') {
      const messageClass = isAI ? "snap-center bg-tea-rose text-black self-start" : "snap-center bg-nyanza text-black self-end";
  
      return (
        <div className={`flex items-center ${isAI ? '' : 'justify-end'}`}>
          {isAI ? <img src={getDisplayPic(message.sid)} alt="user" className={`w-8 h-8 mx-1 rounded-full`} /> : null}
          <div className={`my-2 p-2 rounded-lg w-40 md:w-64 ${messageClass}`}>
            <p className={`text-lg ${isAI ? 'text-start' : 'text-end'}`}>{`${getDisplayName(message.sid)}`}</p>
            <p className={`text-2xl ${isAI ? 'text-start' : 'text-end'}`} style={{ whiteSpace: 'pre-line' }}>{`${message.message}`}</p>
          </div>
          {isAI ? null : <img src={getDisplayPic(message.sid)} alt="user" className={`w-8 h-8 mx-1 rounded-full`} />}
        </div>
      );
    }
    return null;
  };