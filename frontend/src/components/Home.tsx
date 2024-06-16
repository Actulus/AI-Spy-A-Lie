import React, { useState, useEffect } from 'react';
import Button from './partials/Button';
import StatisticsPlayer from './partials/StatisticsPlayer';
import { useNavigate } from 'react-router-dom';
import { HighscoreResponse, Player } from '../../types';
import { useKindeAuth } from '@kinde-oss/kinde-auth-react';

interface HomePageProps {
    isAdmin: boolean;
}

const HomePage: React.FC<HomePageProps> = ({ isAdmin }: { isAdmin: boolean }) => {
    const user = useKindeAuth().user;
    const [TopPlayers, setTopPlayers] = useState<Player[]>([]);
    const navigate = useNavigate();

    const handleStatisticsClicked = () => {
        navigate('/statistics')
    }

    useEffect(() => {
        fetch(`${import.meta.env.VITE_BACKEND_URL}/api/user`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                "kinde_uuid": user?.id,
                "user_name": user?.family_name + " " + user?.given_name,
                "profile_picture": user?.picture,

            })
        })
            .then(response => response.json())
            .catch((error) => {
                console.error('Error:', error);
            });
    }, [user]);

    useEffect(() => {
        fetch(`${import.meta.env.VITE_BACKEND_URL}/api/users/leaderboard`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
            .then(response => response.json())
            .then((data: HighscoreResponse[]) => {
                const players = data.map((player: HighscoreResponse) => ({
                    name: player.user_name.split(' ').map((word) => word[0].toUpperCase()).join(''),
                    score: player.user_total_score,
                    profile: player.profile_picture,
                }));
                setTopPlayers(players);
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    }, []);

    const handlePlayButtonClick = () => {
        navigate('/play-game')
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
                        <li className='flex items-center'>
                            <img src='/joker.svg' className='h-12 w-12 mr-3 place-self-start' />
                            <div>
                                <p>3</p>
                                <p className='text-dark-spring-green'>The number 1 acts as a joker, meaning it can be used as any number.</p>
                            </div>
                        </li>
                    </ul>
                </div>
            </div>
            <div className='bg-spring-green rounded-lg font-keania-one w-full h-full p-5 flex flex-col justify-start col-start-1 md:col-start-2 md:row-start-1'>
                <div className='flex justify-between'>
                    <p className='text-pakistan-green text-shadow-sm shadow-dark-spring-green'>Statistics</p>
                    {isAdmin &&
                        <Button name='statistics-button' onClick={handleStatisticsClicked} style='my-0 mx-0'>Statistics</Button>
                    }
                </div>
                <ul className='flex flex-col gap-3 mt-2'>
                    {TopPlayers.slice(0, 10).map((player, index) => (
                        <StatisticsPlayer key={index} name={player.name ? player.name : "Player"} score={player.score} profile={player.profile ? player.profile :  "https://ui-avatars.com/api/?name="+player.name} />
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