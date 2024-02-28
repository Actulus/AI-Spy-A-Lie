import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import WelcomePage from "./components/Welcome";
import HomePage from "./components/Home";
import NotFoundPage from "./components/NotFound";
import ProfilePage from "./components/Profile";
import { useKindeAuth } from "@kinde-oss/kinde-auth-react";
import Layout from "./components/Layout";

function App() {  
  const { isAuthenticated, isLoading } = useKindeAuth();

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
              <Route path="/home" element={<HomePage />} />
              <Route path="/profile" element={<ProfilePage />} />
            </Route>
          )}
        </Routes>
      </Router>
    </div>
  );

}

export default App;
