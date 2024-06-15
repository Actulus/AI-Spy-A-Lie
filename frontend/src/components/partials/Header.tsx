import React from "react";
import { useNavigate } from "react-router-dom";
import Button from "./Button";
import { useKindeAuth } from "@kinde-oss/kinde-auth-react";


const Header: React.FC = () => {
    const navigate = useNavigate();
    const user = useKindeAuth().user;
    const { logout } = useKindeAuth();
    const handleLogoClicked = () => {
        navigate('/home')
    }

    const handlePfpClicked = () => {
        navigate('/profile')
    }


    return (
        <header className="bg-spring-green text-white text-center flex justify-evenly md:justify-between items-center p-5 w-full h-24 top-0">
            <img src="/logo.png" alt="AI Spy A Lie Logo" onClick={handleLogoClicked} className='w-16 h-16 rounded-full drop-shadow-lg' />
            <div className="flex">
                <Button name='logout-button' onClick={logout}>Logout</Button>
                <img src={user?.picture || "/cat_pfp.png"} alt="Cat Profile Picture" onClick={handlePfpClicked} className='w-16 h-16 rounded-full drop-shadow-lg' />
            </div>
        </header>
    )
}

export default Header;