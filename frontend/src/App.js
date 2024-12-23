import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Register from './components/register';
import Login from './components/login';

const App = () => {
    return (
        <Router>
            <nav>
                <Link to="/register">Register</Link> | 
                <Link to="/login">Login</Link> |
            </nav>

            <Routes>
                <Route path="/register" element={<Register />} />
                <Route path="/login" element={<Login />} />
            </Routes>
        </Router>
    );
};

export default App;
