import React, { useState } from 'react';
import styled from 'styled-components';
import { FiCommand, FiMic } from 'react-icons/fi';

const InputZone = styled.div`
  width: 100%;
  margin-top: 20px;
  display: flex;
  gap: 15px;
  align-items: center;
`;

const MassiveInput = styled.input`
  flex: 1;
  padding: 15px 20px;
  background: rgba(0, 0, 0, 0.8);
  border: 1px solid rgba(0, 255, 255, 0.3);
  border-radius: 15px;
  color: #ffffff;
  font-family: 'Exo 2', sans-serif;
  font-size: 16px;
  backdrop-filter: blur(10px);
  
  &:focus {
    outline: none;
    border-color: #00ffff;
    box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);
  }
  
  &::placeholder {
    color: rgba(255, 255, 255, 0.5);
  }
`;

const ActionButton = styled.button`
  padding: 15px 20px;
  background: rgba(0, 255, 255, 0.2);
  border: 1px solid rgba(0, 255, 255, 0.5);
  border-radius: 15px;
  color: #00ffff;
  font-family: 'Orbitron', monospace;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(0, 255, 255, 0.3);
    transform: scale(1.05);
  }
  
  &:active {
    transform: scale(0.95);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`;

const Composer = ({ onSubmit, disabled, isListening, onVoiceToggle }) => {
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim() && !disabled) {
      onSubmit(inputValue);
      setInputValue('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSubmit(e);
    }
  };

  return (
    <InputZone>
      <MassiveInput
        type="text"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        placeholder="Posez votre question à J.A.R.V.I.S..."
        onKeyPress={handleKeyPress}
        disabled={disabled}
      />
      <ActionButton onClick={handleSubmit} disabled={disabled}>
        <FiCommand />
      </ActionButton>
      {onVoiceToggle && (
        <ActionButton 
          onClick={onVoiceToggle}
          style={{ 
            background: isListening ? 'rgba(255, 0, 0, 0.3)' : 'rgba(0, 255, 255, 0.2)',
            borderColor: isListening ? 'rgba(255, 0, 0, 0.5)' : 'rgba(0, 255, 255, 0.5)'
          }}
        >
          <FiMic />
        </ActionButton>
      )}
    </InputZone>
  );
};

export default Composer;