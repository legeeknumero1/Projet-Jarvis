import { useState, useRef, useCallback, useEffect } from 'react';

/**
 * Hook personnalisé pour la reconnaissance vocale
 * Optimisé pour les performances et la gestion des erreurs
 */
export const useVoiceRecognition = ({
  isConnected = false,
  interactionMode = 'hybrid',
  onTranscriptionComplete,
  onError
}) => {
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);
  const isComponentMountedRef = useRef(true);
  const recognitionCleanupTimerRef = useRef(null);

  // Configuration de la reconnaissance vocale
  const initializeRecognition = useCallback(() => {
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
      recognitionRef.current.continuous = false;
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
        
        if (transcript.trim()) {
          console.log('🗣️ Transcription finale:', transcript);
          recognitionRef.current.stop();
          setIsListening(false);
          
          if (onTranscriptionComplete) {
            onTranscriptionComplete(transcript, interimTranscript);
          }
        }
      };
      
      recognitionRef.current.onend = () => {
        if (isComponentMountedRef.current) {
          console.log('🎯 Reconnaissance vocale terminée');
          setIsListening(false);
          
          if (recognitionCleanupTimerRef.current) {
            clearTimeout(recognitionCleanupTimerRef.current);
            recognitionCleanupTimerRef.current = null;
          }
          
          // En mode vocal pur, redémarrer automatiquement avec protection memory leak
          if (interactionMode === 'voice-only' && isComponentMountedRef.current) {
            setTimeout(() => {
              if (isComponentMountedRef.current) {
                console.log('🔄 Redémarrage auto reconnaissance (mode vocal)');
                try {
                  if (recognitionRef.current && !isListening) {
                    recognitionRef.current.start();
                  }
                } catch (error) {
                  console.warn('⚠️ Impossible de redémarrer reconnaissance:', error);
                }
              }
            }, 3000);
          }
        }
      };
      
      recognitionRef.current.onerror = (event) => {
        if (isComponentMountedRef.current) {
          console.error('🔥 Erreur reconnaissance vocale:', event.error);
          setIsListening(false);
          
          if (recognitionCleanupTimerRef.current) {
            clearTimeout(recognitionCleanupTimerRef.current);
            recognitionCleanupTimerRef.current = null;
          }
          
          // Gestion des erreurs spécifiques
          let errorMessage = 'Erreur de reconnaissance vocale';
          
          switch(event.error) {
            case 'not-allowed':
              errorMessage = '❌ Accès au microphone refusé. Autorisez l\'accès dans les paramètres du navigateur.';
              alert(errorMessage);
              break;
            case 'no-speech':
              console.log('🔇 Aucune parole détectée, redémarrage possible');
              break;
            case 'network':
              console.error('🌐 Erreur réseau reconnaissance vocale - Tentative en mode non-continu');
              if (recognitionRef.current) {
                recognitionRef.current.continuous = false;
              }
              break;
            case 'service-not-allowed':
              console.error('🚫 Service de reconnaissance vocale bloqué');
              break;
            case 'bad-grammar':
              console.error('📝 Grammaire de reconnaissance invalide');
              break;
            default:
              console.error('🔥 Erreur inconnue:', event.error);
          }
          
          if (onError) {
            onError(event.error, errorMessage);
          }
        }
      };
    }
  }, [interactionMode, onTranscriptionComplete, onError, isListening]);

  // Toggle de la reconnaissance vocale
  const toggleVoiceRecognition = useCallback(() => {
    if (!recognitionRef.current) {
      console.error('❌ Reconnaissance vocale non supportée');
      if (onError) {
        onError('not-supported', '❌ Reconnaissance vocale non supportée par ce navigateur');
      }
      return;
    }
    
    try {
      if (isListening) {
        console.log('🛑 Arrêt reconnaissance vocale');
        recognitionRef.current.abort();
        setIsListening(false);
      } else {
        console.log('🎤 Démarrage reconnaissance vocale');
        if (recognitionRef.current && !isListening) {
          recognitionRef.current.start();
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
            if (onError) {
              onError('recovery-failed', 'Impossible de redémarrer la reconnaissance vocale');
            }
          }
        }, 1000);
      }
    }
  }, [isListening, onError]);

  // Initialization effect
  useEffect(() => {
    initializeRecognition();
    
    return () => {
      isComponentMountedRef.current = false;
      
      if (recognitionCleanupTimerRef.current) {
        clearTimeout(recognitionCleanupTimerRef.current);
      }
      
      // Nettoyage sécurisé
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
          recognitionRef.current.onstart = null;
          recognitionRef.current.onresult = null;
          recognitionRef.current.onend = null;
          recognitionRef.current.onerror = null;
        } catch (error) {
          console.warn('⚠️ Erreur nettoyage reconnaissance:', error);
        }
      }
    };
  }, [initializeRecognition]);

  return {
    isListening,
    toggleVoiceRecognition,
    isSupported: !!(window.SpeechRecognition || window.webkitSpeechRecognition)
  };
};