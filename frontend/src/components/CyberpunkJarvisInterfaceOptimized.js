import React, { useState, useEffect, useRef, useCallback, useMemo, memo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './CyberpunkJarvisInterface.css';

// Composant Message optimisé avec React.memo
const MessageBubble = memo(({ msg, isLoading = false, onRetry }) => {
  const messageVariants = {
    initial: { opacity: 0, y: 50, scale: 0.8 },
    animate: { opacity: 1, y: 0, scale: 1 },
    exit: { opacity: 0, scale: 0.8 }
  };

  if (isLoading) {
    return (
      <motion.div
        className="message-bubble assistant loading"
        variants={messageVariants}
        initial="initial"
        animate="animate"
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
    );
  }

  return (
    <motion.div
      className={`message-bubble ${msg.type} ${msg.isError ? 'error' : ''}`}
      variants={messageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
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
        
        {msg.isError && onRetry && (
          <button 
            className="retry-button"
            onClick={onRetry}
            aria-label="Réessayer"
          >
            🔄 Réessayer
          </button>
        )}
      </div>
    </motion.div>
  );
});

MessageBubble.displayName = 'MessageBubble';

// Composant WelcomeScreen optimisé
const WelcomeScreen = memo(({ interactionMode, availableVoices }) => {
  const orbitVariants = {
    rotate: { rotate: [0, 360] },
    scale: { scale: [1, 1.2, 1] }
  };

  const getModeDisplay = useMemo(() => {
    switch(interactionMode) {
      case 'voice-only': return '🎤 Vocal Uniquement';
      case 'text-only': return '📝 Texte Uniquement';
      default: return '📝🎤 Hybride (Vocal + Texte)';
    }
  }, [interactionMode]);

  return (
    <motion.div 
      className="welcome-screen"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 1 }}
    >
      <motion.div 
        className="welcome-orb"
        animate={{ 
          rotate: orbitVariants.rotate.rotate,
          scale: orbitVariants.scale.scale
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
          Mode actuel: {getModeDisplay}
        </span>
      </div>
      <div className="welcome-features">
        <span>🎤 {availableVoices.length} voix disponibles</span>
        <span>🔊 Synthèse vocale premium</span>
        <span>🧠 IA neuromorphique</span>
      </div>
    </motion.div>
  );
});

WelcomeScreen.displayName = 'WelcomeScreen';

// Composant principal optimisé
const CyberpunkJarvisInterface = () => {
  // États optimisés avec useState
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [autoSpeak, setAutoSpeak] = useState(false);
  const [availableVoices, setAvailableVoices] = useState([]);
  const [selectedVoiceIndex, setSelectedVoiceIndex] = useState(0);
  const [isWsConnected, setIsWsConnected] = useState(false);
  
  // Variables non-utilisées dans cette version simplifiée mais gardées pour cohérence
  // const [isListening, setIsListening] = useState(false);
  // const [interactionMode, setInteractionMode] = useState('hybrid');
  // const [setSelectedVoiceIndex] = useState(0);
  
  // Refs optimisées
  const messagesEndRef = useRef(null);
  const synthRef = useRef(null);
  const inputRef = useRef(null);
  const wsRef = useRef(null);
  const isComponentMountedRef = useRef(true);
  
  // Refs non-utilisées dans cette version simplifiée
  // const recognitionRef = useRef(null);
  // const recognitionCleanupTimerRef = useRef(null);
  
  // Configuration API optimisée avec useMemo
  const apiConfig = useMemo(() => ({
    API_BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
    WS_URL: (() => {
      const WS_BASE_RAW = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';
      return WS_BASE_RAW.endsWith('/ws') ? WS_BASE_RAW : `${WS_BASE_RAW.replace(/\/$/, '')}/ws`;
    })()
  }), []);

  // Test de connexion optimisé avec useCallback
  const testConnection = useCallback(async () => {
    try {
      const controller = new AbortController();
      const id = setTimeout(() => controller.abort(), 5000);
      const response = await fetch(`${apiConfig.API_BASE_URL}/health`, {
        method: 'GET',
        signal: controller.signal
      });
      clearTimeout(id);
      if (response.ok) {
        setIsConnected(true);
      } else {
        throw new Error('Backend non accessible');
      }
    } catch (error) {
      console.error('❌ Connexion backend échouée:', error);
      setIsConnected(false);
    }
  }, [apiConfig.API_BASE_URL]);

  // Synthèse vocale optimisée avec useCallback - DÉPLACÉ AVANT connectWebSocket pour corriger le hoisting error
  const speakMessage = useCallback(async (text) => {
    if (!text || isSpeaking) return;
    
    setIsSpeaking(true);
    
    if (synthRef.current && 'speechSynthesis' in window) {
      try {
        synthRef.current.cancel();
        
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
        
        let selectedVoice = null;
        if (availableVoices.length > 0 && selectedVoiceIndex < availableVoices.length) {
          selectedVoice = availableVoices[selectedVoiceIndex];
          console.log('🎯 Voix utilisée:', selectedVoice.name, selectedVoice.lang);
        } else {
          selectedVoice = availableVoices[0] || voices[0];
          console.log('⚠️ Fallback voix:', selectedVoice?.name, selectedVoice?.lang);
        }
        
        const utterance = new SpeechSynthesisUtterance(text.substring(0, 300));
        
        if (selectedVoice) {
          utterance.lang = selectedVoice.lang;
        } else {
          utterance.lang = 'fr-FR';
        }
        
        utterance.rate = 0.9;
        utterance.pitch = 1.0;
        utterance.volume = 0.8;
        
        utterance.onend = () => {
          console.log('🔊 Synthèse vocale terminée');
          setIsSpeaking(false);
        };
        
        utterance.onerror = (error) => {
          console.error('❌ Erreur synthèse vocale:', error);
          setIsSpeaking(false);
        };
        
        synthRef.current.speak(utterance);
        
      } catch (error) {
        console.error('❌ Erreur synthèse:', error);
        setIsSpeaking(false);
      }
    } else {
      console.warn('⚠️ SpeechSynthesis non supporté');
      setIsSpeaking(false);
    }
  }, [isSpeaking, availableVoices, selectedVoiceIndex]);

  // WebSocket optimisé avec useCallback - Maintenant speakMessage est défini au-dessus
  const connectWebSocket = useCallback(() => {
    try {
      const ws = new WebSocket(apiConfig.WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsWsConnected(true);
      };
      
      ws.onclose = () => {
        setIsWsConnected(false);
        if (isComponentMountedRef.current) {
          setTimeout(() => connectWebSocket(), 3000);
        }
      };
      
      ws.onerror = () => {
        setIsWsConnected(false);
      };
      
      ws.onmessage = (evt) => {
        try {
          const data = JSON.parse(evt.data);
          if (data?.response) {
            const assistantMessage = {
              id: Date.now(),
              type: 'assistant',
              content: data.response,
              timestamp: new Date()
            };
            setMessages(prev => [...prev, assistantMessage]);
            // speakMessage est maintenant défini au-dessus, plus d'erreur hoisting
            if (autoSpeak && speakMessage) {
              setTimeout(() => speakMessage(data.response), 500);
            }
          }
        } catch (err) {
          console.error('Erreur parsing WS message:', err);
        }
      };
    } catch (err) {
      console.error('WS init error:', err);
    }
  }, [apiConfig.WS_URL, autoSpeak, speakMessage]);


  // Envoi de message optimisé avec useCallback
  const handleSendMessage = useCallback(async (message) => {
    const messageToSend = message || inputMessage;
    if (!messageToSend.trim() || !isConnected) return;
    
    const sanitizedMessage = messageToSend.trim().substring(0, 5000);
    
    setIsLoading(true);
    setInputMessage('');
    
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: sanitizedMessage,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    
    try {
      if (isWsConnected && wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          message: sanitizedMessage,
          user_id: 'enzo',
          timestamp: new Date().toISOString()
        }));
      } else {
        const controller = new AbortController();
        const id = setTimeout(() => controller.abort(), 15000);
        const response = await fetch(`${apiConfig.API_BASE_URL}/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: sanitizedMessage, user_id: 'enzo' }),
          signal: controller.signal
        });
        clearTimeout(id);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        const assistantMessage = {
          id: Date.now() + 1,
          type: 'assistant',
          content: data.response || 'Pas de réponse du système.',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, assistantMessage]);
        if (autoSpeak) setTimeout(() => speakMessage(data.response), 500);
      }
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: `⚠️ Erreur de connexion: ${error.message}. Vérifiez le backend/WS.`,
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    }
    
    setIsLoading(false);
  }, [inputMessage, isConnected, isWsConnected, autoSpeak, speakMessage, apiConfig.API_BASE_URL]);

  // Autres fonctions optimisées avec useCallback
  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  }, [handleSendMessage]);

  const handleSubmit = useCallback((e) => {
    e.preventDefault();
    handleSendMessage();
  }, [handleSendMessage]);

  const stopSpeaking = useCallback(() => {
    try {
      if (synthRef.current) {
        console.log('🛑 Arrêt synthèse vocale');
        synthRef.current.cancel();
      }
      setIsSpeaking(false);
    } catch (error) {
      console.error('🔥 Erreur arrêt synthèse:', error);
      setIsSpeaking(false);
    }
  }, []);

  const toggleAutoSpeak = useCallback(() => {
    const newAutoSpeak = !autoSpeak;
    setAutoSpeak(newAutoSpeak);
    console.log('🔊 Lecture automatique:', newAutoSpeak ? 'ACTIVÉE' : 'DÉSACTIVÉE');
    
    if (newAutoSpeak) {
      speakMessage('Lecture automatique activée');
    }
  }, [autoSpeak, speakMessage]);

  const speakLastMessage = useCallback(() => {
    const lastAssistantMessage = messages.filter(msg => msg.type === 'assistant').pop();
    if (lastAssistantMessage && lastAssistantMessage.content) {
      speakMessage(lastAssistantMessage.content);
    } else {
      console.warn('⚠️ Aucune réponse à lire');
    }
  }, [messages, speakMessage]);

  // Status text optimisé avec useMemo
  const statusText = useMemo(() => {
    if (isWsConnected) return 'En ligne (WS)';
    if (isConnected) return 'En ligne (REST)';
    return 'Hors ligne';
  }, [isWsConnected, isConnected]);

  // Auto-scroll optimisé
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  // Effect pour l'initialisation
  useEffect(() => {
    testConnection();
    connectWebSocket();
    const interval = setInterval(testConnection, 30000);
    return () => {
      isComponentMountedRef.current = false;
      clearInterval(interval);
      try { wsRef.current?.close(); } catch {}
    };
  }, [testConnection, connectWebSocket]);

  // Effect pour auto-scroll optimisé
  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Effect pour auto-resize optimisé
  useEffect(() => {
    if (inputRef.current) {
      const el = inputRef.current;
      el.style.height = 'auto';
      el.style.height = Math.min(el.scrollHeight, 150) + 'px';
    }
  }, [inputMessage]);

  // Configuration voix optimisée
  useEffect(() => {
    let voiceLoadTimeout = null;
    
    if ('speechSynthesis' in window) {
      synthRef.current = window.speechSynthesis;
      
      const loadVoices = () => {
        if (!isComponentMountedRef.current) return;
        
        try {
          const allVoices = synthRef.current.getVoices();
          console.log('🔍 Toutes les voix détectées:', allVoices.map(v => `${v.name} (${v.lang})`));
        
          let frenchVoices = allVoices.filter(voice => 
            voice.lang.startsWith('fr') || 
            voice.lang.includes('FR') ||
            voice.name.toLowerCase().includes('french') ||
            voice.name.toLowerCase().includes('français')
          );
          
          if (frenchVoices.length === 0) {
            console.warn('⚠️ Aucune voix française trouvée, recherche alternatives...');
            
            frenchVoices = allVoices.filter(voice => 
              (voice.lang.startsWith('en-GB') || voice.lang.startsWith('en-UK')) ||
              voice.name.toLowerCase().includes('british') ||
              voice.name.toLowerCase().includes('uk')
            );
            
            if (frenchVoices.length === 0) {
              frenchVoices = allVoices.filter(voice => 
                voice.name.toLowerCase().includes('european') ||
                voice.lang.startsWith('de') ||
                voice.lang.startsWith('es') ||
                voice.lang.startsWith('it')
              );
            }
            
            if (frenchVoices.length === 0) {
              frenchVoices = allVoices.filter(voice => 
                voice.lang.startsWith('en-US') && (
                  voice.name.toLowerCase().includes('zira') ||
                  voice.name.toLowerCase().includes('eva') ||
                  voice.name.toLowerCase().includes('aria') ||
                  voice.name.toLowerCase().includes('jenny')
                )
              );
            }
            
            if (frenchVoices.length === 0) {
              frenchVoices = allVoices.filter(voice => 
                voice.lang.startsWith('en-US') &&
                !voice.name.toLowerCase().includes('compact') &&
                !voice.name.toLowerCase().includes('enhanced')
              );
            }
            
            console.log('🔄 Voix alternatives sélectionnées:', frenchVoices.map(v => `${v.name} (${v.lang})`));
          }
          
          const selectedVoices = frenchVoices.slice(0, 9);
          
          if (isComponentMountedRef.current) {
            setAvailableVoices(selectedVoices.length > 0 ? selectedVoices : allVoices.slice(0, 9));
          }
          
          console.log('✅ Voix sélectionnées:', selectedVoices.map(v => `${v.name} (${v.lang})`));
          console.log(`🎤 ${selectedVoices.length} voix configurées`);
        } catch (error) {
          console.error('Erreur lors du chargement des voix:', error);
        }
      };
      
      try {
        loadVoices();
        
        if (synthRef.current) {
          synthRef.current.onvoiceschanged = loadVoices;
        }
        
        voiceLoadTimeout = setTimeout(() => {
          if (isComponentMountedRef.current && availableVoices.length === 0) {
            console.warn('⚠️ Timeout chargement voix, utilisation voix par défaut');
            setAvailableVoices([]);
          }
        }, 5000);
        
      } catch (error) {
        console.error('🔥 Erreur chargement voix:', error);
        if (isComponentMountedRef.current) {
          setAvailableVoices([]);
        }
      }
    }
    
    return () => {
      if (voiceLoadTimeout) {
        clearTimeout(voiceLoadTimeout);
      }
      if (synthRef.current && synthRef.current.onvoiceschanged) {
        synthRef.current.onvoiceschanged = null;
      }
    };
  }, []);

  // Interface JSX optimisée avec composants mémorisés
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
      
      {/* Header optimisé */}
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
          <div className="status-indicators">
            <div className={`status-dot ${(isWsConnected || isConnected) ? 'connected' : 'disconnected'}`}></div>
            <span className="status-text">{statusText}</span>
            
            {/* Indicateur d'écoute temporairement désactivé dans cette version */}
            {false && (
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

      {/* Zone de chat optimisée */}
      <main className="chat-area">
        <div className="messages-container">
          <AnimatePresence>
            {messages.length === 0 ? (
              <WelcomeScreen 
                interactionMode="hybrid"
                availableVoices={availableVoices}
              />
            ) : (
              <>
                {messages.map((msg) => (
                  <MessageBubble
                    key={msg.id}
                    msg={msg}
                    onRetry={msg.isError ? () => handleSendMessage(msg.content) : null}
                  />
                ))}
                
                {isLoading && <MessageBubble isLoading={true} />}
                
                <div ref={messagesEndRef} />
              </>
            )}
          </AnimatePresence>
        </div>
      </main>
      
      {/* Zone de saisie optimisée */}
      <motion.footer 
        className="input-area"
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1, delay: 0.5 }}
      >
        <form onSubmit={handleSubmit} className="input-form">
          <div className="input-container">
            <textarea
              ref={inputRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                !isConnected ? "Connexion au système..." :
                "Parlez à J.A.R.V.I.S ou tapez..."
              }
              className="message-input"
              disabled={!isConnected}
              rows={1}
              aria-label="Saisir un message pour Jarvis"
            />
          
            <div className="input-controls">
              {isSpeaking && (
                <motion.button
                  type="button"
                  onClick={stopSpeaking}
                  className="control-btn stop-btn"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  title="Arrêter la lecture"
                  aria-label="Arrêter la lecture"
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
                aria-label="Lire la dernière réponse"
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
                aria-pressed={autoSpeak}
                aria-label="Activer la lecture automatique"
              >
                {autoSpeak ? '🔊' : '🔇'}
              </motion.button>
            
              <motion.button
                type="submit"
                disabled={!isConnected || !inputMessage.trim()}
                className={`control-btn send-btn ${inputMessage.trim() && isConnected ? 'active' : ''}`}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                title="Envoyer le message"
                aria-label="Envoyer le message"
              >
                ⚡
              </motion.button>
            </div>
          </div>
        </form>
      </motion.footer>
    </div>
  );
};

export default memo(CyberpunkJarvisInterface);