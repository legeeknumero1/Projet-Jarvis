import React, { useEffect, useState } from 'react';
import { ChatProvider } from '../../context/ChatContext';
import StatusBar from './StatusBar';
import MessageList from '../chat/MessageList';
import Composer from '../chat/Composer';
import { useChat } from '../../context/ChatContext';

const ChatLayoutInner = () => {
  const { state, actions } = useChat();
  const [ws, setWs] = useState(null);

  // Configuration WebSocket
  const API_KEY = process.env.REACT_APP_API_KEY || 'jarvis-dev-key';
  const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';

  // Hook WebSocket
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        const websocket = new WebSocket(WS_URL);
        
        websocket.onopen = () => {
          console.log('✅ WebSocket connecté');
          actions.setConnected(true);
          setWs(websocket);
        };

        websocket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            console.log('📨 WS message reçu:', data);
            
            if (data.response) {
              actions.addMessage({
                id: Date.now(),
                type: 'assistant',
                content: data.response,
                timestamp: new Date()
              });
            }
          } catch (error) {
            console.error('❌ Erreur parsing WS message:', error);
          }
        };

        websocket.onclose = () => {
          console.log('🔌 WebSocket déconnecté');
          actions.setConnected(false);
          setWs(null);
          
          // Reconnexion automatique après 3s
          setTimeout(connectWebSocket, 3000);
        };

        websocket.onerror = (error) => {
          console.error('❌ WebSocket erreur:', error);
          actions.setConnected(false);
        };
        
      } catch (error) {
        console.error('❌ Erreur connexion WebSocket:', error);
        actions.setConnected(false);
      }
    };

    connectWebSocket();

    // Cleanup
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  const handleSendMessage = (text) => {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      console.error('❌ WebSocket non connecté');
      return;
    }

    // Ajouter message utilisateur
    actions.addMessage({
      id: Date.now(),
      type: 'user', 
      content: text,
      timestamp: new Date()
    });

    // Envoyer via WebSocket
    ws.send(JSON.stringify({
      message: text,
      user_id: 'enzo'
    }));
  };

  const handleVoiceToggle = () => {
    actions.setListening(!state.isListening);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 text-white">
      {/* Header avec StatusBar */}
      <header className="p-6 border-b border-cyan-500/20">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
            J.A.R.V.I.S
          </h1>
          <StatusBar />
        </div>
      </header>

      {/* Zone principale de chat */}
      <main className="flex-1 flex flex-col max-h-[calc(100vh-120px)]">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6">
          <MessageList messages={state.messages} />
        </div>

        {/* Composer fixe en bas */}
        <div className="p-6 border-t border-cyan-500/20 bg-black/20 backdrop-blur-md">
          <Composer 
            onSubmit={handleSendMessage}
            disabled={state.isLoading}
            isListening={state.isListening}
            onVoiceToggle={handleVoiceToggle}
          />
        </div>
      </main>
    </div>
  );
};

const ChatLayout = () => {
  return (
    <ChatProvider>
      <ChatLayoutInner />
    </ChatProvider>
  );
};

export default ChatLayout;