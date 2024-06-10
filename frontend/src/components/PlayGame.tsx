import { useNavigate } from "react-router-dom";
import Button from "./partials/Button";

const PlayGamePage: React.FC = () => {
  const navigate = useNavigate();

  const handleGameButtonClick = (difficulty: string) => {
    navigate(`/game/${difficulty}`);
  };

  return (
    <div className="flex flex-col">
      <h1 className="text-2xl font-bold self-center text-white m-2">Choose difficulty:</h1>
    <div className="flex flex-col md:flex-row justify-center items-center">
      <Button onClick={() => handleGameButtonClick('tutorial')} name="play-button">Tutorial</Button>
      <Button onClick={() => handleGameButtonClick('easy')} name="play-button">
        Easy
      </Button>
      <Button onClick={() => handleGameButtonClick('medium')} name="play-button">
        Medium
      </Button>
      <Button onClick={() => handleGameButtonClick('hard')} name="play-button">
        Hard
      </Button>
    </div>
    </div>
  );
};

export default PlayGamePage;
