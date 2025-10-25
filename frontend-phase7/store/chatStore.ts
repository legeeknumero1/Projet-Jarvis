/**
 * Store Zustand pour la gestion globale des conversations et messages
 */

'use client';

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { Conversation, Message } from '@/types';

export interface ChatState {
  // État
  conversations: Conversation[];
  currentConversation: Conversation | null;
  messages: Message[];
  isLoading: boolean;
  error: string | null;

  // Actions
  setConversations: (conversations: Conversation[]) => void;
  setCurrentConversation: (conversation: Conversation | null) => void;
  addConversation: (conversation: Conversation) => void;
  updateConversation: (conversationId: string, updates: Partial<Conversation>) => void;
  deleteConversation: (conversationId: string) => void;
  archiveConversation: (conversationId: string) => void;

  // Messages
  setMessages: (messages: Message[]) => void;
  addMessage: (message: Message) => void;
  updateMessage: (messageId: string, updates: Partial<Message>) => void;
  clearMessages: () => void;

  // Utils
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  resetStore: () => void;
}

const initialState = {
  conversations: [],
  currentConversation: null,
  messages: [],
  isLoading: false,
  error: null,
};

export const useChatStore = create<ChatState>()(
  devtools(
    persist(
      (set) => ({
        ...initialState,

        setConversations: (conversations) => set({ conversations }),

        setCurrentConversation: (conversation) =>
          set({
            currentConversation: conversation,
            messages: conversation ? [] : [],
          }),

        addConversation: (conversation) =>
          set((state) => ({
            conversations: [conversation, ...state.conversations],
          })),

        updateConversation: (conversationId, updates) =>
          set((state) => {
            const conversations = state.conversations.map((conv) =>
              conv.id === conversationId ? { ...conv, ...updates } : conv,
            );

            const currentConversation =
              state.currentConversation?.id === conversationId
                ? { ...state.currentConversation, ...updates }
                : state.currentConversation;

            return {
              conversations,
              currentConversation,
            };
          }),

        deleteConversation: (conversationId) =>
          set((state) => {
            const conversations = state.conversations.filter((conv) => conv.id !== conversationId);
            const currentConversation =
              state.currentConversation?.id === conversationId ? null : state.currentConversation;

            return {
              conversations,
              currentConversation,
              messages: currentConversation ? state.messages : [],
            };
          }),

        archiveConversation: (conversationId) =>
          set((state) => ({
            conversations: state.conversations.map((conv) =>
              conv.id === conversationId ? { ...conv, isArchived: true } : conv,
            ),
          })),

        setMessages: (messages) => set({ messages }),

        addMessage: (message) =>
          set((state) => ({
            messages: [...state.messages, message],
          })),

        updateMessage: (messageId, updates) =>
          set((state) => ({
            messages: state.messages.map((msg) =>
              msg.id === messageId ? { ...msg, ...updates } : msg,
            ),
          })),

        clearMessages: () => set({ messages: [] }),

        setLoading: (isLoading) => set({ isLoading }),

        setError: (error) => set({ error }),

        resetStore: () => set(initialState),
      }),
      {
        name: 'chat-store',
        version: 1,
      },
    ),
  ),
);
