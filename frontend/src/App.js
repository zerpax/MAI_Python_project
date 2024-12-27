import React, {useEffect} from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Register from './components/register';
import Login from './components/login';

const App = () => {
    useEffect(() => {
        // TrackerSDK will be available after the script loads
        const script = document.createElement('script');
        script.src = 'http://127.0.0.1:8001/SDK_tracker.js';
        script.async = true;
        script.onload = () => {
          if (window.TrackerSDK) {
            window.TrackerSDK.init(); // Initialize the tracker
          }
        };
        document.head.appendChild(script);
      }, []);
    return (
        <Router>
            <nav>
                <Link to="/register">Register</Link> | 
                <Link to="/login">Login</Link> |
            </nav>

            <Routes>
                <Route path="/" element={<MainPage />} />
                <Route path="/register" element={<Register />} />
                <Route path="/login" element={<Login />} />
            </Routes>
        </Router>
    );
};

const MainPage = () => {
  return <h1>Welcome to the Main Page</h1>;
};

export default App;
