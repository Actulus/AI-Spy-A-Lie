import React from 'react';
import Button from './partials/Button'
import { useKindeAuth } from "@kinde-oss/kinde-auth-react";


const WelcomePage: React.FC = () => {
    const { login, register} = useKindeAuth();

    return (
        <div className='flex flex-col'>
            <div className='text-white flex flex-col items-center md:flex-row md:justify-between md:items-start'>
                <img src="/logo.png" alt="AI Spy A Lie Logo" className='w-24 h-24 rounded-full md:float-left mt-5 drop-shadow-lg md:h-52 md:w-52 md:ml-8'/>
                <div className='flex flex-col mt-5 md:mt-0 md:flex-row md:float-right md:mr-8 items-center'>
                    <Button onClick={register} name='register-button'>Register</Button>
                    <Button onClick={login} name='login-button'>Login</Button>
                </div>
            </div>
            <div className='text-white text-center mt-14 mx-4 whitespace-break-spaces md:text-left md:mx-5 lg:ml-16'>
                <p className='text-3xl text-shadow shadow-black font-bold mb-2'>Unmask Deception, Sharpen Wit:
                Where Minds Duel in the Art of Deceit!</p>
                <p className='text-2xl text-balance'>Welcome to AI Spy A Lie, your digital arena for intense Liar's Dice battles against cunning AI opponents. Dive into a world where strategic thinking meets deception, challenging your wit with every roll of the dice. Whether you're a seasoned player or new to the game, AI Spy A Lie offers a dynamic platform to test your skills, sharpen your mind, and experience the thrill of outsmarting artificial intelligence. Join us, where victory depends on your ability to unveil the truth and master the art of bluffing!</p>
            </div>
            <div>
                <img src='preview_2.png' alt='AI Spy A Lie Preview' className='w-1/2 h-auto m-5 float-right' />
            </div>
        </div>
    );
};

export default WelcomePage;