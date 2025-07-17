import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import ChatInterface from './components/ChatInterface';
import VoiceControl from './components/VoiceControl';
import StatusBar from './components/StatusBar';
import useWebSocket from 'react-use-websocket';

const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
`;

const MainContent = styled(motion.div)`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  padding: 30px;
  max-width: 800px;
  width: 100%;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
`;

const Header = styled.div`
  text-align: center;
  margin-bottom: 30px;
`;

const Title = styled.h1`
  color: white;
  font-size: 3rem;
  margin: 0;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  font-weight: 300;
`;

const Subtitle = styled.p`
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.2rem;
  margin: 10px 0 0 0;
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
    <AppContainer>
      <MainContent
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <Header>
          <Title>JARVIS</Title>
          <Subtitle>Assistant IA Personnel</Subtitle>
        </Header>
        
        <StatusBar 
          isConnected={isConnected}
          isListening={isListening}
        />
        
        <ChatInterface 
          messages={messages}
          onSendMessage={handleSendMessage}
          isConnected={isConnected}
        />
        
        <VoiceControl 
          onVoiceInput={handleVoiceInput}
          isConnected={isConnected}
          isListening={isListening}
          setIsListening={setIsListening}
        />
      </MainContent>
    </AppContainer>
  );
}

export default App;