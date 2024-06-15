import React from "react"
import { Outlet } from "react-router-dom"
import Header from "./partials/Header"
import Footer from "./partials/Footer"

const Layout: React.FC = () => {
    return (
        <div className="flex flex-col justify-between min-h-screen w-full">
            <Header />
            <Outlet />
            <Footer />
        </div>
    )
}

export default Layout;