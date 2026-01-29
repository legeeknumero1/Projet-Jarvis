import React, { useState, useEffect, useRef } from 'react';
import useWebSocket from 'react-use-websocket';
import DOMPurify from 'dompurify';
import { apiService } from '../services/api';
import './ChatGPTInterface.css';

const ChatGPTInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isConnected, setIsConnected] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);

  const API_KEY = process.env.REACT_APP_API_KEY || 'dev-key';
  const WS_URL = `${process.env.REACT_APP_WS_URL || 'ws://localhost:8100/ws'}?api_key=${API_KEY}`;

  const { lastMessage } = useWebSocket(WS_URL, {
    onOpen: () => setIsConnected(true),
    onClose: () => setIsConnected(false),
    shouldReconnect: () => true,
  });

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async (e) => {
    if (e) e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const content = DOMPurify.sanitize(inputMessage.trim());
    setInputMessage('');
    setIsLoading(true);

    // Ajout local immédiat
    setMessages(prev => [...prev, { id: Date.now(), type: 'user', content }]);

    try {
      const data = await apiService.sendMessage(content, conversationId);
      if (data.conversation_id) setConversationId(data.conversation_id);
      
      setMessages(prev => [...prev, {
        id: data.id,
        type: 'assistant',
        content: data.content
      }]);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="jarvis-container">
      <div className="jarvis-header">
        <h1 className="jarvis-title">Jarvis v1.9</h1>
        <div className={`status-indicator ${isConnected ? 'status-online' : 'status-offline'}`}>
          {isConnected ? '● Online' : '○ Offline'}
        </div>
      </div>

      <div className="messages-container">
        {messages.map((msg) => (
          <div key={msg.id} className={`message-row ${msg.type === 'user' ? 'message-user' : 'message-assistant'}`}>
            <div className={`avatar ${msg.type === 'user' ? 'avatar-user' : 'avatar-assistant'}`}>
              {msg.type === 'user' ? '👤' : '🤖'}
            </div>
            <div className="message-content">{msg.content}</div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <form onSubmit={handleSendMessage}>
          <div className="input-box">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage(e)}
              placeholder="Posez une question à Jarvis..."
              className="chat-textarea"
              rows={1}
            />
          </div>
        </form>
      </div>
    </div>
  );
};

export default ChatGPTInterface;
