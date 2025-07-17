import React, { useState, useEffect } from 'react';
import styled, { keyframes } from 'styled-components';
import { motion } from 'framer-motion';
import ChatInterface from './components/ChatInterface';
import VoiceControl from './components/VoiceControl';
import StatusBar from './components/StatusBar';
import JarvisSphere from './components/JarvisSphere';
import MassiveInterface from './components/MassiveInterface';
import useWebSocket from 'react-use-websocket';

// Cyberpunk-inspired animations
const neonGlow = keyframes`
  0%, 100% { 
    text-shadow: 0 0 5px #00ffff, 0 0 10px #00ffff, 0 0 15px #00ffff, 0 0 20px #00ffff;
  }
  50% { 
    text-shadow: 0 0 2px #00ffff, 0 0 5px #00ffff, 0 0 8px #00ffff, 0 0 12px #00ffff;
  }
`;

const pulseGlow = keyframes`
  0%, 100% { 
    box-shadow: 0 0 20px rgba(0, 255, 255, 0.3), 0 0 40px rgba(0, 255, 255, 0.1), inset 0 0 20px rgba(0, 255, 255, 0.1);
  }
  50% { 
    box-shadow: 0 0 30px rgba(0, 255, 255, 0.5), 0 0 60px rgba(0, 255, 255, 0.2), inset 0 0 30px rgba(0, 255, 255, 0.2);
  }
`;

const AppContainer = styled.div`
  min-height: 100vh;
  background: 
    radial-gradient(circle at 20% 20%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgba(120, 255, 198, 0.2) 0%, transparent 50%),
    linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #2a2a2a 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.02'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E") repeat;
    pointer-events: none;
    z-index: 1;
  }
`;

const MainContent = styled(motion.div)`
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 1px solid rgba(0, 255, 255, 0.3);
  animation: ${pulseGlow} 3s ease-in-out infinite;
  padding: 40px;
  max-width: 900px;
  width: 100%;
  max-height: 85vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 2;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(45deg, transparent 48%, rgba(0, 255, 255, 0.1) 50%, transparent 52%);
    pointer-events: none;
  }
`;

const Header = styled.div`
  text-align: center;
  margin-bottom: 30px;
  position: relative;
`;

const Title = styled.h1`
  color: #00ffff;
  font-size: 4rem;
  margin: 0;
  font-weight: 100;
  font-family: 'Orbitron', monospace;
  letter-spacing: 8px;
  animation: ${neonGlow} 2s ease-in-out infinite;
  text-transform: uppercase;
  
  &::before {
    content: 'JARVIS';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    color: rgba(0, 255, 255, 0.3);
    z-index: -1;
    transform: translate(2px, 2px);
  }
`;

const Subtitle = styled.p`
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.3rem;
  margin: 15px 0 0 0;
  font-family: 'Roboto', sans-serif;
  letter-spacing: 2px;
  text-transform: uppercase;
  font-weight: 300;
`;

const WS_URL = process.env.NODE_ENV === 'production' 
  ? 'ws://localhost:8000/ws' 
  : 'ws://localhost:8000/ws';

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState([]);
  const [isListening, setIsListening] = useState(false);
  
  const { 
    sendMessage, 
    lastMessage, 
    readyState,
    getWebSocket 
  } = useWebSocket(WS_URL, {
    onOpen: () => {
      console.log('WebSocket connected');
      setIsConnected(true);
    },
    onClose: () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
    },
    onError: (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    },
    shouldReconnect: (closeEvent) => true,
    reconnectAttempts: 10,
    reconnectInterval: 3000,
  });

  useEffect(() => {
    if (lastMessage !== null) {
      try {
        const data = JSON.parse(lastMessage.data);
        setMessages(prev => [...prev, {
          id: Date.now(),
          type: 'assistant',
          content: data.response,
          timestamp: new Date(data.timestamp)
        }]);
      } catch (error) {
        console.error('Error parsing message:', error);
      }
    }
  }, [lastMessage]);

  const handleSendMessage = (message) => {
    if (isConnected && sendMessage) {
      const messageData = {
        message: message,
        user_id: 'default',
        timestamp: new Date().toISOString()
      };
      
      // Ajouter le message utilisateur
      setMessages(prev => [...prev, {
        id: Date.now(),
        type: 'user',
        content: message,
        timestamp: new Date()
      }]);
      
      // Envoyer via WebSocket
      sendMessage(JSON.stringify(messageData));
    }
  };

  const handleVoiceInput = (transcript) => {
    if (transcript) {
      handleSendMessage(transcript);
    }
  };

  const containerVariants = {
    hidden: { opacity: 0, y: 50 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: {
        duration: 0.8,
        ease: "easeOut"
      }
    }
  };

  return (
    <MassiveInterface 
      isConnected={isConnected}
      isListening={isListening}
      messages={messages}
      onSendMessage={handleSendMessage}
      onVoiceInput={handleVoiceInput}
      setIsListening={setIsListening}
    />
  );
}

export default App;