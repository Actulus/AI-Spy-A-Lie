import React from 'react';

interface StatisticsPlayerProps {
    profile: string | undefined;
    name: string;
    score: number;
}

const StatisticsPlayer: React.FC<StatisticsPlayerProps> = ({ name, score, profile }) => {
    return (
        <div className='flex gap-2'>
            <img src={profile} className='h-10 w-10 rounded-full'/>
            <div className='flex flex-col'>
                <p className='text-pakistan-green'>Player: {name}</p>
                <p className='text-deep-spring-green'>Score: {score}</p>
            </div>
        </div>
    )
}

export default StatisticsPlayer;