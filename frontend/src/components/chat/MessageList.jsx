import React, { useEffect, useRef } from 'react';
import MessageItem from './MessageItem';

const MessageList = ({ messages }) => {
  const messagesEndRef = useRef(null);

  // Auto-scroll vers le bas quand nouveaux messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div>
      {messages.map((message, index) => (
        <MessageItem 
          key={message.id || index}
          role={message.type} 
          text={message.content}
          timestamp={message.timestamp}
        />
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;