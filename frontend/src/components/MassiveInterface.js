import React, { useState, useEffect } from 'react';
import styled, { keyframes } from 'styled-components';
import { motion } from 'framer-motion';
import { FiCpu, FiActivity, FiWifi, FiMic, FiSettings, FiPower, FiVolume2, FiHome, FiShield, FiDatabase, FiMonitor, FiHardDrive, FiClock, FiGlobe, FiUser, FiMail, FiCalendar, FiMap, FiCamera, FiMusic, FiVideo, FiTrend, FiSun, FiMoon, FiCloud, FiZap, FiCommand, FiTerminal, FiCode, FiGithub, FiLinkedin, FiTwitter, FiInstagram } from 'react-icons/fi';
import JarvisSphere from './JarvisSphere';
import MessageList from './chat/MessageList';

// Animations massives
const matrixRain = keyframes`
  0% { transform: translateY(-100vh); opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { transform: translateY(100vh); opacity: 0; }
`;

const neonPulse = keyframes`
  0%, 100% { 
    box-shadow: 
      0 0 20px rgba(0, 255, 255, 0.5),
      0 0 40px rgba(0, 255, 255, 0.3),
      0 0 60px rgba(0, 255, 255, 0.1),
      inset 0 0 20px rgba(0, 255, 255, 0.1);
  }
  50% { 
    box-shadow: 
      0 0 30px rgba(0, 255, 255, 0.8),
      0 0 60px rgba(0, 255, 255, 0.5),
      0 0 90px rgba(0, 255, 255, 0.3),
      inset 0 0 30px rgba(0, 255, 255, 0.2);
  }
`;

const scanlineMove = keyframes`
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100vw); }
`;

const hologramFlicker = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
  51% { opacity: 0.9; }
  52% { opacity: 0.8; }
  53% { opacity: 1; }
`;

const dataStream = keyframes`
  0% { transform: translateX(-100px); opacity: 0; }
  50% { opacity: 1; }
  100% { transform: translateX(100px); opacity: 0; }
`;

// Container principal MASSIF
const MassiveContainer = styled.div`
  width: 100vw;
  height: 100vh;
  background: 
    radial-gradient(circle at 10% 20%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgba(120, 255, 198, 0.2) 0%, transparent 50%),
    radial-gradient(circle at 60% 10%, rgba(255, 255, 120, 0.2) 0%, transparent 50%),
    linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 30%, #2a2a2a 60%, #1a1a1a 100%);
  position: relative;
  overflow: hidden;
  display: grid;
  grid-template-columns: 300px 1fr 300px;
  grid-template-rows: 100px 1fr 100px;
  gap: 20px;
  padding: 20px;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
      repeating-linear-gradient(
        90deg,
        transparent,
        transparent 100px,
        rgba(0, 255, 255, 0.03) 101px,
        rgba(0, 255, 255, 0.03) 102px
      ),
      repeating-linear-gradient(
        0deg,
        transparent,
        transparent 100px,
        rgba(0, 255, 255, 0.03) 101px,
        rgba(0, 255, 255, 0.03) 102px
      );
    pointer-events: none;
    z-index: 1;
  }
`;

// Effet Matrix
const MatrixBackground = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 1;
`;

const MatrixChar = styled.div`
  position: absolute;
  color: rgba(0, 255, 255, 0.5);
  font-family: 'Roboto Mono', monospace;
  font-size: 14px;
  animation: ${matrixRain} ${props => props.duration}s linear infinite;
  animation-delay: ${props => props.delay}s;
  left: ${props => props.left}%;
  top: -20px;
`;

const Scanline = styled.div`
  position: absolute;
  top: ${props => props.top}%;
  left: 0;
  width: 2px;
  height: 100vh;
  background: linear-gradient(to bottom, transparent, #00ffff, transparent);
  animation: ${scanlineMove} ${props => props.duration}s linear infinite;
  animation-delay: ${props => props.delay}s;
  z-index: 2;
`;

// Header massif
const MassiveHeader = styled.div`
  grid-column: 1 / -1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(0, 0, 0, 0.8);
  border: 1px solid rgba(0, 255, 255, 0.3);
  border-radius: 15px;
  padding: 20px 40px;
  backdrop-filter: blur(20px);
  animation: ${neonPulse} 3s ease-in-out infinite;
  position: relative;
  z-index: 10;
`;

const LogoSection = styled.div`
  display: flex;
  align-items: center;
  gap: 20px;
`;

const MassiveTitle = styled.h1`
  font-family: 'Orbitron', monospace;
  font-size: 3rem;
  color: #00ffff;
  text-shadow: 
    0 0 10px #00ffff,
    0 0 20px #00ffff,
    0 0 30px #00ffff;
  margin: 0;
  letter-spacing: 5px;
  animation: ${hologramFlicker} 2s ease-in-out infinite;
`;

const SystemStats = styled.div`
  display: flex;
  gap: 30px;
  font-family: 'Roboto Mono', monospace;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
`;

const StatItem = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  
  .icon {
    font-size: 20px;
    color: #00ffff;
  }
  
  .value {
    font-weight: 600;
    color: #00ffff;
  }
`;

// Panneau latéral gauche
const LeftPanel = styled.div`
  grid-row: 2;
  display: flex;
  flex-direction: column;
  gap: 20px;
  z-index: 10;
`;

const PanelSection = styled.div`
  background: rgba(0, 0, 0, 0.8);
  border: 1px solid rgba(0, 255, 255, 0.3);
  border-radius: 15px;
  padding: 20px;
  backdrop-filter: blur(20px);
  animation: ${neonPulse} 4s ease-in-out infinite;
  animation-delay: ${props => props.delay}s;
  
  h3 {
    color: #00ffff;
    font-family: 'Orbitron', monospace;
    margin: 0 0 15px 0;
    font-size: 1.2rem;
    text-transform: uppercase;
    letter-spacing: 2px;
  }
`;

const MenuItems = styled.div`
  display: flex;
  flex-direction: column;
  gap: 10px;
`;

const MenuItem = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 15px;
  border-radius: 8px;
  background: rgba(0, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Roboto Mono', monospace;
  
  &:hover {
    background: rgba(0, 255, 255, 0.2);
    color: #00ffff;
    transform: translateX(5px);
  }
  
  .icon {
    color: #00ffff;
  }
`;

// Zone centrale MASSIVE
const CentralArea = styled.div`
  grid-row: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 10;
`;

const SphereContainer = styled.div`
  transform: scale(2);
  margin: 50px 0;
`;

const ChatZone = styled.div`
  width: 100%;
  height: 60%;
  background: rgba(0, 0, 0, 0.9);
  border: 1px solid rgba(0, 255, 255, 0.3);
  border-radius: 20px;
  padding: 30px;
  backdrop-filter: blur(20px);
  animation: ${neonPulse} 5s ease-in-out infinite;
  overflow-y: auto;
  position: relative;
  
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.3);
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(0, 255, 255, 0.5);
    border-radius: 4px;
  }
`;

const MessageContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 15px;
  height: 100%;
`;

const Message = styled.div`
  padding: 15px 20px;
  border-radius: 15px;
  font-family: 'Exo 2', sans-serif;
  font-size: 16px;
  line-height: 1.6;
  max-width: 80%;
  
  ${props => props.isUser ? `
    background: rgba(0, 255, 255, 0.2);
    border: 1px solid rgba(0, 255, 255, 0.5);
    color: #ffffff;
    margin-left: auto;
    text-align: right;
  ` : `
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: #00ffff;
    margin-right: auto;
  `}
`;

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
`;

// Panneau latéral droit
const RightPanel = styled.div`
  grid-row: 2;
  display: flex;
  flex-direction: column;
  gap: 20px;
  z-index: 10;
`;

const DataStream = styled.div`
  font-family: 'Roboto Mono', monospace;
  font-size: 12px;
  color: rgba(0, 255, 255, 0.7);
  display: flex;
  align-items: center;
  gap: 10px;
  
  &::before {
    content: '${props => props.symbol}';
    animation: ${dataStream} 2s ease-in-out infinite;
    animation-delay: ${props => props.delay}s;
  }
`;

// Footer massif
const MassiveFooter = styled.div`
  grid-column: 1 / -1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(0, 0, 0, 0.8);
  border: 1px solid rgba(0, 255, 255, 0.3);
  border-radius: 15px;
  padding: 20px 40px;
  backdrop-filter: blur(20px);
  animation: ${neonPulse} 6s ease-in-out infinite;
  position: relative;
  z-index: 10;
`;

const FooterSection = styled.div`
  display: flex;
  align-items: center;
  gap: 20px;
  font-family: 'Roboto Mono', monospace;
  color: rgba(255, 255, 255, 0.8);
`;

const SocialLinks = styled.div`
  display: flex;
  gap: 15px;
  
  a {
    color: rgba(0, 255, 255, 0.7);
    font-size: 20px;
    transition: all 0.3s ease;
    
    &:hover {
      color: #00ffff;
      transform: scale(1.2);
    }
  }
`;

const MassiveInterface = ({ isConnected, isListening, messages, onSendMessage, onVoiceInput, setIsListening }) => {
  const [inputValue, setInputValue] = useState('');
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim() && onSendMessage) {
      onSendMessage(inputValue);
      setInputValue('');
    }
  };

  const MatrixEffect = () => {
    const chars = Array.from({ length: 50 }, (_, i) => (
      <MatrixChar
        key={i}
        left={Math.random() * 100}
        duration={Math.random() * 3 + 2}
        delay={Math.random() * 5}
      >
        {String.fromCharCode(0x30A0 + Math.random() * 96)}
      </MatrixChar>
    ));
    return <MatrixBackground>{chars}</MatrixBackground>;
  };

  const ScanlineEffect = () => {
    return (
      <>
        <Scanline top={20} duration={8} delay={0} />
        <Scanline top={50} duration={12} delay={2} />
        <Scanline top={80} duration={10} delay={4} />
      </>
    );
  };

  return (
    <MassiveContainer>
      <MatrixEffect />
      <ScanlineEffect />
      
      {/* Header massif */}
      <MassiveHeader>
        <LogoSection>
          <MassiveTitle>J.A.R.V.I.S</MassiveTitle>
          <div style={{ color: 'rgba(255, 255, 255, 0.7)', fontFamily: 'Roboto Mono' }}>
            Just A Rather Very Intelligent System
          </div>
        </LogoSection>
        
        <SystemStats>
          <StatItem>
            <FiCpu className="icon" />
            <div className="value">98.7%</div>
            <div>CPU</div>
          </StatItem>
          <StatItem>
            <FiDatabase className="icon" />
            <div className="value">2.4GB</div>
            <div>RAM</div>
          </StatItem>
          <StatItem>
            <FiHardDrive className="icon" />
            <div className="value">847GB</div>
            <div>Storage</div>
          </StatItem>
          <StatItem>
            <FiWifi className="icon" />
            <div className="value">{isConnected ? 'Online' : 'Offline'}</div>
            <div>Network</div>
          </StatItem>
        </SystemStats>
      </MassiveHeader>
      
      {/* Panneau gauche */}
      <LeftPanel>
        <PanelSection delay={0}>
          <h3>System Control</h3>
          <MenuItems>
            <MenuItem>
              <FiPower className="icon" />
              <span>Power Management</span>
            </MenuItem>
            <MenuItem>
              <FiSettings className="icon" />
              <span>Configuration</span>
            </MenuItem>
            <MenuItem>
              <FiMonitor className="icon" />
              <span>Display Settings</span>
            </MenuItem>
            <MenuItem>
              <FiShield className="icon" />
              <span>Security</span>
            </MenuItem>
          </MenuItems>
        </PanelSection>
        
        <PanelSection delay={1}>
          <h3>Smart Home</h3>
          <MenuItems>
            <MenuItem>
              <FiHome className="icon" />
              <span>Home Control</span>
            </MenuItem>
            <MenuItem>
              <FiSun className="icon" />
              <span>Lighting</span>
            </MenuItem>
            <MenuItem>
              <FiMusic className="icon" />
              <span>Entertainment</span>
            </MenuItem>
            <MenuItem>
              <FiCamera className="icon" />
              <span>Security Cameras</span>
            </MenuItem>
          </MenuItems>
        </PanelSection>
        
        <PanelSection delay={2}>
          <h3>Personal Assistant</h3>
          <MenuItems>
            <MenuItem>
              <FiCalendar className="icon" />
              <span>Calendar</span>
            </MenuItem>
            <MenuItem>
              <FiMail className="icon" />
              <span>Messages</span>
            </MenuItem>
            <MenuItem>
              <FiMap className="icon" />
              <span>Navigation</span>
            </MenuItem>
            <MenuItem>
              <FiCloud className="icon" />
              <span>Weather</span>
            </MenuItem>
          </MenuItems>
        </PanelSection>
      </LeftPanel>
      
      {/* Zone centrale */}
      <CentralArea>
        <SphereContainer>
          <JarvisSphere 
            isActive={isConnected && isListening}
            audioLevel={0.5}
          />
        </SphereContainer>
        
        <ChatZone>
          <MessageContainer>
            <MessageList messages={messages} />
          </MessageContainer>
        </ChatZone>
        
        <InputZone>
          <MassiveInput
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Posez votre question à J.A.R.V.I.S..."
            onKeyPress={(e) => e.key === 'Enter' && handleSubmit(e)}
          />
          <ActionButton onClick={handleSubmit}>
            <FiCommand />
          </ActionButton>
          <ActionButton 
            onClick={() => setIsListening(!isListening)}
            style={{ 
              background: isListening ? 'rgba(255, 0, 0, 0.3)' : 'rgba(0, 255, 255, 0.2)',
              borderColor: isListening ? 'rgba(255, 0, 0, 0.5)' : 'rgba(0, 255, 255, 0.5)'
            }}
          >
            <FiMic />
          </ActionButton>
        </InputZone>
      </CentralArea>
      
      {/* Panneau droit */}
      <RightPanel>
        <PanelSection delay={0}>
          <h3>System Status</h3>
          <DataStream symbol="▶" delay={0}>Neural Network: Active</DataStream>
          <DataStream symbol="◆" delay={0.5}>Voice Recognition: {isListening ? 'Listening' : 'Standby'}</DataStream>
          <DataStream symbol="●" delay={1}>Memory Core: Optimized</DataStream>
          <DataStream symbol="◉" delay={1.5}>Response Time: 247ms</DataStream>
        </PanelSection>
        
        <PanelSection delay={1}>
          <h3>Analytics</h3>
          <DataStream symbol="▲" delay={0}>Queries Today: 127</DataStream>
          <DataStream symbol="▼" delay={0.5}>Success Rate: 98.7%</DataStream>
          <DataStream symbol="♦" delay={1}>Learning Rate: 4.2%</DataStream>
          <DataStream symbol="◈" delay={1.5}>Uptime: 99.98%</DataStream>
        </PanelSection>
        
        <PanelSection delay={2}>
          <h3>Quick Actions</h3>
          <MenuItems>
            <MenuItem>
              <FiTerminal className="icon" />
              <span>Terminal</span>
            </MenuItem>
            <MenuItem>
              <FiCode className="icon" />
              <span>Code Editor</span>
            </MenuItem>
            <MenuItem>
              <FiGithub className="icon" />
              <span>GitHub</span>
            </MenuItem>
            <MenuItem>
              <FiZap className="icon" />
              <span>Automation</span>
            </MenuItem>
          </MenuItems>
        </PanelSection>
      </RightPanel>
      
      {/* Footer massif */}
      <MassiveFooter>
        <FooterSection>
          <FiClock />
          <span>{currentTime.toLocaleTimeString()}</span>
          <span>|</span>
          <span>{currentTime.toLocaleDateString()}</span>
        </FooterSection>
        
        <FooterSection>
          <span>Developed by Enzo</span>
          <span>|</span>
          <span>Perpignan, France</span>
        </FooterSection>
        
        <SocialLinks>
          <a href="#"><FiGithub /></a>
          <a href="#"><FiLinkedin /></a>
          <a href="#"><FiTwitter /></a>
          <a href="#"><FiInstagram /></a>
        </SocialLinks>
      </MassiveFooter>
    </MassiveContainer>
  );
};

export default MassiveInterface;