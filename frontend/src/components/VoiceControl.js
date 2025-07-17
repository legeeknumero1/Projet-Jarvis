import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { FiMic, FiMicOff } from 'react-icons/fi';

const VoiceContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  margin-top: 20px;
`;

const VoiceButton = styled(motion.button)`
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: none;
  background: ${props => props.isListening 
    ? 'linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%)'
    : 'linear-gradient(135deg, #51cf66 0%, #40c057 100%)'};
  color: white;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  position: relative;
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const PulseRing = styled(motion.div)`
  position: absolute;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.4);
  top: -2px;
  left: -2px;
`;

const VoiceStatus = styled.div`
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  text-align: center;
  min-width: 120px;
`;

const TranscriptDisplay = styled(motion.div)`
  background: rgba(255, 255, 255, 0.1);
  padding: 15px 20px;
  border-radius: 15px;
  color: white;
  font-style: italic;
  max-width: 300px;
  text-align: center;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  margin-top: 15px;
`;

const VoiceControl = ({ onVoiceInput, isConnected, isListening, setIsListening }) => {
  const [transcript, setTranscript] = useState('');
  const [recognition, setRecognition] = useState(null);
  const [isSupported, setIsSupported] = useState(false);

  useEffect(() => {
    // Vérifier si l'API Speech Recognition est supportée
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognitionInstance = new SpeechRecognition();
      
      recognitionInstance.continuous = false;
      recognitionInstance.interimResults = true;
      recognitionInstance.lang = 'fr-FR';
      recognitionInstance.maxAlternatives = 1;
      
      recognitionInstance.onstart = () => {
        setIsListening(true);
        setTranscript('');
      };
      
      recognitionInstance.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }
        
        setTranscript(finalTranscript || interimTranscript);
        
        if (finalTranscript) {
          onVoiceInput(finalTranscript);
        }
      };
      
      recognitionInstance.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        setTranscript('');
      };
      
      recognitionInstance.onend = () => {
        setIsListening(false);
      };
      
      setRecognition(recognitionInstance);
      setIsSupported(true);
    } else {
      setIsSupported(false);
    }
  }, [onVoiceInput, setIsListening]);

  const toggleListening = () => {
    if (!recognition || !isConnected) return;
    
    if (isListening) {
      recognition.stop();
    } else {
      recognition.start();
    }
  };

  const getStatusText = () => {
    if (!isSupported) return 'Non supporté';
    if (!isConnected) return 'Déconnecté';
    if (isListening) return 'Écoute...';
    return 'Cliquez pour parler';
  };

  const pulseAnimation = {
    scale: [1, 1.2, 1],
    opacity: [0.7, 0.3, 0.7],
    transition: {
      duration: 1.5,
      repeat: Infinity,
      ease: "easeInOut"
    }
  };

  return (
    <VoiceContainer>
      <div>
        <VoiceButton
          onClick={toggleListening}
          disabled={!isSupported || !isConnected}
          isListening={isListening}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          {isListening ? (
            <>
              <FiMicOff />
              <PulseRing animate={pulseAnimation} />
            </>
          ) : (
            <FiMic />
          )}
        </VoiceButton>
        
        <VoiceStatus>
          {getStatusText()}
        </VoiceStatus>
        
        {transcript && (
          <TranscriptDisplay
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            "{transcript}"
          </TranscriptDisplay>
        )}
      </div>
    </VoiceContainer>
  );
};

export default VoiceControl;