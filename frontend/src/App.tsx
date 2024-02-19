import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import WelcomePage from "./components/Welcome";
import HomePage from "./components/Home";
import LoginPage from "./components/Login";
import RegisterPage from "./components/Register";
import NotFoundPage from "./components/NotFound";
import Header from "./components/partials/Header";
import Footer from "./components/partials/Footer";
import ProfilePage from "./components/Profile";

function App() {
  return (
    <Router>
      <div className="bg-gradient-to-b from-malachite to-dark-green min-h-screen min-w-screen font-roboto flex flex-col justify-between">
      <Header />
        <Routes>
          <Route path="/" element={<WelcomePage />} />
          <Route path="/home" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
        <Footer />
      </div>
    </Router>
  );

}

export default App
