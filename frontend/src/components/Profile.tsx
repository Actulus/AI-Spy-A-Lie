import { useKindeAuth } from '@kinde-oss/kinde-auth-react';
import React from 'react';
import { useState, useEffect } from 'react';
import StatisticsPlayer from './partials/StatisticsPlayer';
import { Player, HighscoreResponse } from '../../types';

const ProfilePage: React.FC = () => {
    const user = useKindeAuth().user;
    const [highscore, setHighscore] = useState<number>(0);
    const [userScores, setUserScores] = useState<Player[]>([]);

    useEffect(() => {
        fetch(`${import.meta.env.VITE_BACKEND_URL}/api/highscores/${user?.id}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then((data: HighscoreResponse[]) => {
            const players = data.map((player: HighscoreResponse) => ({
                name: player.user_name,
                score: player.user_score,
                profile: player.profile_picture,
            }));
            setUserScores(players);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }, [user?.id]); 

    useEffect(() => {
        fetch(`${import.meta.env.VITE_BACKEND_URL}/api/highscores/${user?.id}/best`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then((data: HighscoreResponse) => {
            setHighscore(data.user_score);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }, [user?.id]);



    return (
        <div className='bg-spring-green h-full w-fit m-5 p-5 rounded flex flex-col flex-grow place-self-center'>
            <img src={user?.picture ? user.picture : '/cat_pfp.png'} className='w-20 h-20' />
            <div className='flex gap-1 items-end'>
                <p className="text-4xl text-pakistan-green font-keania-one">Name:</p>
                <p className='text-3xl text-dark-spring-green font-roboto'>{user?.family_name} {user?.given_name}</p>
            </div>
            <div className='flex gap-1 items-end'>
                <p className="text-4xl text-pakistan-green font-keania-one">Email:</p>
                <p className='text-3xl text-dark-spring-green font-roboto'>{user?.email}</p>
            </div>
            <div className='flex gap-1 items-end'>
                <p className="text-4xl text-pakistan-green font-keania-one">Highscore:</p>
                <p className='text-3xl text-dark-spring-green font-roboto'>{highscore}</p>
            </div>
            <div className='bg-spring-green rounded-lg font-keania-one w-full h-full p-5 flex flex-col justify-start col-start-1 md:col-start-2 md:row-start-1'>
                <p className='text-pakistan-green text-shadow-sm shadow-dark-spring-green'>Personal Statistics</p>
                <ul className='flex flex-col gap-3 mt-2'>
                    {userScores.slice(0, 10).map((player, index) => (
                        <StatisticsPlayer key={index} name={player.name ? player.name : "Player"} score={player.score} profile={player.profile ? player.profile : '/cat_pfp.png'} />
                    ))}
                </ul>
            </div>
        </div>
    );
};

export default ProfilePage;