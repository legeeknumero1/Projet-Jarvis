import React from 'react';
import styled from 'styled-components';

const Message = styled.div`
  margin: 1rem 0;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  font-size: 1rem;
  line-height: 1.5;
  position: relative;
  backdrop-filter: blur(10px);
  
  ${props => props.isUser ? `
    background: linear-gradient(135deg, 
      rgba(0, 255, 255, 0.1), 
      rgba(0, 200, 255, 0.05)
    );
    border: 1px solid rgba(0, 255, 255, 0.3);
    margin-left: 20%;
    text-align: right;
  ` : `
    background: linear-gradient(135deg, 
      rgba(255, 255, 255, 0.05), 
      rgba(200, 200, 200, 0.02)
    );
    border: 1px solid rgba(255, 255, 255, 0.1);
    margin-right: 20%;
  `}

  &::before {
    content: '';
    position: absolute;
    top: 50%;
    ${props => props.isUser ? 'right: -10px;' : 'left: -10px;'}
    width: 0;
    height: 0;
    border: 10px solid transparent;
    ${props => props.isUser ? 
      'border-left-color: rgba(0, 255, 255, 0.3);' : 
      'border-right-color: rgba(255, 255, 255, 0.1);'
    }
    transform: translateY(-50%);
  }
`;

const MessageItem = ({ role, text, timestamp }) => {
  const isUser = role === 'user';
  
  return (
    <Message isUser={isUser}>
      {text}
    </Message>
  );
};

export default MessageItem;