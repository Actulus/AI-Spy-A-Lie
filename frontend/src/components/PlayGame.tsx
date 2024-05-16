import { useNavigate } from "react-router-dom";
import Button from "./partials/Button";

const PlayGamePage: React.FC = () => {
  const navigate = useNavigate();

  const handleGameButtonClick = (difficulty: string) => {
    navigate(`/game/${difficulty}`);
  };

  return (
    <div>
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
  );
};

export default PlayGamePage;
