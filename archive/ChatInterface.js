import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { FiSend, FiUser, FiCpu } from 'react-icons/fi';

const ChatContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  margin-bottom: 20px;
  max-height: 400px;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 10px;
  }
`;

const MessageBubble = styled(motion.div)`
  display: flex;
  margin-bottom: 15px;
  align-items: flex-start;
  justify-content: ${props => props.isUser ? 'flex-end' : 'flex-start'};
`;

const MessageContent = styled.div`
  max-width: 70%;
  padding: 15px 20px;
  border-radius: 20px;
  background: ${props => props.isUser 
    ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    : 'rgba(255, 255, 255, 0.1)'};
  color: white;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  
  p {
    margin: 0;
    line-height: 1.4;
  }
`;

const MessageIcon = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: ${props => props.isUser 
    ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    : 'rgba(255, 255, 255, 0.1)'};
  display: flex;
  align-items: center;
  justify-content: center;
  margin: ${props => props.isUser ? '0 0 0 10px' : '0 10px 0 0'};
  color: white;
  font-size: 18px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
`;

const MessageTime = styled.div`
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 5px;
`;

const InputContainer = styled.div`
  display: flex;
  gap: 10px;
  align-items: center;
`;

const MessageInput = styled.input`
  flex: 1;
  padding: 15px 20px;
  border: none;
  border-radius: 25px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 16px;
  outline: none;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  
  &::placeholder {
    color: rgba(255, 255, 255, 0.6);
  }
  
  &:focus {
    border-color: rgba(255, 255, 255, 0.4);
    box-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
  }
`;

const SendButton = styled(motion.button)`
  width: 50px;
  height: 50px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const EmptyState = styled.div`
  text-align: center;
  color: rgba(255, 255, 255, 0.6);
  padding: 40px;
  
  h3 {
    margin-bottom: 10px;
  }
  
  p {
    font-size: 14px;
    line-height: 1.6;
  }
`;

const ChatInterface = ({ messages, onSendMessage, isConnected }) => {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim() && isConnected) {
      onSendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('fr-FR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const messageVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: {
        duration: 0.3,
        ease: "easeOut"
      }
    }
  };

  return (
    <ChatContainer>
      <MessagesContainer>
        {messages.length === 0 ? (
          <EmptyState>
            <h3>Bonjour ! Je suis Jarvis</h3>
            <p>
              Votre assistant IA personnel. Vous pouvez me parler en tapant un message
              ou en utilisant la commande vocale. Je peux vous aider avec la domotique,
              répondre à vos questions, et bien plus encore !
            </p>
          </EmptyState>
        ) : (
          <AnimatePresence>
            {messages.map((message) => (
              <MessageBubble 
                key={message.id}
                isUser={message.type === 'user'}
                variants={messageVariants}
                initial="hidden"
                animate="visible"
              >
                {message.type === 'assistant' && (
                  <MessageIcon isUser={false}>
                    <FiCpu />
                  </MessageIcon>
                )}
                
                <div>
                  <MessageContent isUser={message.type === 'user'}>
                    <p>{message.content}</p>
                  </MessageContent>
                  <MessageTime>
                    {formatTime(message.timestamp)}
                  </MessageTime>
                </div>
                
                {message.type === 'user' && (
                  <MessageIcon isUser={true}>
                    <FiUser />
                  </MessageIcon>
                )}
              </MessageBubble>
            ))}
          </AnimatePresence>
        )}
        <div ref={messagesEndRef} />
      </MessagesContainer>
      
      <form onSubmit={handleSubmit}>
        <InputContainer>
          <MessageInput
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={isConnected ? "Tapez votre message..." : "Connexion en cours..."}
            disabled={!isConnected}
          />
          <SendButton
            type="submit"
            disabled={!isConnected || !inputValue.trim()}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <FiSend />
          </SendButton>
        </InputContainer>
      </form>
    </ChatContainer>
  );
};

export default ChatInterface;