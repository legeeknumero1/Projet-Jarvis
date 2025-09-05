import { useState, useRef, useCallback, useEffect } from 'react';

/**
 * Hook personnalisé pour la gestion WebSocket
 * Optimisé pour les performances et la reconnexion automatique
 */
export const useWebSocket = ({ url, onMessage, onError }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState('CONNECTING'); // CONNECTING, OPEN, CLOSING, CLOSED
  const wsRef = useRef(null);
  const isComponentMountedRef = useRef(true);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;
  const baseReconnectDelay = 1000;

  // Fonction de connexion optimisée
  const connect = useCallback(() => {
    if (!url) {
      console.error('❌ URL WebSocket manquante');
      return;
    }

    try {
      // Fermer la connexion existante si elle existe
      if (wsRef.current && wsRef.current.readyState !== WebSocket.CLOSED) {
        wsRef.current.close();
      }

      console.log('🔌 Tentative de connexion WebSocket:', url);
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        if (isComponentMountedRef.current) {
          console.log('✅ WebSocket connecté');
          setIsConnected(true);
          setConnectionState('OPEN');
          reconnectAttemptsRef.current = 0; // Reset compteur tentatives
        }
      };

      ws.onclose = (event) => {
        if (isComponentMountedRef.current) {
          console.log('🔌 WebSocket fermé:', event.code, event.reason);
          setIsConnected(false);
          setConnectionState('CLOSED');
          
          // Reconnexion automatique avec backoff exponentiel
          if (reconnectAttemptsRef.current < maxReconnectAttempts) {
            const delay = baseReconnectDelay * Math.pow(2, reconnectAttemptsRef.current);
            console.log(`🔄 Reconnexion automatique dans ${delay}ms (tentative ${reconnectAttemptsRef.current + 1}/${maxReconnectAttempts})`);
            
            reconnectTimeoutRef.current = setTimeout(() => {
              if (isComponentMountedRef.current) {
                reconnectAttemptsRef.current += 1;
                connect();
              }
            }, delay);
          } else {
            console.error('🚫 Nombre maximum de tentatives de reconnexion atteint');
            if (onError) {
              onError('max-reconnect-attempts', 'Impossible de se reconnecter au WebSocket');
            }
          }
        }
      };

      ws.onerror = (error) => {
        if (isComponentMountedRef.current) {
          console.error('🔥 Erreur WebSocket:', error);
          setIsConnected(false);
          setConnectionState('CLOSED');
          
          if (onError) {
            onError('websocket-error', 'Erreur de connexion WebSocket');
          }
        }
      };

      ws.onmessage = (event) => {
        if (isComponentMountedRef.current && onMessage) {
          try {
            const data = JSON.parse(event.data);
            onMessage(data);
          } catch (parseError) {
            console.error('❌ Erreur parsing message WebSocket:', parseError);
            console.log('Message brut reçu:', event.data);
            
            if (onError) {
              onError('parse-error', 'Erreur de parsing du message WebSocket');
            }
          }
        }
      };

    } catch (error) {
      console.error('🔥 Erreur initialisation WebSocket:', error);
      setIsConnected(false);
      setConnectionState('CLOSED');
      
      if (onError) {
        onError('init-error', 'Erreur d\'initialisation WebSocket');
      }
    }
  }, [url, onMessage, onError]);

  // Fonction d'envoi de message optimisée
  const sendMessage = useCallback((message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      try {
        const messageString = typeof message === 'string' ? message : JSON.stringify(message);
        wsRef.current.send(messageString);
        return true;
      } catch (error) {
        console.error('❌ Erreur envoi message WebSocket:', error);
        if (onError) {
          onError('send-error', 'Erreur d\'envoi du message');
        }
        return false;
      }
    } else {
      console.warn('⚠️ WebSocket non connecté, impossible d\'envoyer le message');
      return false;
    }
  }, [onError]);

  // Fonction de reconnexion manuelle
  const reconnect = useCallback(() => {
    console.log('🔄 Reconnexion manuelle demandée');
    
    // Arrêter les tentatives automatiques
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    // Reset du compteur et reconnexion
    reconnectAttemptsRef.current = 0;
    connect();
  }, [connect]);

  // Fonction de fermeture propre
  const disconnect = useCallback(() => {
    console.log('🔌 Fermeture WebSocket demandée');
    
    // Arrêter les tentatives de reconnexion
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    // Fermer la connexion
    if (wsRef.current) {
      wsRef.current.close(1000, 'Fermeture normale');
    }
    
    setIsConnected(false);
    setConnectionState('CLOSED');
  }, []);

  // Status de la connexion
  const getConnectionStatus = useCallback(() => {
    if (!wsRef.current) return 'UNINITIALIZED';
    
    switch(wsRef.current.readyState) {
      case WebSocket.CONNECTING: return 'CONNECTING';
      case WebSocket.OPEN: return 'OPEN';
      case WebSocket.CLOSING: return 'CLOSING';
      case WebSocket.CLOSED: return 'CLOSED';
      default: return 'UNKNOWN';
    }
  }, []);

  // Effect d'initialisation
  useEffect(() => {
    connect();
    
    return () => {
      isComponentMountedRef.current = false;
      
      // Cleanup des timeouts
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      
      // Fermeture propre du WebSocket
      if (wsRef.current) {
        wsRef.current.close(1000, 'Component unmounting');
      }
    };
  }, [connect]);

  return {
    isConnected,
    connectionState,
    sendMessage,
    reconnect,
    disconnect,
    getConnectionStatus,
    reconnectAttempts: reconnectAttemptsRef.current,
    maxReconnectAttempts
  };
};