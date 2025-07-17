import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { FiWifi, FiWifiOff, FiMic, FiMicOff } from 'react-icons/fi';

const StatusContainer = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  margin-bottom: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
`;

const StatusItem = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
  font-size: 14px;
`;

const StatusIcon = styled(motion.div)`
  font-size: 16px;
  color: ${props => props.isActive ? '#51cf66' : '#ff6b6b'};
`;

const StatusText = styled.span`
  color: rgba(255, 255, 255, 0.9);
`;

const StatusDot = styled(motion.div)`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: ${props => props.isActive ? '#51cf66' : '#ff6b6b'};
  margin-right: 5px;
`;

const StatusBar = ({ isConnected, isListening }) => {
  const pulseAnimation = {
    scale: [1, 1.2, 1],
    opacity: [0.7, 1, 0.7],
    transition: {
      duration: 1,
      repeat: Infinity,
      ease: "easeInOut"
    }
  };

  return (
    <StatusContainer>
      <StatusItem>
        <StatusDot 
          isActive={isConnected}
          animate={isConnected ? pulseAnimation : {}}
        />
        <StatusIcon isActive={isConnected}>
          {isConnected ? <FiWifi /> : <FiWifiOff />}
        </StatusIcon>
        <StatusText>
          {isConnected ? 'Connecté' : 'Déconnecté'}
        </StatusText>
      </StatusItem>
      
      <StatusItem>
        <StatusDot 
          isActive={isListening}
          animate={isListening ? pulseAnimation : {}}
        />
        <StatusIcon isActive={isListening}>
          {isListening ? <FiMic /> : <FiMicOff />}
        </StatusIcon>
        <StatusText>
          {isListening ? 'Écoute' : 'Veille'}
        </StatusText>
      </StatusItem>
    </StatusContainer>
  );
};

export default StatusBar;