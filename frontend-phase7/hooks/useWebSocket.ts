/**
 * Hook personnalisé pour gérer les WebSockets
 */

'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import { WebSocketMessage } from '@/types';

export interface UseWebSocketState {
  isConnected: boolean;
  lastMessage: WebSocketMessage | null;
  error: string | null;
}

export interface UseWebSocketActions {
  send: (message: WebSocketMessage) => void;
  disconnect: () => void;
  reconnect: () => void;
}

/**
 * Hook pour gérer les WebSockets
 * @param url - L'URL WebSocket du serveur
 * @param onMessage - Callback optionnel appelé à chaque message reçu
 */
export function useWebSocket(
  url: string,
  onMessage?: (message: WebSocketMessage) => void,
): UseWebSocketState & UseWebSocketActions {
  const [state, setState] = useState<UseWebSocketState>({
    isConnected: false,
    lastMessage: null,
    error: null,
  });

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;
  const reconnectDelay = 3000;

  /**
   * Se connecter au WebSocket
   */
  const connect = useCallback(() => {
    try {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        return;
      }

      const wsUrl = url.startsWith('ws://') || url.startsWith('wss://') ? url : `ws://${url}`;
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        setState((prev) => ({
          ...prev,
          isConnected: true,
          error: null,
        }));
        reconnectAttemptsRef.current = 0;
      };

      wsRef.current.onmessage = (event: MessageEvent) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setState((prev) => ({
            ...prev,
            lastMessage: message,
          }));

          if (onMessage) {
            onMessage(message);
          }
        } catch (error) {
          console.error('Erreur parsing WebSocket message:', error);
        }
      };

      wsRef.current.onerror = (event: Event) => {
        setState((prev) => ({
          ...prev,
          error: 'Erreur WebSocket',
        }));
      };

      wsRef.current.onclose = () => {
        setState((prev) => ({
          ...prev,
          isConnected: false,
        }));

        // Tentative de reconnexion
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current += 1;
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectDelay * Math.pow(2, reconnectAttemptsRef.current - 1));
        } else {
          setState((prev) => ({
            ...prev,
            error: 'Impossible de se reconnecter après plusieurs tentatives',
          }));
        }
      };
    } catch (error) {
      setState((prev) => ({
        ...prev,
        error: `Erreur de connexion: ${error instanceof Error ? error.message : 'Erreur inconnue'}`,
      }));
    }
  }, [url, onMessage]);

  /**
   * Envoyer un message via WebSocket
   */
  const send = useCallback((message: WebSocketMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      setState((prev) => ({
        ...prev,
        error: 'WebSocket non connecté',
      }));
    }
  }, []);

  /**
   * Déconnecter le WebSocket
   */
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setState({
      isConnected: false,
      lastMessage: null,
      error: null,
    });
  }, []);

  /**
   * Se reconnecter
   */
  const reconnect = useCallback(() => {
    reconnectAttemptsRef.current = 0;
    disconnect();
    setTimeout(() => connect(), 100);
  }, [connect, disconnect]);

  // Connexion/déconnexion automatique
  useEffect(() => {
    if (typeof window !== 'undefined') {
      connect();
    }

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    ...state,
    send,
    disconnect,
    reconnect,
  };
}
