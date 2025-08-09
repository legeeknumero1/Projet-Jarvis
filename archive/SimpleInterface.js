import React, { useState, useEffect, useRef } from 'react';
import useWebSocket from 'react-use-websocket';

const SimpleInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const recognitionRef = useRef(null);

  const WS_URL = 'ws://localhost:8000/ws';

  const { 
    sendMessage, 
    lastMessage, 
    readyState 
  } = useWebSocket(WS_URL, {
    onOpen: () => {
      console.log('✅ WebSocket connecté');
      setIsConnected(true);
    },
    onClose: () => {
      console.log('❌ WebSocket déconnecté');
      setIsConnected(false);
    },
    onError: (error) => {
      console.error('🔥 WebSocket erreur:', error);
      setIsConnected(false);
    },
    shouldReconnect: () => true,
    reconnectInterval: 3000,
  });

  // Instance #6 - EN_COURS - Correction reconnaissance vocale native
  useEffect(() => {
    // Initialiser reconnaissance vocale native
    if (window.SpeechRecognition || window.webkitSpeechRecognition) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'fr-FR';
      
      recognitionRef.current.onstart = () => {
        console.log('🎤 Reconnaissance vocale démarrée');
        setIsListening(true);
      };
      
      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        console.log('🗣️ Transcription:', transcript);
        handleSendMessage(transcript);
      };
      
      recognitionRef.current.onend = () => {
        console.log('🎤 Reconnaissance vocale arrêtée');
        setIsListening(false);
      };
      
      recognitionRef.current.onerror = (event) => {
        console.error('🔥 Erreur reconnaissance:', event.error);
        setIsListening(false);
      };
    } else {
      console.warn('⚠️ Reconnaissance vocale non supportée');
    }
  }, []);

  useEffect(() => {
    if (lastMessage !== null) {
      try {
        const data = JSON.parse(lastMessage.data);
        setMessages(prev => [...prev, {
          id: Date.now(),
          type: 'assistant',
          content: data.response,
          timestamp: new Date()
        }]);
      } catch (error) {
        console.error('🔥 Erreur parsing message:', error);
      }
    }
  }, [lastMessage]);

  const handleSendMessage = (message) => {
    if (!isConnected || !sendMessage || !message.trim()) return;

    const messageData = {
      message: message.trim(),
      user_id: 'enzo',
      timestamp: new Date().toISOString()
    };

    // Ajouter message utilisateur
    setMessages(prev => [...prev, {
      id: Date.now(),
      type: 'user',
      content: message.trim(),
      timestamp: new Date()
    }]);

    // Envoyer via WebSocket
    sendMessage(JSON.stringify(messageData));
    setInputMessage('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleSendMessage(inputMessage);
  };

  const toggleVoiceRecognition = () => {
    if (!recognitionRef.current) {
      alert('❌ Reconnaissance vocale non supportée par votre navigateur');
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
    } else {
      recognitionRef.current.start();
    }
  };

  return (
    <div style={{
      fontFamily: 'Arial, sans-serif',
      maxWidth: '800px',
      margin: '0 auto',
      padding: '20px',
      backgroundColor: '#1a1a1a',
      color: '#ffffff',
      minHeight: '100vh'
    }}>
      <h1 style={{
        textAlign: 'center',
        color: '#00ffff',
        marginBottom: '30px',
        fontSize: '2.5rem'
      }}>
        JARVIS V1
      </h1>

      <div style={{
        backgroundColor: '#2a2a2a',
        padding: '20px',
        borderRadius: '10px',
        marginBottom: '20px'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '15px'
        }}>
          <span>Statut: {isConnected ? '✅ Connecté' : '❌ Déconnecté'}</span>
          <span>Messages: {messages.length}</span>
        </div>
      </div>

      {/* Zone des messages */}
      <div style={{
        backgroundColor: '#2a2a2a',
        padding: '20px',
        borderRadius: '10px',
        height: '400px',
        overflowY: 'auto',
        marginBottom: '20px',
        border: '1px solid #444'
      }}>
        {messages.length === 0 ? (
          <p style={{ color: '#888', textAlign: 'center' }}>
            Aucun message. Commencez une conversation !
          </p>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              style={{
                marginBottom: '15px',
                padding: '10px',
                borderRadius: '8px',
                backgroundColor: msg.type === 'user' ? '#0066cc' : '#2d5a2d',
                marginLeft: msg.type === 'user' ? '20%' : '0',
                marginRight: msg.type === 'user' ? '0' : '20%'
              }}
            >
              <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
                {msg.type === 'user' ? '🧑 Enzo' : '🤖 Jarvis'}
              </div>
              <div>{msg.content}</div>
              <div style={{ fontSize: '12px', color: '#ccc', marginTop: '5px' }}>
                {msg.timestamp.toLocaleTimeString()}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Zone de saisie */}
      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '10px' }}>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Tapez votre message..."
          style={{
            flex: 1,
            padding: '12px',
            borderRadius: '5px',
            border: '1px solid #555',
            backgroundColor: '#333',
            color: '#fff',
            fontSize: '16px'
          }}
        />
        <button
          type="submit"
          disabled={!isConnected || !inputMessage.trim()}
          style={{
            padding: '12px 20px',
            borderRadius: '5px',
            border: 'none',
            backgroundColor: isConnected ? '#00aa00' : '#666',
            color: '#fff',
            cursor: isConnected ? 'pointer' : 'not-allowed',
            fontSize: '16px'
          }}
        >
          Envoyer
        </button>
        <button
          type="button"
          onClick={toggleVoiceRecognition}
          style={{
            padding: '12px 20px',
            borderRadius: '5px',
            border: 'none',
            backgroundColor: isListening ? '#ff4444' : '#0066cc',
            color: '#fff',
            cursor: 'pointer',
            fontSize: '16px'
          }}
        >
          {isListening ? '🔴 Stop' : '🎤 Micro'}
        </button>
      </form>

      {isListening && (
        <div style={{
          textAlign: 'center',
          marginTop: '10px',
          color: '#ff4444',
          fontSize: '14px'
        }}>
          🎤 Parlez maintenant...
        </div>
      )}
    </div>
  );
};

export default SimpleInterface;