import { useState, useRef, useCallback, useEffect } from 'react';

/**
 * Hook personnalisé pour la synthèse vocale
 * Optimisé pour les performances et la gestion des voix
 */
export const useSpeechSynthesis = () => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [availableVoices, setAvailableVoices] = useState([]);
  const [selectedVoiceIndex, setSelectedVoiceIndex] = useState(0);
  const synthRef = useRef(null);
  const isComponentMountedRef = useRef(true);

  // Fonction de chargement des voix optimisée
  const loadVoices = useCallback(() => {
    if (!isComponentMountedRef.current) return;
    
    try {
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
      
      // Limiter à 9 voix maximum pour éviter surcharge mémoire
      const selectedVoices = frenchVoices.slice(0, 9);
      
      if (isComponentMountedRef.current) {
        setAvailableVoices(selectedVoices.length > 0 ? selectedVoices : allVoices.slice(0, 9));
      }
      
      console.log('✅ Voix sélectionnées:', selectedVoices.map(v => `${v.name} (${v.lang})`));
      console.log(`🎤 ${selectedVoices.length} voix configurées`);
    } catch (error) {
      console.error('Erreur lors du chargement des voix:', error);
    }
  }, []);

  // Fonction de synthèse vocale optimisée
  const speak = useCallback(async (text, options = {}) => {
    if (!text || isSpeaking) return false;
    
    if (!synthRef.current || !('speechSynthesis' in window)) {
      console.warn('⚠️ Synthèse vocale non supportée');
      return false;
    }

    setIsSpeaking(true);
    
    try {
      // Arrêter toute synthèse en cours
      synthRef.current.cancel();
      
      // Attendre que les voix soient chargées
      const waitForVoices = () => {
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
      
      const voices = await waitForVoices();
      
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
      
      // Limiter la longueur du texte
      const textToSpeak = text.substring(0, options.maxLength || 300);
      const utterance = new SpeechSynthesisUtterance(textToSpeak);
      
      // Configuration dynamique selon la voix sélectionnée
      if (selectedVoice) {
        utterance.lang = selectedVoice.lang;
        utterance.voice = selectedVoice;
      } else {
        utterance.lang = options.lang || 'fr-FR';
      }
      
      // Paramètres optimisés selon le type de voix
      if (utterance.lang.startsWith('fr')) {
        utterance.rate = options.rate || 0.9;
        utterance.pitch = options.pitch || 1.0;
      } else if (utterance.lang.startsWith('en-GB')) {
        utterance.rate = options.rate || 0.8; // Plus lent pour accent britannique
        utterance.pitch = options.pitch || 0.9;
      } else {
        utterance.rate = options.rate || 0.85; // Défaut
        utterance.pitch = options.pitch || 1.0;
      }
      
      utterance.volume = options.volume || 0.9;
      
      // Promesse pour gérer les événements
      return new Promise((resolve, reject) => {
        utterance.onstart = () => {
          console.log('🔊 Synthèse vocale démarrée');
        };
        
        utterance.onend = () => {
          console.log('🔊 Synthèse vocale terminée');
          setIsSpeaking(false);
          resolve(true);
        };
        
        utterance.onerror = (error) => {
          console.error('🔥 Erreur synthèse vocale:', error);
          setIsSpeaking(false);
          reject(error);
        };
        
        synthRef.current.speak(utterance);
        
        // Timeout de sécurité
        setTimeout(() => {
          if (isSpeaking) {
            synthRef.current?.cancel();
            setIsSpeaking(false);
            reject(new Error('Timeout synthèse vocale'));
          }
        }, options.timeout || 30000);
      });
      
    } catch (error) {
      console.error('🔥 Erreur TTS:', error);
      setIsSpeaking(false);
      return false;
    }
  }, [isSpeaking, availableVoices, selectedVoiceIndex]);

  // Fonction d'arrêt
  const stop = useCallback(() => {
    try {
      if (synthRef.current) {
        console.log('🛑 Arrêt synthèse vocale');
        synthRef.current.cancel();
      }
      setIsSpeaking(false);
      return true;
    } catch (error) {
      console.error('🔥 Erreur arrêt synthèse:', error);
      setIsSpeaking(false);
      return false;
    }
  }, []);

  // Fonction de changement de voix
  const changeVoice = useCallback((direction) => {
    if (availableVoices.length === 0) {
      console.warn('⚠️ Aucune voix disponible pour changement');
      return null;
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
    
    return selectedVoice;
  }, [availableVoices, selectedVoiceIndex]);

  // Test de la voix courante
  const testCurrentVoice = useCallback(() => {
    if (availableVoices.length > 0 && selectedVoiceIndex < availableVoices.length) {
      const selectedVoice = availableVoices[selectedVoiceIndex];
      speak(`Voix ${selectedVoiceIndex + 1}: ${selectedVoice.name}`);
    }
  }, [availableVoices, selectedVoiceIndex, speak]);

  // Sécuriser l'index de voix si la liste change
  useEffect(() => {
    if (selectedVoiceIndex >= availableVoices.length && availableVoices.length > 0) {
      setSelectedVoiceIndex(0);
    }
  }, [availableVoices, selectedVoiceIndex]);

  // Initialisation des voix
  useEffect(() => {
    let voiceLoadTimeout = null;
    
    if ('speechSynthesis' in window) {
      synthRef.current = window.speechSynthesis;
      
      try {
        loadVoices();
        
        // Écouter le chargement des voix (pour certains navigateurs)
        if (synthRef.current) {
          synthRef.current.onvoiceschanged = loadVoices;
        }
        
        // Timeout de sécurité pour éviter attente infinie
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
    
    // Cleanup pour éviter memory leaks
    return () => {
      isComponentMountedRef.current = false;
      if (voiceLoadTimeout) {
        clearTimeout(voiceLoadTimeout);
      }
      if (synthRef.current && synthRef.current.onvoiceschanged) {
        synthRef.current.onvoiceschanged = null;
      }
      // Arrêter toute synthèse en cours
      try {
        synthRef.current?.cancel();
      } catch (error) {
        console.warn('⚠️ Erreur cleanup synthèse:', error);
      }
    };
  }, [loadVoices]);

  return {
    isSpeaking,
    availableVoices,
    selectedVoiceIndex,
    speak,
    stop,
    changeVoice,
    testCurrentVoice,
    isSupported: 'speechSynthesis' in window,
    currentVoice: availableVoices[selectedVoiceIndex] || null
  };
};