import React from "react"
import { Outlet } from "react-router-dom"
import Header from "./partials/Header"
import Footer from "./partials/Footer"

interface LayoutProps {
    isAdmin: boolean
}

const Layout: React.FC<LayoutProps> = ({isAdmin}:{isAdmin: boolean}) => {
    return (
        <div className="flex flex-col justify-between min-h-screen w-full">
            <Header isAdmin={isAdmin} />
            <Outlet />
            <Footer />
        </div>
    )
}

export default Layout;