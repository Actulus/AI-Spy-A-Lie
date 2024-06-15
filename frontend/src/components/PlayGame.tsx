import { useNavigate } from "react-router-dom";
import Button from "./partials/Button";

const PlayGamePage: React.FC = () => {
  const navigate = useNavigate();
  const isDisabled = true;
  const disabledStyle = "cursor-not-allowed opacity-50"

  const handleGameButtonClick = (difficulty: string) => {
    navigate(`/game/${difficulty}`);
  };

  return (
    <div className="flex flex-col">
      <h1 className="text-2xl font-bold self-center text-white m-2">Choose difficulty:</h1>
      <div className="flex flex-col md:flex-row justify-center items-center">
        <Button onClick={() => handleGameButtonClick('tutorial')} name="play-button">Tutorial</Button>
        <Button onClick={() => handleGameButtonClick('easy')} name="play-button">
          Q-Learning
        </Button>
        <Button onClick={() => handleGameButtonClick('medium')} name="play-button">
          Deep Q-Network
        </Button>
        <Button onClick={() => handleGameButtonClick('hard')} name="play-button">
        State–action–reward–state–action
        </Button>
        <Button onClick={() => handleGameButtonClick('pvp')} name="play-button" isDisabled={isDisabled} style={disabledStyle} tooltip="Coming soon">
          Play with a friend
        </Button>
      </div>
    </div>
  );
};

export default PlayGamePage;
