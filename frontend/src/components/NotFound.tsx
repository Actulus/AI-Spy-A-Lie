import { useKindeAuth } from '@kinde-oss/kinde-auth-react';
import React from 'react';
import { Link } from 'react-router-dom';

const NotFoundPage: React.FC = () => {
    const {isAuthenticated} = useKindeAuth();

    return (
        <div className=''>
            <div className='flex justify-center'>
                <img src="/404.png" alt="404 not found" className='h-96' />
            </div>
            <div className='lowercase text-white flex flex-col gap-y-2 justify-center'>
                <p className='text-2xl self-center'>the page you were looking for does not exist</p>
                <p className='text-lg self-center'>(unless you were looking for cat gifs, in that case you found the right place)</p>
            </div>
            <div className="mt-4 flex justify-center">
                <img
                    src="https://cataas.com/cat/gif"
                    alt="img"
                    className="object-cover w-80 h-80 self-center"
                />
            </div>
            <div className='xl:float-right flex flex-col justify-center gap-y-2 mr-5'>
                <p className='text-white text-lg self-center'>or you can go back to the home page</p>
                {isAuthenticated ? <Link to='/home'><img src='/logo.png' alt='logo go to home page' className='rounded-full'/></Link> : <Link to='/'><img src='/logo.png' alt='logo go to home page' className='rounded-full'/></Link>}
            </div>
        </div>
    );
};

export default NotFoundPage;