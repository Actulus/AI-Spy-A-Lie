import { useEffect, useState } from "react";
const Home = () => {
    const [message, setMessage] = useState<string>("")

    useEffect (() => {
        fetch("http://127.0.0.1:5000/hello")
        .then((response) => response.json())
        .then((data) => setMessage(data.msg))
    }
    , []);

    return (
        <div>
        <h1 className="text-4xl text-gray-500">Home</h1>
        
        {message && <h1 className="text-4xl text-gray-500">{message}</h1>}
        </div>
    )
}

export default Home;