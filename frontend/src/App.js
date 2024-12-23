import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Register from './components/register';
import Login from './components/login';
import TrainingPlanList from './components/training_plan_list';
import EditTrainingPlan from './components/edit_training_plan';

const App = () => {
    const coach_id = 9;

    return (
        <Router>
            <nav>
                <Link to="/register">Register</Link> | 
                <Link to="/login">Login</Link> |
                <Link to="/training_plan_list">TrainingPlanList</Link>
            </nav>

            <Routes>
                <Route path="/register" element={<Register />} />
                <Route path="/login" element={<Login />} />
                <Route path="/training_plan_list" element={<TrainingPlanList coach_id = {coach_id} />} />
                <Route path="/edit_training_plan/:plan_id" element={<EditTrainingPlan />} />
            </Routes>
        </Router>
    );
};

export default App;
