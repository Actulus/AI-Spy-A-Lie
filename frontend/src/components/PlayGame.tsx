import { useNavigate } from "react-router-dom";
import Button from "./partials/Button";

const PlayGamePage: React.FC = () => {
  const navigate = useNavigate();

  const handleEasyGameButtonClick = () => {
    navigate("/easy-game");
  };

  const handleMediumGameButtonClick = () => {
    navigate("/medium-game");
  };

  const handleHardGameButtonClick = () => {
    navigate("/hard-game");
  };

  return (
    <div>
      <Button onClick={handleEasyGameButtonClick} name="play-button">
        Easy
      </Button>
      <Button onClick={handleMediumGameButtonClick} name="play-button">
        Medium
      </Button>
      <Button onClick={handleHardGameButtonClick} name="play-button">
        Hard
      </Button>
    </div>
  );
};

export default PlayGamePage;