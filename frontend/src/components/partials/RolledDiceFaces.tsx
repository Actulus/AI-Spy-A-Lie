import { forwardRef, useEffect, useState } from 'react';

const RolledDiceFaces = forwardRef<HTMLDivElement, { user: string; rolledDice: string[]; last_action_was_challenge: boolean|undefined }>(
  ({ user, rolledDice, last_action_was_challenge }, ref) => {
    const [diceWithAnimation, setDiceWithAnimation] = useState(
      rolledDice.map((face, index) => ({ face, key: index, animation: last_action_was_challenge }))
    );

    useEffect(() => {
      // Apply the animation class when the rolledDice changes
      setDiceWithAnimation(rolledDice.map((face, index) => ({
        face,
        key: index,
        animation: last_action_was_challenge,
      })));

      // Remove the animation class after the animation duration
      const timer = setTimeout(() => {
        setDiceWithAnimation(rolledDice.map((face, index) => ({
          face,
          key: index,
          animation: false,
        })));
      }, 1000); // match the animation duration

      return () => clearTimeout(timer);
    }, [rolledDice, last_action_was_challenge]);

    return (
      <div ref={ref} className="flex flex-col items-center">
        <p className="text-white text-2xl">{user} Dice</p>
        <div className="flex flex-wrap justify-center items-center outline outline-white rounded-lg">
          {diceWithAnimation.map(({ face, key, animation }) => (
            <div
              key={key}
              className={`flex text-2xl m-2 p-2 text-center justify-center items-center bg-nyanza text-black rounded-lg`}
            >
              <p className={`text-4xl ${animation ? 'animate-spin' : ''}`}>{face}</p>
            </div>
          ))}
        </div>
      </div>
    );
  }
);

export default RolledDiceFaces;
