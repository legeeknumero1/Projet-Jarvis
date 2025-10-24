import React, { useEffect, useRef } from 'react';
import styled, { keyframes } from 'styled-components';
import { motion } from 'framer-motion';

const rotate = keyframes`
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
`;

const pulse = keyframes`
  0%, 100% {
    transform: scale(1);
    opacity: 0.8;
  }
  50% {
    transform: scale(1.1);
    opacity: 1;
  }
`;

const wave = keyframes`
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
`;

const SphereContainer = styled.div`
  position: relative;
  width: 200px;
  height: 200px;
  margin: 20px auto;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const SphereCore = styled(motion.div)`
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: 
    radial-gradient(circle at 30% 30%, rgba(0, 255, 255, 0.8) 0%, transparent 70%),
    radial-gradient(circle at 70% 70%, rgba(0, 255, 255, 0.4) 0%, transparent 70%),
    radial-gradient(circle at 50% 50%, rgba(0, 255, 255, 0.2) 0%, transparent 100%);
  border: 2px solid rgba(0, 255, 255, 0.6);
  box-shadow: 
    0 0 30px rgba(0, 255, 255, 0.5),
    0 0 60px rgba(0, 255, 255, 0.3),
    0 0 90px rgba(0, 255, 255, 0.1),
    inset 0 0 30px rgba(0, 255, 255, 0.2);
  animation: ${pulse} 2s ease-in-out infinite;
  position: relative;
  z-index: 3;
  
  &::before {
    content: '';
    position: absolute;
    top: 10px;
    left: 10px;
    right: 10px;
    bottom: 10px;
    border-radius: 50%;
    background: radial-gradient(circle at 40% 40%, rgba(255, 255, 255, 0.3) 0%, transparent 50%);
  }
`;

const OrbitRing = styled.div`
  position: absolute;
  border: 1px solid rgba(0, 255, 255, 0.3);
  border-radius: 50%;
  animation: ${rotate} ${props => props.duration}s linear infinite;
  
  &:nth-child(1) {
    width: 160px;
    height: 160px;
    top: 20px;
    left: 20px;
    animation-direction: normal;
  }
  
  &:nth-child(2) {
    width: 180px;
    height: 180px;
    top: 10px;
    left: 10px;
    animation-direction: reverse;
  }
  
  &:nth-child(3) {
    width: 200px;
    height: 200px;
    top: 0px;
    left: 0px;
    animation-direction: normal;
  }
`;

const ParticleWave = styled.div`
  position: absolute;
  width: 4px;
  height: 4px;
  background: rgba(0, 255, 255, 0.7);
  border-radius: 50%;
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
  animation: ${wave} 3s ease-in-out infinite;
  animation-delay: ${props => props.delay}s;
  
  &:nth-child(1) { top: 20%; left: 50%; }
  &:nth-child(2) { top: 40%; left: 80%; }
  &:nth-child(3) { top: 60%; left: 20%; }
  &:nth-child(4) { top: 80%; left: 50%; }
  &:nth-child(5) { top: 50%; left: 10%; }
  &:nth-child(6) { top: 30%; left: 70%; }
`;

const FrequencyBar = styled.div`
  position: absolute;
  bottom: -40px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 3px;
  align-items: end;
`;

const FrequencyLine = styled.div`
  width: 3px;
  background: linear-gradient(to top, #00ffff, rgba(0, 255, 255, 0.3));
  border-radius: 2px;
  animation: ${pulse} 0.5s ease-in-out infinite;
  animation-delay: ${props => props.delay}s;
  height: ${props => props.height}px;
`;

const JarvisSphere = ({ isActive, audioLevel }) => {
  const sphereRef = useRef(null);
  
  useEffect(() => {
    if (isActive && sphereRef.current) {
      sphereRef.current.style.transform = 'scale(1.2)';
      sphereRef.current.style.filter = 'brightness(1.5)';
    } else if (sphereRef.current) {
      sphereRef.current.style.transform = 'scale(1)';
      sphereRef.current.style.filter = 'brightness(1)';
    }
  }, [isActive]);

  const sphereVariants = {
    idle: { 
      scale: 1,
      rotate: 0,
      transition: { duration: 0.5 }
    },
    active: { 
      scale: 1.2,
      rotate: 360,
      transition: { 
        rotate: { duration: 2, repeat: Infinity, ease: "linear" },
        scale: { duration: 0.5 }
      }
    },
    speaking: {
      scale: [1, 1.3, 1],
      transition: { 
        duration: 0.6,
        repeat: Infinity,
        ease: "easeInOut"
      }
    }
  };

  return (
    <SphereContainer>
      <OrbitRing duration={8} />
      <OrbitRing duration={12} />
      <OrbitRing duration={16} />
      
      <SphereCore
        ref={sphereRef}
        variants={sphereVariants}
        animate={isActive ? "active" : "idle"}
        whileHover="speaking"
      >
        <ParticleWave delay={0} />
        <ParticleWave delay={0.5} />
        <ParticleWave delay={1} />
        <ParticleWave delay={1.5} />
        <ParticleWave delay={2} />
        <ParticleWave delay={2.5} />
      </SphereCore>
      
      <FrequencyBar>
        {[...Array(12)].map((_, i) => (
          <FrequencyLine
            key={i}
            height={Math.random() * 20 + 10}
            delay={i * 0.1}
          />
        ))}
      </FrequencyBar>
    </SphereContainer>
  );
};

export default JarvisSphere;