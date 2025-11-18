import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import LaunchList from './components/LaunchList';
import LaunchDetail from './components/LaunchDetail';
import Statistics from './components/Statistics';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App min-h-screen bg-gray-50">
        <Navbar />
        <div className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<LaunchList />} />
            <Route path="/launch/:id" element={<LaunchDetail />} />
            <Route path="/statistics" element={<Statistics />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;