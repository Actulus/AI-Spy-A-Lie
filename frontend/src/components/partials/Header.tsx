import React from "react";
import { useNavigate } from "react-router-dom";

const Header: React.FC = () => {
    const navigate = useNavigate();
    const handleLogoClicked = () => {
        navigate('/home')
    }

    const handlePfpClicked = () => {
        navigate('/profile')
    }

    return (
        <div>
            <header className="bg-spring-green text-white text-center flex justify-between items-center p-5 w-full h-24 top-0">
                <img src="/logo.png" alt="AI Spy A Lie Logo" onClick={handleLogoClicked} className='w-16 h-16 rounded-full drop-shadow-lg'/>
                <img src="/cat_pfp.png" alt="Cat Profile Picture" onClick={handlePfpClicked} className='w-16 h-16 rounded-full drop-shadow-lg'/>
            </header>
        </div>
    )
}

export default Header;