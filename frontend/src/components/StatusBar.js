import React from 'react';
import styled, { keyframes } from 'styled-components';
import { motion } from 'framer-motion';
import { FiWifi, FiWifiOff, FiMic, FiMicOff, FiCpu, FiActivity } from 'react-icons/fi';

const scanLine = keyframes`
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
`;

const dataFlow = keyframes`
  0% { opacity: 0; transform: translateX(-20px); }
  50% { opacity: 1; transform: translateX(0px); }
  100% { opacity: 0; transform: translateX(20px); }
`;

const StatusContainer = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 15px;
  margin-bottom: 25px;
  backdrop-filter: blur(15px);
  border: 1px solid rgba(0, 255, 255, 0.3);
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00ffff, transparent);
    animation: ${scanLine} 2s linear infinite;
  }
  
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(45deg, transparent 48%, rgba(0, 255, 255, 0.05) 50%, transparent 52%);
    pointer-events: none;
  }
`;

const StatusItem = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  color: white;
  font-size: 14px;
  position: relative;
  z-index: 1;
`;

const StatusIcon = styled(motion.div)`
  font-size: 18px;
  color: ${props => props.isActive ? '#00ffff' : '#ff4757'};
  filter: drop-shadow(0 0 8px ${props => props.isActive ? '#00ffff' : '#ff4757'});
`;

const StatusText = styled.span`
  color: rgba(255, 255, 255, 0.9);
  font-family: 'Roboto Mono', monospace;
  font-weight: 300;
  letter-spacing: 1px;
  text-transform: uppercase;
`;

const StatusDot = styled(motion.div)`
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: ${props => props.isActive ? '#00ffff' : '#ff4757'};
  box-shadow: 0 0 15px ${props => props.isActive ? '#00ffff' : '#ff4757'};
  margin-right: 8px;
`;

const SystemStats = styled.div`
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  font-family: 'Roboto Mono', monospace;
`;

const StatItem = styled.div`
  display: flex;
  align-items: center;
  gap: 5px;
  
  &::before {
    content: '';
    width: 8px;
    height: 1px;
    background: rgba(0, 255, 255, 0.5);
    animation: ${dataFlow} 1s ease-in-out infinite;
    animation-delay: ${props => props.delay}s;
  }
`;

const ActivityIndicator = styled.div`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100px;
  height: 2px;
  background: linear-gradient(90deg, transparent, #00ffff, transparent);
  opacity: ${props => props.isActive ? 1 : 0};
  animation: ${props => props.isActive ? scanLine : 'none'} 1s linear infinite;
  pointer-events: none;
`;

const StatusBar = ({ isConnected, isListening }) => {
  const pulseAnimation = {
    scale: [1, 1.3, 1],
    opacity: [0.7, 1, 0.7],
    transition: {
      duration: 0.8,
      repeat: Infinity,
      ease: "easeInOut"
    }
  };

  return (
    <StatusContainer>
      <ActivityIndicator isActive={isConnected && isListening} />
      
      <StatusItem>
        <StatusDot 
          isActive={isConnected}
          animate={isConnected ? pulseAnimation : {}}
        />
        <StatusIcon isActive={isConnected}>
          {isConnected ? <FiWifi /> : <FiWifiOff />}
        </StatusIcon>
        <StatusText>
          {isConnected ? 'Neural Link' : 'Offline'}
        </StatusText>
      </StatusItem>
      
      <SystemStats>
        <StatItem delay={0}>
          <FiCpu />
          <span>AI Core</span>
        </StatItem>
        <StatItem delay={0.2}>
          <FiActivity />
          <span>Active</span>
        </StatItem>
      </SystemStats>
      
      <StatusItem>
        <StatusDot 
          isActive={isListening}
          animate={isListening ? pulseAnimation : {}}
        />
        <StatusIcon isActive={isListening}>
          {isListening ? <FiMic /> : <FiMicOff />}
        </StatusIcon>
        <StatusText>
          {isListening ? 'Listening' : 'Standby'}
        </StatusText>
      </StatusItem>
    </StatusContainer>
  );
};

export default StatusBar;