import { useKindeAuth } from '@kinde-oss/kinde-auth-react';
import React from 'react';


const ProfilePage: React.FC = () => {
    const user = useKindeAuth().user;
    const highscore = 100;


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
        </div>
    );
};

export default ProfilePage;