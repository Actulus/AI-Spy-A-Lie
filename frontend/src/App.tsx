import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import WelcomePage from "./components/Welcome";
import HomePage from "./components/Home";
import LoginPage from "./components/Login";
import RegisterPage from "./components/Register";
import NotFoundPage from "./components/NotFound";

function App() {
  return (
    <Router>
      <div className="bg-gradient-to-b from-malachite to-dark-green min-h-screen min-w-screen">
        <Routes>
          <Route path="/" element={<WelcomePage />} />
          <Route path="/home" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </div>
    </Router>
  );

}

export default App
