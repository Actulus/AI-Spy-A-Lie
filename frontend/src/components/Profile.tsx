import { useKindeAuth } from '@kinde-oss/kinde-auth-react';
import React from 'react';
import { useState, useEffect } from 'react';
import { HighscoreResponse, TotalHighscoreResponse } from '../../types';

interface PersonalScores {
    score: number;
    highscore_datetime: Date;
    ai_bot_type: string;
}

const ProfilePage: React.FC = () => {
    const user = useKindeAuth().user;
    const [highscore, setHighscore] = useState<number>(0);
    const [userScores, setUserScores] = useState<PersonalScores[]>([]);

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
                    score: player.user_score,
                    highscore_datetime: player.highscore_datetime,
                    ai_bot_type: player.ai_bot_type,
                }));

                players.sort((a, b) => new Date(b.highscore_datetime).getTime() - new Date(a.highscore_datetime).getTime());

                setUserScores(players);
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    }, [user?.id]);

    useEffect(() => {
        fetch(`${import.meta.env.VITE_BACKEND_URL}/api/highscores/${user?.id}/total`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
            .then(response => response.json())
            .then((data: TotalHighscoreResponse) => {
                setHighscore(data.total_score);
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    }, [user?.id]);

    const formatDate = (datetimeString: Date) => {
        const date = new Date(datetimeString);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are zero-indexed
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    };


    return (
        <div className='bg-spring-green w-fit m-5 p-5 rounded flex flex-col flex-grow place-self-center'>
            <img src={user?.picture ? user.picture : '/cat_pfp.png'} className='w-20 h-20' />
            <div className='flex gap-1 items-end'>
                <p className="md:text-4xl text-pakistan-green font-keania-one">Name:</p>
                <p className='md:text-3xl text-dark-spring-green font-roboto'>{user?.family_name} {user?.given_name}</p>
            </div>
            <div className='flex gap-1 items-end'>
                <p className="md:text-4xl text-pakistan-green font-keania-one">Email:</p>
                <p className='md:text-3xl text-dark-spring-green font-roboto'>{user?.email}</p>
            </div>
            <div className='flex gap-1 items-end'>
                <p className="md:text-4xl text-pakistan-green font-keania-one">Highscore:</p>
                <p className='md:text-3xl text-dark-spring-green font-roboto'>{highscore}</p>
            </div>
            <div className='bg-spring-green rounded-lg font-keania-one w-full h-full flex flex-col justify-start col-start-1 md:col-start-2 md:row-start-1'>
                <p className='md:text-4xl text-pakistan-green shadow-dark-spring-green'>Personal Statistics:</p>
                <div className=' overflow-y-scroll h-96'>
                    {userScores.map((player) => (
                        <div className='flex flex-col bg-green-400 p-2 rounded-lg my-2'>
                            <div className='flex gap-1'>
                                <p className='text-pakistan-green'>Score:</p>
                                <p className='text-dark-spring-green font-roboto'>{player.score}</p>
                            </div>
                            <div className='flex gap-1'>
                                <p className='text-pakistan-green'>Highscore Date:</p>
                                <p className='text-dark-spring-green font-roboto'>{formatDate(player.highscore_datetime)}</p>
                            </div>
                            <div className='flex gap-1'>
                                <p className='text-pakistan-green'>AI Bot Type:</p>
                                <p className='text-dark-spring-green font-roboto'>{player.ai_bot_type}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default ProfilePage;