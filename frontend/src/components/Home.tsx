import React from 'react';
import Button from './partials/Button';
import { useKindeAuth } from '@kinde-oss/kinde-auth-react';
import StatisticsPlayer from './partials/StatisticsPlayer';

const HomePage: React.FC = () => {
    const user = useKindeAuth().user;

    const TopPlayers = [
        { name: user?.family_name, score: 100, profile: user?.picture },
        { name: 'Player 2', score: 90, profile: '' },
        { name: 'Player 3', score: 80, profile: '' },
        { name: 'Player 4', score: 70, profile: '' },
        { name: 'Player 5', score: 60, profile: '' },
        { name: 'Player 6', score: 50, profile: '' },
        { name: 'Player 7', score: 40, profile: '' },
        { name: user?.family_name, score: 30, profile: user?.picture },
        { name: 'Player 4', score: 70, profile: '' },
        { name: 'Player 5', score: 60, profile: '' },
        { name: 'Player 6', score: 50, profile: '' },
        { name: 'Player 7', score: 40, profile: '' },
        { name: user?.family_name, score: 30, profile: user?.picture },
    ]

    const handlePlayButtonClick = () => {
        console.log('Join a game button clicked');
    }

    return (
        <div className='grid grid-cols-1 gap-2 m-2 md:grid-cols-2 flex-grow'>
            <div className='flex flex-col gap-2'>
                <div className='bg-spring-green rounded-lg font-keania-one w-full h-full p-5 flex justify-between col-start-1 md:row-start-1'>
                    <div>
                        <p className='text-pakistan-green text-shadow-sm shadow-dark-spring-green'>Join a game</p>
                        <p className='font-roboto text-dark-spring-green'>Play against bots or humans</p>
                    </div>
                    <div className='md:place-self-end'>
                        <Button onClick={handlePlayButtonClick} name='play-button'>Play now</Button>
                    </div>
                </div>
                <div className='bg-spring-green rounded-lg font-keania-one w-full h-fit p-5 flex flex-col justify-between col-start-1 md:row-start-1'>
                    <p className='text-pakistan-green text-shadow-sm shadow-dark-spring-green'>Game Rules</p>
                    <ul className='flex flex-col gap-3 ml-2 mt-2 font-roboto'>
                        <li className='flex items-center'>
                            <img src='/dice-five.svg' className='h-12 w-12 mr-3 place-self-start' />
                            <div className='flex flex-col'>
                                <p>1</p>
                                <p className='text-dark-spring-green'>Each player rolls five dice and keeps them hidden from others. Players take turns making bids about the results of all the dice, such as how many fives there are.</p>
                            </div>
                        </li>
                        <li className='flex items-center'>
                            <img src='/loop.svg' className='h-12 w-12 mr-3 place-self-start' />
                            <div>
                                <p>2</p>
                                <p className='text-dark-spring-green'>When a player thinks the last bid is a lie, they can challenge it. If the bid was true, the challenger loses a die. If it was a lie, the bidder loses a die.</p>
                            </div>
                        </li>
                        <li className='flex items-center'>
                            <img src='/trophy.svg' className='h-12 w-12 mr-3 place-self-start' />
                            <div>
                                <p>3</p>
                                <p className='text-dark-spring-green'>The game continues until only one player has dice left. That player wins the game.</p>
                            </div>
                        </li>
                    </ul>
                </div>
            </div>
            <div className='bg-spring-green rounded-lg font-keania-one w-full h-full p-5 flex flex-col justify-between col-start-1 md:col-start-2 md:row-start-1'>
                <p className='text-pakistan-green text-shadow-sm shadow-dark-spring-green'>Statistics</p>
                <ul className='flex flex-col gap-3 mt-2'>
                    {TopPlayers.slice(0, 10).map((player, index) => (
                        <StatisticsPlayer key={index} name={player.name ? player.name : "Player"} score={player.score} profile={player.profile ? player.profile : '/cat_pfp.png'} />
                    ))}
                </ul>
            </div>
            <div className='bg-spring-green rounded-lg font-keania-one w-full h-fit p-5 flex flex-col justify-between col-start-1 md:row-start-2 md:col-span-2'>
                <p className='text-pakistan-green text-shadow-sm shadow-dark-spring-green'>How to play</p>
                <ul className='flex flex-col gap-3 ml-2 mt-2'>
                    <li className='flex items-center'>
                        <img src='/dice-five.svg' className='h-10 w-10 mr-2' />
                        <p>1. Roll the dice</p>
                    </li>
                    <li className='flex items-center'>
                        <img src='/megaphone.svg' className='h-10 w-10 mr-2' />
                        <p>2. Make a bid</p></li>
                    <li className='flex items-center'>
                        <img src='/search-magnify-glass.svg' className='h-10 w-10 mr-2' />
                        <p>3. Call a bluff</p></li>
                    <li className='flex items-center'>
                        <img src='/trophy.svg' className='h-10 w-10 mr-2' />
                        <p>4. Win the game</p></li>
                </ul>
            </div>
        </div>
    )
}

export default HomePage;