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
  const inputRef = useRef(null);
  
  // Configuration API
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  // WebSocket (normalisé pour garantir le suffixe /ws)
  const WS_BASE_RAW = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';
  const WS_URL = (WS_BASE_RAW.endsWith('/ws') ? WS_BASE_RAW : `${WS_BASE_RAW.replace(/\/$/, '')}/ws`);
  
  // WebSocket
  const wsRef = useRef(null);
  const [isWsConnected, setIsWsConnected] = useState(false);

  // Test de connexion au démarrage (REST health) + gestion WebSocket
  useEffect(() => {
    testConnection();
    connectWebSocket();
    const interval = setInterval(testConnection, 30000); // Test toutes les 30s
    return () => {
      clearInterval(interval);
      try { wsRef.current?.close(); } catch {}
    };
  }, []);

  const connectWebSocket = () => {
    try {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsWsConnected(true);
      };
      ws.onclose = () => {
        setIsWsConnected(false);
        // Reconnexion automatique simple
        setTimeout(() => connectWebSocket(), 3000);
      };
      ws.onerror = (e) => {
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
            // Lecture auto si activée
            if (autoSpeak) {
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
  };
  
  const testConnection = async () => {
    try {
      const controller = new AbortController();
      const id = setTimeout(() => controller.abort(), 5000);
      const response = await fetch(`${API_BASE_URL}/health`, {
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
  };
  
  // Configuration synthèse vocale et chargement des voix
  useEffect(() => {
    if ('speechSynthesis' in window) {
      synthRef.current = window.speechSynthesis;
      
      const loadVoices = () => {
        const allVoices = synthRef.current.getVoices();
        console.log('🔍 Toutes les voix détectées:', allVoices.map(v => `${v.name} (${v.lang})`));
        
        // Priorité aux voix françaises
        let frenchVoices = allVoices.filter(voice => 
          voice.lang.startsWith('fr') || 
          voice.lang.includes('FR') ||
          voice.name.toLowerCase().includes('french') ||
          voice.name.toLowerCase().includes('français')
        );
        
        // Si pas de voix françaises, chercher alternatives de qualité
        if (frenchVoices.length === 0) {
          console.warn('⚠️ Aucune voix française trouvée, recherche alternatives...');
          
          // Priorité 1: Voix UK/britanniques (meilleur accent)
          frenchVoices = allVoices.filter(voice => 
            (voice.lang.startsWith('en-GB') || voice.lang.startsWith('en-UK')) ||
            voice.name.toLowerCase().includes('british') ||
            voice.name.toLowerCase().includes('uk')
          );
          
          // Priorité 2: Voix européennes
          if (frenchVoices.length === 0) {
            frenchVoices = allVoices.filter(voice => 
              voice.name.toLowerCase().includes('european') ||
              voice.lang.startsWith('de') || // Allemand
              voice.lang.startsWith('es') || // Espagnol
              voice.lang.startsWith('it')    // Italien
            );
          }
          
          // Priorité 3: Voix femmes US (plus agréables)
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
          
          // Priorité 4: Toutes voix US sans compact/enhanced
          if (frenchVoices.length === 0) {
            frenchVoices = allVoices.filter(voice => 
              voice.lang.startsWith('en-US') &&
              !voice.name.toLowerCase().includes('compact') &&
              !voice.name.toLowerCase().includes('enhanced')
            );
          }
          
          console.log('🔄 Voix alternatives sélectionnées:', frenchVoices.map(v => `${v.name} (${v.lang})`));
        }
        
        // Limiter à 9 voix maximum
        const selectedVoices = frenchVoices.slice(0, 9);
        setAvailableVoices(selectedVoices.length > 0 ? selectedVoices : allVoices.slice(0, 9));
        
        console.log('✅ Voix sélectionnées:', selectedVoices.map(v => `${v.name} (${v.lang})`));
        console.log(`🎤 ${selectedVoices.length} voix configurées`);
      };
      
      // Chargement robuste des voix
      try {
        loadVoices();
        
        // Écouter le chargement des voix (pour certains navigateurs)
        if (synthRef.current) {
          synthRef.current.onvoiceschanged = loadVoices;
        }
      } catch (error) {
        console.error('🔥 Erreur chargement voix:', error);
        // Fallback: utiliser voix par défaut
        setAvailableVoices([]);
      }
    }
  }, []);
  
  // Configuration reconnaissance vocale
  useEffect(() => {
    // Vérification robuste du support de la reconnaissance vocale
    const hasSpeechRecognition = () => {
      try {
        return !!(window.SpeechRecognition || window.webkitSpeechRecognition);
      } catch (error) {
        console.warn('⚠️ Erreur vérification SpeechRecognition:', error);
        return false;
      }
    };
    
    if (hasSpeechRecognition()) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      // Configuration optimisée pour éviter erreurs réseau
      recognitionRef.current.continuous = false; // Changé en false pour éviter network errors
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'fr-FR';
      recognitionRef.current.maxAlternatives = 1;
      
      recognitionRef.current.onstart = () => {
        console.log('✅ Reconnaissance vocale démarrée avec succès');
        setIsListening(true);
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
            setTimeout(() => handleSendMessage(transcript), 500);
          } else {
            // En mode hybrid/text, afficher et permettre édition
            setInputMessage(transcript);
            recognitionRef.current.stop();
            setIsListening(false);
            
            // En mode hybrid, envoyer automatiquement après un délai
            if (interactionMode === 'hybrid') {
              setTimeout(() => handleSendMessage(transcript), 500);
            }
          }
        }
      };
      
      recognitionRef.current.onend = () => {
        console.log('🎯 Reconnaissance vocale terminée');
        setIsListening(false);
        
        // En mode vocal pur, redémarrer automatiquement
        if (interactionMode === 'voice-only' && !isLoading) {
          setTimeout(() => {
            console.log('🔄 Redémarrage auto reconnaissance (mode vocal)');
            try {
              if (recognitionRef.current && !isListening) {
                recognitionRef.current.start();
              }
            } catch (error) {
              console.warn('⚠️ Impossible de redémarrer reconnaissance:', error);
            }
          }, 3000); // Augmenté à 3s pour éviter conflicts
        }
      };
      
      recognitionRef.current.onerror = (event) => {
        console.error('🔥 Erreur reconnaissance vocale:', event.error);
        setIsListening(false);
        
        // Gestion des erreurs spécifiques
        if (event.error === 'not-allowed') {
          alert('❌ Accès au microphone refusé. Autorisez l’accès dans les paramètres du navigateur.');
        } else if (event.error === 'no-speech') {
          console.log('🔇 Aucune parole détectée, redémarrage possible');
        } else if (event.error === 'network') {
          console.error('🌐 Erreur réseau reconnaissance vocale - Tentative en mode non-continu');
          // Forcer mode non-continu pour éviter erreurs réseau
          if (recognitionRef.current) {
            recognitionRef.current.continuous = false;
          }
        } else if (event.error === 'service-not-allowed') {
          console.error('🚫 Service de reconnaissance vocale bloqué');
        } else if (event.error === 'bad-grammar') {
          console.error('📝 Grammaire de reconnaissance invalide');
        }
      };
    }
    
    return () => {
      // Nettoyage sécurisé
      try {
        if (recognitionRef.current) {
          recognitionRef.current.abort();
          recognitionRef.current.onstart = null;
          recognitionRef.current.onend = null;
          recognitionRef.current.onresult = null;
          recognitionRef.current.onerror = null;
        }
      } catch (error) {
        console.warn('⚠️ Erreur nettoyage reconnaissance:', error);
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

  // Auto‑resize du champ de saisie
  useEffect(() => {
    if (inputRef.current) {
      const el = inputRef.current;
      el.style.height = 'auto';
      el.style.height = Math.min(el.scrollHeight, 150) + 'px'; // max 150px (aligné avec CSS)
    }
  }, [inputMessage]);

  // Sécuriser l'index de voix si la liste change
  useEffect(() => {
    if (selectedVoiceIndex >= availableVoices.length) {
      setSelectedVoiceIndex(0);
    }
  }, [availableVoices]);
  
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
          console.log('🎯 Voix utilisée:', selectedVoice.name, selectedVoice.lang);
        } else {
          // Fallback: première voix disponible
          selectedVoice = availableVoices[0] || voices[0];
          console.log('⚠️ Fallback voix:', selectedVoice?.name, selectedVoice?.lang);
        }
        
        const utterance = new SpeechSynthesisUtterance(text.substring(0, 300));
        
        // Configuration dynamique selon la voix sélectionnée
        if (selectedVoice) {
          utterance.lang = selectedVoice.lang; // Utiliser la langue de la voix
        } else {
          utterance.lang = 'fr-FR'; // Fallback français
        }
        
        // Paramètres optimisés selon le type de voix
        if (utterance.lang.startsWith('fr')) {
          utterance.rate = 0.9;
          utterance.pitch = 1.0;
        } else if (utterance.lang.startsWith('en-GB')) {
          utterance.rate = 0.8; // Plus lent pour accent britannique
          utterance.pitch = 0.9;
        } else {
          utterance.rate = 0.85; // Défaut
          utterance.pitch = 1.0;
        }
        
        utterance.volume = 0.9;
        
        if (selectedVoice) {
          utterance.voice = selectedVoice;
          console.log('🎯 Synthèse avec voix:', selectedVoice.name, selectedVoice.lang);
        } else {
          console.warn('⚠️ Aucune voix sélectionnée, utilisation voix par défaut');
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
      if (isWsConnected && wsRef.current?.readyState === WebSocket.OPEN) {
        // Envoi via WebSocket
        wsRef.current.send(JSON.stringify({
          message: sanitizedMessage,
          user_id: 'enzo',
          timestamp: new Date().toISOString()
        }));
      } else {
        // Fallback REST
        const controller = new AbortController();
        const id = setTimeout(() => controller.abort(), 15000);
        const response = await fetch(`${API_BASE_URL}/chat`, {
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
  };

  // Saisie: Entrée pour envoyer, Shift+Entrée pour nouvelle ligne
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    handleSendMessage();
  };

  const getStatusText = () => {
    if (isWsConnected) return 'En ligne (WS)';
    if (isConnected) return 'En ligne (REST)';
    return 'Hors ligne';
  };
  
  const toggleVoiceRecognition = () => {
    if (!recognitionRef.current) {
      console.error('❌ Reconnaissance vocale non supportée');
      alert('❌ Reconnaissance vocale non supportée par ce navigateur');
      return;
    }
    
    try {
      if (isListening) {
        console.log('🛑 Arrêt reconnaissance vocale');
        recognitionRef.current.abort(); // Utiliser abort() au lieu de stop() pour arrêt immédiat
        setIsListening(false);
      } else {
        console.log('🎤 Démarrage reconnaissance vocale');
        // Vérifier si une reconnaissance n'est pas déjà en cours
        if (recognitionRef.current && !isListening) {
          recognitionRef.current.start();
          // setIsListening sera mis à true dans onstart
        } else {
          console.warn('⚠️ Reconnaissance déjà en cours ou ref invalide');
        }
      }
    } catch (error) {
      console.error('🔥 Erreur toggle reconnaissance:', error);
      setIsListening(false);
      
      // Tentative de récupération
      if (error.name === 'InvalidStateError') {
        console.log('🔄 Tentative de récupération InvalidStateError');
        setTimeout(() => {
          try {
            recognitionRef.current?.start();
          } catch (retryError) {
            console.error('🚫 Échec récupération:', retryError);
          }
        }, 1000);
      }
    }
  };
  
  const stopSpeaking = () => {
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
  };
  
  const toggleAutoSpeak = () => {
    const newAutoSpeak = !autoSpeak;
    setAutoSpeak(newAutoSpeak);
    console.log('🔊 Lecture automatique:', newAutoSpeak ? 'ACTIVÉE' : 'DÉSACTIVÉE');
    
    // Feedback visuel/vocal
    if (newAutoSpeak) {
      speakMessage('Lecture automatique activée');
    }
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
    if (availableVoices.length === 0) {
      console.warn('⚠️ Aucune voix disponible pour changement');
      return;
    }
    
    let newIndex;
    if (direction === 'next') {
      newIndex = (selectedVoiceIndex + 1) % availableVoices.length;
    } else {
      newIndex = selectedVoiceIndex === 0 ? availableVoices.length - 1 : selectedVoiceIndex - 1;
    }
    
    setSelectedVoiceIndex(newIndex);
    const selectedVoice = availableVoices[newIndex];
    console.log('🔄 Voix changée:', selectedVoice?.name, selectedVoice?.lang);
    console.log(`📊 Voix ${newIndex + 1}/${availableVoices.length}`);
    
    // Test de la nouvelle voix avec un message court
    if (selectedVoice) {
      setTimeout(() => {
        speakMessage(`Voix ${newIndex + 1}: ${selectedVoice.name}`);
      }, 100);
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
          {availableVoices.length > 0 && (
            <div className="voice-selector">
              <motion.button
                className="voice-btn"
                onClick={() => changeVoice('prev')}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                title="Voix précédente"
                disabled={availableVoices.length <= 1}
              >
                ◀️
              </motion.button>
              <span className="voice-info" title={availableVoices[selectedVoiceIndex]?.name || 'Aucune voix'}>
                {availableVoices.length > 0 ? `${selectedVoiceIndex + 1}/${availableVoices.length}` : '0/0'}
                <br/>
                <small>{availableVoices[selectedVoiceIndex]?.name?.substring(0, 10) || 'Aucune'}</small>
              </span>
              <motion.button
                className="voice-btn"
                onClick={() => changeVoice('next')}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                title="Voix suivante"
                disabled={availableVoices.length <= 1}
              >
                ▶️
              </motion.button>
            </div>
          )}
          
          <div className="status-indicators">
            <div className={`status-dot ${ (isWsConnected || isConnected) ? 'connected' : 'disconnected'}`}></div>
            <span className="status-text">{getStatusText()}</span>
            
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

      {/* Bandeau connexion / fallback */}
      {(!isWsConnected || !isConnected) && (
        <div className={`connection-banner ${isWsConnected ? 'rest-only' : 'offline'}`}>
          <span>
            {isWsConnected && !isConnected ? 'Backend REST indisponible — WebSocket actif' :
             !isWsConnected && isConnected ? 'WebSocket indisponible — Bascule REST' :
             'Hors ligne — vérifiez le backend'}
          </span>
          <div className="banner-actions">
            <button onClick={testConnection} className="banner-btn" aria-label="Réessayer">Réessayer</button>
            {!isWsConnected && (
              <button onClick={connectWebSocket} className="banner-btn" aria-label="Reconnecter WebSocket">Reconnecter WS</button>
            )}
          </div>
        </div>
      )}
      
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
          {/* Interface normale (hybride et texte) */}
          {interactionMode !== 'voice-only' && (
            <div className="input-container">
              <textarea
                ref={inputRef}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={
                  !isConnected ? "Connexion au système..." :
                  interactionMode === 'text-only' ? "Tapez votre message..." :
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
                  type="button"
                  onClick={toggleVoiceRecognition}
                  className={`control-btn mic-btn ${isListening ? 'listening' : ''}`}
                  disabled={!isConnected || interactionMode === 'text-only'}
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  title={
                    interactionMode === 'text-only' ? 'Non disponible en mode texte' :
                    'Reconnaissance vocale'
                  }
                  aria-pressed={isListening}
                  aria-label="Basculer le micro"
                >
                  {isListening ? '⏹️' : '🎤'}
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
          )}
          
          {/* Interface mode vocal uniquement */}
          {interactionMode === 'voice-only' && (
            <div className="voice-only-interface">
              <div className="voice-only-controls">
                {isSpeaking && (
                  <motion.button
                    type="button"
                    onClick={stopSpeaking}
                    className="control-btn stop-btn voice-only-btn"
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
                  className="control-btn speak-btn voice-only-btn"
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
                  className={`control-btn auto-speak-btn voice-only-btn ${autoSpeak ? 'active' : ''}`}
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
                  className={`control-btn mic-btn voice-only-mic ${isListening ? 'listening' : ''}`}
                  disabled={!isConnected}
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  title="Cliquer pour parler (mode vocal)"
                >
                  {isListening ? '⏹️' : '🎤'}
                </motion.button>
              </div>
            </div>
          )}
          
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
                Voix {selectedVoiceIndex + 1}/{availableVoices.length}: {availableVoices[selectedVoiceIndex]?.name || 'Défaut'}
              </small>
            </motion.div>
          )}
        </form>
      </motion.footer>
    </div>
  );
};

export default CyberpunkJarvisInterface;
