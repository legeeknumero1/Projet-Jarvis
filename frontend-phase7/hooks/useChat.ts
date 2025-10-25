/**
 * Hook personnalisé pour gérer le chat
 */

'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { Message, ChatRequest, AppError } from '@/types';
import { chatApi } from '@/lib/api';

export interface UseChatState {
  messages: Message[];
  currentConversationId: string | null;
  isLoading: boolean;
  error: string | null;
  isStreaming: boolean;
}

export interface UseChatActions {
  sendMessage: (content: string) => Promise<void>;
  loadHistory: (conversationId: string) => Promise<void>;
  createConversation: (title: string) => Promise<string>;
  clearError: () => void;
  resetChat: () => void;
}

export function useChat(): UseChatState & UseChatActions {
  const [state, setState] = useState<UseChatState>({
    messages: [],
    currentConversationId: null,
    isLoading: false,
    error: null,
    isStreaming: false,
  });

  const abortControllerRef = useRef<AbortController | null>(null);

  /**
   * Envoyer un message
   */
  const sendMessage = useCallback(async (content: string) => {
    if (!state.currentConversationId) {
      setState((prev) => ({ ...prev, error: 'Aucune conversation active' }));
      return;
    }

    // Créer un message utilisateur optimiste
    const userMessage: Message = {
      id: `temp_${Date.now()}`,
      conversationId: state.currentConversationId,
      role: 'user',
      content,
      timestamp: new Date(),
    };

    setState((prev) => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isLoading: true,
      error: null,
    }));

    try {
      abortControllerRef.current = new AbortController();

      // Envoyer le message à l'API
      const response = await chatApi.sendMessage(state.currentConversationId, content);

      if (!response.success) {
        throw new AppError('SEND_ERROR', response.error || 'Erreur lors de l\'envoi du message');
      }

      // Ajouter la réponse de l'assistant
      const assistantMessage = response.data.message as Message;
      setState((prev) => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
        isLoading: false,
      }));
    } catch (error) {
      const errorMessage = error instanceof AppError ? error.message : 'Erreur inconnue';
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
    }
  }, [state.currentConversationId]);

  /**
   * Charger l'historique d'une conversation
   */
  const loadHistory = useCallback(async (conversationId: string) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      const history = await chatApi.getHistory(conversationId, 50);
      const messages = (history.data || history || []) as Message[];

      setState((prev) => ({
        ...prev,
        messages: messages.map((msg) => ({
          ...msg,
          timestamp: new Date(msg.timestamp),
        })),
        currentConversationId: conversationId,
        isLoading: false,
      }));
    } catch (error) {
      const errorMessage = error instanceof AppError ? error.message : 'Erreur lors du chargement de l\'historique';
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
    }
  }, []);

  /**
   * Créer une nouvelle conversation
   */
  const createConversation = useCallback(async (title: string): Promise<string> => {
    try {
      const response = await chatApi.createConversation(title);
      const conversationId = response.data?.id || response.id;

      setState((prev) => ({
        ...prev,
        currentConversationId: conversationId,
        messages: [],
      }));

      return conversationId;
    } catch (error) {
      const errorMessage = error instanceof AppError ? error.message : 'Erreur lors de la création de la conversation';
      setState((prev) => ({ ...prev, error: errorMessage }));
      throw error;
    }
  }, []);

  /**
   * Effacer l'erreur
   */
  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  /**
   * Réinitialiser le chat
   */
  const resetChat = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setState({
      messages: [],
      currentConversationId: null,
      isLoading: false,
      error: null,
      isStreaming: false,
    });
  }, []);

  // Cleanup
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return {
    ...state,
    sendMessage,
    loadHistory,
    createConversation,
    clearError,
    resetChat,
  };
}
