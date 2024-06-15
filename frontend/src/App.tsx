import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import WelcomePage from "./components/Welcome";
import HomePage from "./components/Home";
import NotFoundPage from "./components/NotFound";
import ProfilePage from "./components/Profile";
import { useKindeAuth } from "@kinde-oss/kinde-auth-react";
import Layout from "./components/Layout";
import PlayGamePage from "./components/PlayGame";
import GamePage from "./components/Game";
import Statistics from "./components/Statistics";
import { useState, useEffect } from "react";

function App() {
  const { isAuthenticated, isLoading } = useKindeAuth();
  const user = useKindeAuth().user;
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    if(!user) return;
    fetch(`${import.meta.env.VITE_BACKEND_URL}/api/users/${user?.id}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    })
      .then(response => response.json())
      .then((data) => {
        const is_admin = data.is_admin;
        setIsAdmin(is_admin);
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  }, [user]);

  if (isLoading) {
    return <div className="bg-gradient-to-b from-malachite to-dark-green min-h-screen min-w-screen">Loading...</div>;
  }

  return (
    <div className="bg-gradient-to-b from-malachite to-dark-green min-h-screen min-w-screen font-roboto">
      <Router>
        <Routes>
          <Route path="/" element={<WelcomePage />} />
          <Route path="*" element={<NotFoundPage />} />
          {isAuthenticated && (
            <Route path="/" element={<Layout />} >
              <Route path="/home" element={<HomePage isAdmin={isAdmin} />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/play-game" element={<PlayGamePage />} />
              <Route path="/game/:difficulty" element={<GamePage />} />
              <Route path="/statistics" element={<Statistics />} />
            </Route>
          )}
        </Routes>
      </Router>
    </div>
  );
}

export default App;