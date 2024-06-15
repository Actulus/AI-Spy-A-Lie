import React, { forwardRef } from 'react';

const RolledDiceFaces = forwardRef<HTMLDivElement, { user: string; rolledDice: string[]; }>(
  ({ user, rolledDice}, ref) => {
    return (
      <div ref={ref} className={`flex flex-col items-center`}>
        <p className="text-white text-2xl">{user} Dices</p>
        <div className="flex flex-wrap justify-center items-center outline outline-white rounded-lg">
          {rolledDice.map((face, index) => (
            <div key={index} className="flex text-2xl m-2 p-2 text-center justify-center items-center bg-nyanza text-black rounded-lg">
              {face}
            </div>
          ))}
        </div>
      </div>
    );
  }
);

export default RolledDiceFaces;
