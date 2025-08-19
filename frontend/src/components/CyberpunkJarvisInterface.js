import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './CyberpunkJarvisInterface.css';

const CyberpunkJarvisInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [autoSpeak, setAutoSpeak] = useState(false);
  const [interactionMode, setInteractionMode] = useState('hybrid'); // 'voice-only', 'text-only', 'hybrid'
  const [availableVoices, setAvailableVoices] = useState([]);
  const [selectedVoiceIndex, setSelectedVoiceIndex] = useState(0);
  const [connectionStatus, setConnectionStatus] = useState('Initialisation...');
  
  const recognitionRef = useRef(null);
  const messagesEndRef = useRef(null);
  const synthRef = useRef(null);
  
  // Configuration API
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  const TTS_API_URL = process.env.REACT_APP_TTS_URL || 'http://localhost:8002';
  
  // Test de connexion au démarrage
  useEffect(() => {
    testConnection();
    const interval = setInterval(testConnection, 30000); // Test toutes les 30s
    return () => clearInterval(interval);
  }, []);
  
  const testConnection = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`, { 
        method: 'GET',
        timeout: 5000 
      });
      if (response.ok) {
        setIsConnected(true);
        setConnectionStatus('En ligne');
      } else {
        throw new Error('Backend non accessible');
      }
    } catch (error) {
      console.error('❌ Connexion backend échouée:', error);
      setIsConnected(false);
      setConnectionStatus('Hors ligne');
    }
  };
  
  // Configuration synthèse vocale et chargement des voix
  useEffect(() => {
    if ('speechSynthesis' in window) {
      synthRef.current = window.speechSynthesis;
      
      const loadVoices = () => {
        const voices = synthRef.current.getVoices();
        const frenchVoices = voices.filter(voice => 
          voice.lang.startsWith('fr') && 
          !voice.name.toLowerCase().includes('compact')
        );
        
        // Sélectionner jusqu'à 9 voix françaises différentes
        const selectedVoices = frenchVoices.slice(0, 9);
        setAvailableVoices(selectedVoices.length > 0 ? selectedVoices : voices.slice(0, 9));
        console.log('🗣️ Voix disponibles:', selectedVoices.length > 0 ? selectedVoices.length : voices.slice(0, 9).length);
      };
      
      // Charger les voix immédiatement si disponibles
      loadVoices();
      
      // Écouter le chargement des voix (pour certains navigateurs)
      synthRef.current.onvoiceschanged = loadVoices;
    }
  }, []);
  
  // Configuration reconnaissance vocale
  useEffect(() => {
    if (window.SpeechRecognition || window.webkitSpeechRecognition) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'fr-FR';
      
      recognitionRef.current.onstart = () => {
        setIsListening(true);
        console.log('🎤 Reconnaissance vocale démarrée');
      };
      
      recognitionRef.current.onresult = (event) => {
        let transcript = '';
        let interimTranscript = '';
        
        for (let i = 0; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            transcript += event.results[i][0].transcript;
          } else {
            interimTranscript += event.results[i][0].transcript;
          }
        }
        
        // En mode vocal uniquement, ne pas afficher le texte intermédiaire
        if (interactionMode !== 'voice-only') {
          setInputMessage(transcript || interimTranscript);
        }
        
        if (transcript.trim()) {
          console.log('🗣️ Transcription finale:', transcript);
          
          if (interactionMode === 'voice-only') {
            // En mode vocal pur, envoyer directement sans afficher le texte
            recognitionRef.current.stop();
            setIsListening(false);
            setTimeout(() => handleSendMessage(transcript), 300);
          } else {
            // En mode hybrid/text, afficher et permettre édition
            setInputMessage(transcript);
            recognitionRef.current.stop();
            setIsListening(false);
            
            // En mode hybrid, envoyer automatiquement après un délai
            if (interactionMode === 'hybrid') {
              setTimeout(() => handleSendMessage(transcript), 300);
            }
          }
        }
      };
      
      recognitionRef.current.onend = () => {
        setIsListening(false);
        console.log('🎤 Reconnaissance vocale terminée');
      };
      
      recognitionRef.current.onerror = (event) => {
        console.error('🔥 Erreur reconnaissance vocale:', event.error);
        setIsListening(false);
      };
    }
    
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, []);
  
  // Auto-scroll
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  // Synthèse vocale TTS
  const speakMessage = async (text) => {
    if (!text || isSpeaking) return;
    
    setIsSpeaking(true);
    
    // Utiliser UNIQUEMENT la synthèse vocale navigateur pour une voix naturelle
    if (synthRef.current && 'speechSynthesis' in window) {
      try {
        // Arrêter toute synthèse en cours
        synthRef.current.cancel();
        
        // Attendre que les voix soient chargées
        const loadVoices = () => {
          return new Promise((resolve) => {
            let voices = synthRef.current.getVoices();
            if (voices.length > 0) {
              resolve(voices);
            } else {
              synthRef.current.onvoiceschanged = () => {
                voices = synthRef.current.getVoices();
                resolve(voices);
              };
            }
          });
        };
        
        const voices = await loadVoices();
        
        // Utiliser la voix sélectionnée par l'utilisateur
        let selectedVoice = null;
        if (availableVoices.length > 0 && selectedVoiceIndex < availableVoices.length) {
          selectedVoice = availableVoices[selectedVoiceIndex];
        } else {
          // Fallback: chercher une voix française
          const frenchVoices = voices.filter(voice => 
            voice.lang.startsWith('fr') && 
            !voice.name.toLowerCase().includes('compact')
          );
          selectedVoice = frenchVoices[0] || voices[0];
        }
        
        const utterance = new SpeechSynthesisUtterance(text.substring(0, 300));
        utterance.lang = 'fr-FR';
        utterance.rate = 0.85;
        utterance.pitch = 1.0;
        utterance.volume = 0.9;
        
        if (selectedVoice) {
          utterance.voice = selectedVoice;
          console.log('🗣️ Voix sélectionnée:', selectedVoice.name, selectedVoice.lang);
        }
        
        utterance.onstart = () => {
          console.log('🔊 Synthèse vocale démarrée');
        };
        
        utterance.onend = () => {
          console.log('🔊 Synthèse vocale terminée');
          setIsSpeaking(false);
        };
        
        utterance.onerror = (error) => {
          console.error('🔥 Erreur synthèse vocale:', error);
          setIsSpeaking(false);
        };
        
        synthRef.current.speak(utterance);
        
      } catch (error) {
        console.error('🔥 Erreur TTS:', error);
        setIsSpeaking(false);
      }
    } else {
      console.warn('⚠️ Synthèse vocale non supportée');
      setIsSpeaking(false);
    }
    
    // Timeout de sécurité
    setTimeout(() => {
      if (isSpeaking) {
        synthRef.current?.cancel();
        setIsSpeaking(false);
      }
    }, 30000);
  };
  
  // Envoi de message
  const handleSendMessage = async (message) => {
    const messageToSend = message || inputMessage;
    if (!messageToSend.trim() || !isConnected) return;
    
    const sanitizedMessage = messageToSend.trim().substring(0, 5000);
    
    setIsLoading(true);
    setInputMessage('');
    
    // Ajouter message utilisateur
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: sanitizedMessage,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    
    try {
      console.log('📤 Envoi message vers backend...');
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: sanitizedMessage,
          user_id: 'enzo'
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('📥 Réponse backend:', data);
      
      // Ajouter réponse assistant
      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: data.response || 'Pas de réponse du système.',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      
      // Synthèse vocale automatique si activée
      if (autoSpeak) {
        setTimeout(() => {
          speakMessage(data.response);
        }, 1000);
      }
      
    } catch (error) {
      console.error('❌ Erreur chat:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: `⚠️ Erreur de connexion: ${error.message}. Vérifiez que le backend Jarvis est démarré sur le port 8000.`,
        timestamp: new Date(),
        isError: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    }
    
    setIsLoading(false);
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    handleSendMessage();
  };
  
  const toggleVoiceRecognition = () => {
    if (!recognitionRef.current) {
      alert('❌ Reconnaissance vocale non supportée par ce navigateur');
      return;
    }
    
    if (isListening) {
      recognitionRef.current.stop();
    } else {
      recognitionRef.current.start();
    }
  };
  
  const stopSpeaking = () => {
    if (synthRef.current) {
      synthRef.current.cancel();
    }
    setIsSpeaking(false);
  };
  
  const toggleAutoSpeak = () => {
    setAutoSpeak(!autoSpeak);
    console.log('🔊 Lecture automatique:', !autoSpeak ? 'ON' : 'OFF');
  };
  
  const speakLastMessage = () => {
    const lastAssistantMessage = messages.filter(msg => msg.type === 'assistant').pop();
    if (lastAssistantMessage && lastAssistantMessage.content) {
      speakMessage(lastAssistantMessage.content);
    } else {
      console.warn('⚠️ Aucune réponse à lire');
    }
  };
  
  const changeInteractionMode = (mode) => {
    setInteractionMode(mode);
    console.log('🎯 Mode d’interaction changé:', mode);
    
    // Ajuster comportements selon le mode
    if (mode === 'voice-only') {
      setAutoSpeak(true); // Activation automatique lecture
      setInputMessage(''); // Vider le champ de saisie
    } else if (mode === 'text-only') {
      setAutoSpeak(false); // Désactiver lecture automatique
      if (isListening) {
        recognitionRef.current?.stop();
      }
    }
  };
  
  const changeVoice = (direction) => {
    if (availableVoices.length === 0) return;
    
    let newIndex;
    if (direction === 'next') {
      newIndex = (selectedVoiceIndex + 1) % availableVoices.length;
    } else {
      newIndex = selectedVoiceIndex === 0 ? availableVoices.length - 1 : selectedVoiceIndex - 1;
    }
    
    setSelectedVoiceIndex(newIndex);
    const selectedVoice = availableVoices[newIndex];
    console.log('🗣️ Voix changée:', selectedVoice.name, selectedVoice.lang);
    
    // Test de la nouvelle voix
    speakMessage('Voix changée');
  };
  
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  return (
    <div className="cyberpunk-container">
      {/* Background animé */}
      <div className="cyberpunk-bg">
        <div className="grid-overlay"></div>
        <div className="particles">
          {[...Array(50)].map((_, i) => (
            <div key={i} className="particle" style={{
              left: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
              animationDuration: `${3 + Math.random() * 4}s`
            }}></div>
          ))}
        </div>
      </div>
      
      {/* Header */}
      <motion.header 
        className="cyberpunk-header"
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1 }}
      >
        <div className="header-left">
          <div className="jarvis-logo">
            <motion.div 
              className="logo-sphere"
              animate={{ 
                rotate: 360,
                scale: [1, 1.1, 1]
              }}
              transition={{ 
                rotate: { repeat: Infinity, duration: 10, ease: "linear" },
                scale: { repeat: Infinity, duration: 2, ease: "easeInOut" }
              }}
            >
              <div className="sphere-inner"></div>
            </motion.div>
            <div className="logo-text">
              <h1>J.A.R.V.I.S</h1>
              <p>Neural Interface v2.0</p>
            </div>
          </div>
        </div>
        
        <div className="header-right">
          {/* Sélecteur de mode d'interaction */}
          <div className="mode-selector">
            <motion.button
              className={`mode-btn ${interactionMode === 'voice-only' ? 'active' : ''}`}
              onClick={() => changeInteractionMode('voice-only')}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              title="Mode vocal uniquement"
            >
              🎤
            </motion.button>
            <motion.button
              className={`mode-btn ${interactionMode === 'hybrid' ? 'active' : ''}`}
              onClick={() => changeInteractionMode('hybrid')}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              title="Mode hybride (vocal + texte)"
            >
              📝🎤
            </motion.button>
            <motion.button
              className={`mode-btn ${interactionMode === 'text-only' ? 'active' : ''}`}
              onClick={() => changeInteractionMode('text-only')}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              title="Mode texte uniquement"
            >
              📝
            </motion.button>
          </div>
          
          {/* Sélecteur de voix */}
          {availableVoices.length > 1 && (
            <div className="voice-selector">
              <motion.button
                className="voice-btn"
                onClick={() => changeVoice('prev')}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                title="Voix précédente"
              >
                ◀️
              </motion.button>
              <span className="voice-info">
                {availableVoices[selectedVoiceIndex]?.name.substring(0, 15) || 'Voix'}
              </span>
              <motion.button
                className="voice-btn"
                onClick={() => changeVoice('next')}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                title="Voix suivante"
              >
                ▶️
              </motion.button>
            </div>
          )}
          
          <div className="status-indicators">
            <div className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`}></div>
            <span className="status-text">{connectionStatus}</span>
            
            {isListening && (
              <motion.div 
                className="listening-indicator"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ repeat: Infinity, duration: 1 }}
              >
                🎤 ÉCOUTE
              </motion.div>
            )}
            
            {isSpeaking && (
              <motion.div 
                className="speaking-indicator"
                animate={{ opacity: [0.5, 1, 0.5] }}
                transition={{ repeat: Infinity, duration: 0.8 }}
              >
                🔊 PARLE
              </motion.div>
            )}
          </div>
        </div>
      </motion.header>
      
      {/* Zone de chat */}
      <main className="chat-area">
        <div className="messages-container">
          <AnimatePresence>
            {messages.length === 0 ? (
              <motion.div 
                className="welcome-screen"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 1 }}
              >
                <motion.div 
                  className="welcome-orb"
                  animate={{ 
                    rotate: [0, 360],
                    scale: [1, 1.2, 1]
                  }}
                  transition={{ 
                    rotate: { repeat: Infinity, duration: 8, ease: "linear" },
                    scale: { repeat: Infinity, duration: 3, ease: "easeInOut" }
                  }}
                >
                  <div className="orb-ring ring-1"></div>
                  <div className="orb-ring ring-2"></div>
                  <div className="orb-ring ring-3"></div>
                  <div className="orb-core"></div>
                </motion.div>
                
                <h2>Bienvenue, Enzo</h2>
                <p>Système d'intelligence artificielle JARVIS opérationnel</p>
                <div className="mode-display">
                  <span className="current-mode">
                    Mode actuel: {
                      interactionMode === 'voice-only' ? '🎤 Vocal Uniquement' :
                      interactionMode === 'text-only' ? '📝 Texte Uniquement' :
                      '📝🎤 Hybride (Vocal + Texte)'
                    }
                  </span>
                </div>
                <div className="welcome-features">
                  <span>🎤 {availableVoices.length} voix disponibles</span>
                  <span>🔊 Synthèse vocale premium</span>
                  <span>🧠 IA neuromorphique</span>
                </div>
              </motion.div>
            ) : (
              <>
                {messages.map((msg) => (
                  <motion.div
                    key={msg.id}
                    className={`message-bubble ${msg.type} ${msg.isError ? 'error' : ''}`}
                    initial={{ opacity: 0, y: 50, scale: 0.8 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    transition={{ duration: 0.5 }}
                  >
                    <div className="message-avatar">
                      {msg.type === 'user' ? (
                        <div className="user-avatar">E</div>
                      ) : (
                        <motion.div 
                          className="ai-avatar"
                          animate={{ rotate: 360 }}
                          transition={{ repeat: Infinity, duration: 4, ease: "linear" }}
                        >
                          J
                        </motion.div>
                      )}
                    </div>
                    
                    <div className="message-content">
                      <div className="message-header">
                        <span className="sender-name">
                          {msg.type === 'user' ? 'Enzo' : 'J.A.R.V.I.S'}
                        </span>
                        <span className="message-time">
                          {msg.timestamp.toLocaleTimeString()}
                        </span>
                      </div>
                      
                      <div className="message-text">
                        {msg.content}
                      </div>
                    </div>
                  </motion.div>
                ))}
                
                {isLoading && (
                  <motion.div
                    className="message-bubble assistant loading"
                    initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: 1, y: 0 }}
                  >
                    <div className="message-avatar">
                      <motion.div 
                        className="ai-avatar"
                        animate={{ rotate: 360 }}
                        transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                      >
                        J
                      </motion.div>
                    </div>
                    
                    <div className="message-content">
                      <div className="loading-animation">
                        <motion.div className="typing-indicator">
                          <motion.span animate={{ opacity: [0, 1, 0] }} transition={{ repeat: Infinity, duration: 1, delay: 0 }}>●</motion.span>
                          <motion.span animate={{ opacity: [0, 1, 0] }} transition={{ repeat: Infinity, duration: 1, delay: 0.3 }}>●</motion.span>
                          <motion.span animate={{ opacity: [0, 1, 0] }} transition={{ repeat: Infinity, duration: 1, delay: 0.6 }}>●</motion.span>
                        </motion.div>
                        <span className="processing-text">J.A.R.V.I.S traite votre demande...</span>
                      </div>
                    </div>
                  </motion.div>
                )}
                
                <div ref={messagesEndRef} />
              </>
            )}
          </AnimatePresence>
        </div>
      </main>
      
      {/* Zone de saisie */}
      <motion.footer 
        className="input-area"
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1, delay: 0.5 }}
      >
        <form onSubmit={handleSubmit} className="input-form">
          <div className="input-container">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                !isConnected ? "Connexion au système..." :
                interactionMode === 'voice-only' ? "Mode vocal actif - Utilisez le micro" :
                interactionMode === 'text-only' ? "Tapez votre message..." :
                "Parlez à J.A.R.V.I.S ou tapez..."
              }
              className="message-input"
              disabled={!isConnected || interactionMode === 'voice-only'}
              rows={1}
              style={{
                display: interactionMode === 'voice-only' ? 'none' : 'block'
              }}
            />
            
            <div className="input-controls" style={{
              right: interactionMode === 'voice-only' ? '50%' : '10px',
              transform: interactionMode === 'voice-only' ? 'translateX(50%)' : 'translateY(-50%)'
            }}>
              {isSpeaking && (
                <motion.button
                  type="button"
                  onClick={stopSpeaking}
                  className="control-btn stop-btn"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  title="Arrêter la lecture"
                >
                  ⏹️
                </motion.button>
              )}
              
              <motion.button
                type="button"
                onClick={speakLastMessage}
                className="control-btn speak-btn"
                disabled={!isConnected || messages.filter(msg => msg.type === 'assistant').length === 0}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                title="Lire la dernière réponse"
              >
                🔊
              </motion.button>
              
              <motion.button
                type="button"
                onClick={toggleAutoSpeak}
                className={`control-btn auto-speak-btn ${autoSpeak ? 'active' : ''}`}
                disabled={!isConnected}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                title={`Lecture automatique: ${autoSpeak ? 'ON' : 'OFF'}`}
              >
                {autoSpeak ? '🔊' : '🔇'}
              </motion.button>
              
              <motion.button
                type="button"
                onClick={toggleVoiceRecognition}
                className={`control-btn mic-btn ${isListening ? 'listening' : ''} ${
                  interactionMode === 'voice-only' ? 'voice-only-mic' : ''
                }`}
                disabled={!isConnected || interactionMode === 'text-only'}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                title={
                  interactionMode === 'voice-only' ? 'Appuyer pour parler (mode vocal)' :
                  interactionMode === 'text-only' ? 'Non disponible en mode texte' :
                  'Reconnaissance vocale'
                }
              >
                {isListening ? '⏹️' : '🎤'}
              </motion.button>
              
              {interactionMode !== 'voice-only' && (
                <motion.button
                  type="submit"
                  disabled={!isConnected || !inputMessage.trim()}
                  className={`control-btn send-btn ${inputMessage.trim() && isConnected ? 'active' : ''}`}
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  title="Envoyer le message"
                >
                  ⚡
                </motion.button>
              )}
            </div>
          </div>
          
          {/* Affichage spécial mode vocal uniquement */}
          {interactionMode === 'voice-only' && !isListening && !isLoading && (
            <motion.div 
              className="voice-only-prompt"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <div className="voice-prompt-content">
                <motion.div 
                  className="pulse-circle"
                  animate={{ 
                    scale: [1, 1.2, 1],
                    opacity: [0.6, 1, 0.6]
                  }}
                  transition={{ 
                    repeat: Infinity, 
                    duration: 2,
                    ease: "easeInOut"
                  }}
                >
                  🎤
                </motion.div>
                <h3>Mode Vocal Actif</h3>
                <p>Cliquez sur le micro pour commencer à parler</p>
                <div className="voice-tips">
                  <span>• Parlez naturellement</span>
                  <span>• Conversation fluide</span>
                  <span>• Réponses vocales automatiques</span>
                </div>
              </div>
            </motion.div>
          )}
          
          {isListening && (
            <motion.div 
              className={`voice-feedback ${
                interactionMode === 'voice-only' ? 'voice-only-feedback' : ''
              }`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <div className="sound-waves">
                {[...Array(7)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="wave"
                    animate={{
                      height: [4, Math.random() * 25 + 10, 4],
                    }}
                    transition={{
                      repeat: Infinity,
                      duration: 0.8 + Math.random() * 0.4,
                      delay: i * 0.1
                    }}
                  />
                ))}
              </div>
              <span>
                {
                  interactionMode === 'voice-only' ? '🎤 Mode vocal - Parlez maintenant...' :
                  'Parlez maintenant...'
                }
              </span>
              {interactionMode === 'voice-only' && (
                <div className="voice-only-hint">
                  <small>Votre voix sera directement traitée sans affichage texte</small>
                </div>
              )}
            </motion.div>
          )}
          
          {/* Instructions mode vocal */}
          {interactionMode === 'voice-only' && (
            <motion.div 
              className="mode-instructions"
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.7 }}
              transition={{ delay: 1 }}
            >
              <small>
                🎤 Mode vocal: Conversation entièrement orale | 
                Voix: {availableVoices[selectedVoiceIndex]?.name || 'Défaut'}
              </small>
            </motion.div>
          )}
        </form>
      </motion.footer>
    </div>
  );
};

export default CyberpunkJarvisInterface;