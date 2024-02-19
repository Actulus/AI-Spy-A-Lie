import React from 'react';
import Button from './partials/Button';

const HomePage: React.FC = () => {
    const handlePlayButtonClick = () => {
        console.log('Join a game button clicked');
    }

    return (
        <div>
            <div className='flex flex-col md:flex-row'>
                <div className='flex flex-col justify-evenly'>
                    <div className='bg-spring-green rounded-lg font-keania-one w-full h-fit p-5 md:w-1/2 flex justify-between'>
                        <div>
                            <p className='text-pakistan-green'>Join a game</p>
                            <p className='font-roboto text-dark-spring-green'>Play against bots or humans</p>
                        </div>
                        <Button onClick={handlePlayButtonClick} name='play-button'>Play now</Button>
                    </div>
                    <div className='bg-spring-green rounded-lg font-keania-one w-full h-fit p-5 md:w-1/2 flex justify-between'>

                    </div>
                    <div>Game Rules</div>
                </div>
                <div>Statistics</div>
            </div>
            <div>How to play</div>
        </div>
    )
}

export default HomePage;