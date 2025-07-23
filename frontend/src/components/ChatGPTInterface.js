import React, { useState, useEffect, useRef } from 'react';
import useWebSocket from 'react-use-websocket';

const ChatGPTInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isConnected, setIsConnected] = useState(true); // API REST toujours connecté
  const [isLoading, setIsLoading] = useState(false);
  const recognitionRef = useRef(null);
  const messagesEndRef = useRef(null);

  // Configuration API - authentification côté serveur uniquement
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';
  // API_KEY supprimée - authentification gérée côté serveur

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

  // Auto-scroll vers le bas
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Reconnaissance vocale
  useEffect(() => {
    if (window.SpeechRecognition || window.webkitSpeechRecognition) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'fr-FR';
      
      recognitionRef.current.onstart = () => setIsListening(true);
      
      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInputMessage(transcript);
        setIsListening(false);
      };
      
      recognitionRef.current.onend = () => setIsListening(false);
      recognitionRef.current.onerror = () => setIsListening(false);
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
        setIsLoading(false);
      } catch (error) {
        console.error('🔥 Erreur parsing message:', error);
        setIsLoading(false);
      }
    }
  }, [lastMessage]);

  const handleSendMessage = async (message) => {
    if (!message.trim()) return;
    
    setIsLoading(true);
    
    // Ajouter message utilisateur
    setMessages(prev => [...prev, {
      id: Date.now(),
      type: 'user',
      content: message.trim(),
      timestamp: new Date()
    }]);
    
    try {
      // Utiliser API REST - authentification gérée côté serveur
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message.trim(),
          user_id: 'enzo'
        })
      });
      
      const data = await response.json();
      
      // Ajouter réponse assistant
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        type: 'assistant',
        content: data.response,
        timestamp: new Date()
      }]);
      
    } catch (error) {
      console.error('❌ Erreur envoi message:', error);
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        type: 'assistant',
        content: 'Désolé, une erreur est survenue. Veuillez réessayer.',
        timestamp: new Date()
      }]);
    }
    
    setInputMessage('');
    setIsLoading(false);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleSendMessage(inputMessage);
  };

  const toggleVoiceRecognition = () => {
    if (!recognitionRef.current) {
      alert('❌ Reconnaissance vocale non supportée');
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
    } else {
      recognitionRef.current.start();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(inputMessage);
    }
  };

  const styles = {
    container: {
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      backgroundColor: '#343541',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    },
    header: {
      padding: '12px 16px',
      backgroundColor: '#202123',
      borderBottom: '1px solid #4d4d4f',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between'
    },
    title: {
      color: '#ececf1',
      fontSize: '16px',
      fontWeight: '600',
      margin: 0
    },
    status: {
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      fontSize: '12px',
      color: isConnected ? '#10a37f' : '#ef4444'
    },
    messagesContainer: {
      flex: 1,
      overflowY: 'auto',
      padding: '0'
    },
    messageGroup: {
      borderBottom: '1px solid #4d4d4f'
    },
    message: {
      padding: '24px',
      display: 'flex',
      gap: '16px',
      maxWidth: '768px',
      margin: '0 auto'
    },
    userMessage: {
      backgroundColor: '#343541'
    },
    assistantMessage: {
      backgroundColor: '#444654'
    },
    avatar: {
      width: '32px',
      height: '32px',
      borderRadius: '4px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: '18px',
      flexShrink: 0
    },
    userAvatar: {
      backgroundColor: '#5436da',
      color: 'white'
    },
    assistantAvatar: {
      backgroundColor: '#10a37f',
      color: 'white'
    },
    messageContent: {
      color: '#ececf1',
      lineHeight: '1.6',
      fontSize: '16px'
    },
    inputContainer: {
      padding: '16px',
      backgroundColor: '#343541'
    },
    inputWrapper: {
      position: 'relative',
      maxWidth: '768px',
      margin: '0 auto',
      backgroundColor: '#40414f',
      borderRadius: '8px',
      border: '1px solid #565869',
      display: 'flex',
      alignItems: 'flex-end'
    },
    textarea: {
      width: '100%',
      padding: '12px 80px 12px 16px',
      backgroundColor: 'transparent',
      border: 'none',
      outline: 'none',
      color: '#ececf1',
      fontSize: '16px',
      lineHeight: '1.5',
      resize: 'none',
      fontFamily: 'inherit'
    },
    buttonContainer: {
      position: 'absolute',
      right: '8px',
      bottom: '8px',
      display: 'flex',
      gap: '4px'
    },
    button: {
      width: '32px',
      height: '32px',
      borderRadius: '4px',
      border: 'none',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: '16px',
      transition: 'background-color 0.2s'
    },
    micButton: {
      backgroundColor: isListening ? '#ef4444' : '#565869',
      color: '#ececf1'
    },
    sendButton: {
      backgroundColor: inputMessage.trim() && isConnected ? '#10a37f' : '#565869',
      color: '#ececf1'
    },
    loadingContainer: {
      padding: '24px',
      display: 'flex',
      gap: '16px',
      maxWidth: '768px',
      margin: '0 auto',
      backgroundColor: '#444654',
      borderBottom: '1px solid #4d4d4f'
    },
    loadingDots: {
      display: 'flex',
      gap: '4px'
    },
    dot: {
      width: '8px',
      height: '8px',
      borderRadius: '50%',
      backgroundColor: '#10a37f',
      animation: 'pulse 1.4s ease-in-out infinite both'
    },
    emptyState: {
      flex: 1,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexDirection: 'column',
      color: '#8e8ea0',
      textAlign: 'center',
      padding: '48px 24px'
    }
  };

  return (
    <div style={styles.container}>
      <style>
        {`
          @keyframes pulse {
            0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
            40% { transform: scale(1); opacity: 1; }
          }
          .dot:nth-child(2) { animation-delay: 0.2s; }
          .dot:nth-child(3) { animation-delay: 0.4s; }
        `}
      </style>
      
      {/* Header */}
      <div style={styles.header}>
        <h1 style={styles.title}>Jarvis</h1>
        <div style={styles.status}>
          <div style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: isConnected ? '#10a37f' : '#ef4444'
          }}></div>
          {isConnected ? 'Connecté' : 'Déconnecté'}
        </div>
      </div>

      {/* Messages */}
      <div style={styles.messagesContainer}>
        {messages.length === 0 ? (
          <div style={styles.emptyState}>
            <div style={{ fontSize: '32px', marginBottom: '16px' }}>🤖</div>
            <h2 style={{ fontSize: '20px', margin: '0 0 8px 0', color: '#ececf1' }}>
              Bonjour Enzo !
            </h2>
            <p style={{ margin: 0, fontSize: '16px' }}>
              Comment puis-je vous aider aujourd'hui ?
            </p>
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <div key={msg.id} style={styles.messageGroup}>
                <div style={{
                  ...styles.message,
                  ...(msg.type === 'user' ? styles.userMessage : styles.assistantMessage)
                }}>
                  <div style={{
                    ...styles.avatar,
                    ...(msg.type === 'user' ? styles.userAvatar : styles.assistantAvatar)
                  }}>
                    {msg.type === 'user' ? '👤' : '🤖'}
                  </div>
                  <div style={styles.messageContent}>
                    {msg.content}
                  </div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div style={styles.loadingContainer}>
                <div style={styles.assistantAvatar}>🤖</div>
                <div style={styles.loadingDots}>
                  <div style={styles.dot} className="dot"></div>
                  <div style={styles.dot} className="dot"></div>
                  <div style={styles.dot} className="dot"></div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input */}
      <div style={styles.inputContainer}>
        <form onSubmit={handleSubmit}>
          <div style={styles.inputWrapper}>
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message Jarvis..."
              style={styles.textarea}
              rows={1}
              disabled={!isConnected}
            />
            <div style={styles.buttonContainer}>
              <button
                type="button"
                onClick={toggleVoiceRecognition}
                style={{
                  ...styles.button,
                  ...styles.micButton
                }}
                title="Reconnaissance vocale"
              >
                {isListening ? '⏹️' : '🎤'}
              </button>
              <button
                type="submit"
                disabled={!isConnected || !inputMessage.trim()}
                style={{
                  ...styles.button,
                  ...styles.sendButton
                }}
                title="Envoyer"
              >
                ↑
              </button>
            </div>
          </div>
        </form>
        
        {isListening && (
          <div style={{
            textAlign: 'center',
            marginTop: '8px',
            color: '#ef4444',
            fontSize: '14px'
          }}>
            🎤 En écoute...
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatGPTInterface;