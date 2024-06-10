import { useKindeAuth } from '@kinde-oss/kinde-auth-react';
import React from 'react';
import { useState, useEffect } from 'react';
import { PersonalStatisticsResponse, TotalHighscoreResponse } from '../../types';


const ProfilePage: React.FC = () => {
    const user = useKindeAuth().user;
    const [highscore, setHighscore] = useState<number>(0);
    const [userScores, setUserScores] = useState<PersonalStatisticsResponse[]>([]);

    useEffect(() => {
        fetch(`${import.meta.env.VITE_BACKEND_URL}/api/users/${user?.id}/match-histories`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
            .then(response => response.json())
            .then((data: PersonalStatisticsResponse[]) => {
                const players = data.map((player: PersonalStatisticsResponse) => ({
                    match_id: player.match_id,
                    match_date: player.match_date,
                    user_score: player.user_score,
                    opponents: player.opponents,
                    ai_opponents: player.ai_opponents,
                }));

                players.sort((a, b) => new Date(b.match_date).getTime() - new Date(a.match_date).getTime());

                setUserScores(players);
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    }, [user?.id]);

    useEffect(() => {
        fetch(`${import.meta.env.VITE_BACKEND_URL}/api/users/${user?.id}/total-score`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
            .then(response => response.json())
            .then((data: TotalHighscoreResponse) => {
                setHighscore(data.user_total_score);
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
                <div className='overflow-y-scroll h-96'>
                    {userScores.map((match) => (
                        <div key={match.match_id} className='flex flex-col bg-green-400 p-2 rounded-lg my-2'>
                            <div className='flex gap-1'>
                                <p className='text-pakistan-green'>Match Date:</p>
                                <p className='text-dark-spring-green font-roboto'>{formatDate(new Date(match.match_date))}</p>
                            </div>
                            <div className='flex gap-1'>
                                <p className='text-pakistan-green'>User Score:</p>
                                <p className='text-dark-spring-green font-roboto'>{match.user_score}</p>
                            </div>
                            {match.opponents.length > 0 &&
                            <div>
                                <p className='text-pakistan-green'>Opponents:</p>
                                {match.opponents.map((opponent, index) => (
                                    <div key={index} className='flex gap-1 ml-4'>
                                        <p className='text-dark-spring-green font-roboto'>{opponent.user_name}:</p>
                                        <p className='text-dark-spring-green font-roboto'>{opponent.score}</p>
                                    </div>
                                ))}
                            </div>
                            }

                            {match.ai_opponents.length > 0 &&
                            <div>
                                <p className='text-pakistan-green'>AI Opponents:</p>
                                {match.ai_opponents.map((aiOpponent, index) => (
                                    <div key={index} className='flex gap-1 ml-4'>
                                        <p className='text-dark-spring-green font-roboto'>- {aiOpponent.ai_type}</p>
                                        <p className='text-dark-spring-green font-roboto'> score:{aiOpponent.score}</p>
                                    </div>
                                ))}
                            </div>
                            }
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default ProfilePage;