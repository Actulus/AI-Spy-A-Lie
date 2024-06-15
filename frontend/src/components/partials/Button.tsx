import React from 'react';

interface ButtonProps {
  onClick: () => void; 
  children: React.ReactNode;
  name?: string;
  style?: string;
  isDisabled?: boolean;
  tooltip?: string;
}

const Button: React.FC<ButtonProps> = ({ onClick, children, name, style, isDisabled, tooltip }) => {
  return (
    <div className="relative flex items-center justify-center">
       {isDisabled && tooltip && (
        <div className="absolute z-50 whitespace-normal break-words rounded-full bg-carmine text-white py-2 px-6 mx-3 my-3 focus:outline-none opacity-0 hover:opacity-100 transition-opacity duration-300">
          {tooltip}
        </div>
      )}
      <button
        name={name ? name : ''}
        className={`font-keania-one bg-gradient-to-b from-malachite to-dark-spring-green hover:bg-gradient-to-b hover:from-dark-spring-green hover:to-malachite text-white rounded-full py-2 px-6 mx-3 my-3 w-fit h-fit drop-shadow-lg ${style}`}
        onClick={onClick}
        disabled={isDisabled}
      >
        {children}
      </button>
    </div>
  );
};

export default Button;
