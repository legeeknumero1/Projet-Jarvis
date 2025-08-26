import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from './components/ui/toaster';
import ChatLayout from './components/ChatLayout';
import './styles/globals.css';

function App() {
  return (
    <div className="App min-h-screen bg-jarvis-bg text-jarvis-text">
      <Router>
        <Routes>
          <Route path="/" element={<ChatLayout />} />
        </Routes>
      </Router>
      <Toaster />
    </div>
  );
}

export default App;