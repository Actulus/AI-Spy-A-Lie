import React from 'react';

interface ButtonProps {
  onClick: () => void; 
  children: React.ReactNode;
  name?: string;
}

const Button: React.FC<ButtonProps> = ({ onClick, children, name }) => {
  return (
    <button name={name ? name : ''}
            className="bg-gradient-to-b from-malachite to-dark-spring-green text-white rounded-full py-2 px-6 mx-3 my-3 w-fit h-fit drop-shadow-lg" 
            onClick={onClick}>
      {children}
    </button>
  );
};

export default Button;
