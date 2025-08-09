import React from 'react';
import MessageItem from './MessageItem';

const MessageList = ({ messages }) => {
  return (
    <div>
      {messages.map((message, index) => (
        <MessageItem 
          key={index}
          role={message.type} 
          text={message.content}
          timestamp={message.timestamp}
        />
      ))}
    </div>
  );
};

export default MessageList;