/**
 * Layout principal du chat
 */

'use client';

import React, { useEffect, useState } from 'react';
import { useChat } from '@/hooks';
import { useChatStore } from '@/store';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';

export function ChatLayout() {
  const { messages, isLoading, error, sendMessage, createConversation, currentConversationId } = useChat();
  const { currentConversation, setCurrentConversation } = useChatStore();
  const [isInitializing, setIsInitializing] = useState(true);

  /**
   * Initialiser une conversation si nécessaire
   */
  useEffect(() => {
    const initializeChat = async () => {
      if (!currentConversation && !currentConversationId) {
        try {
          await createConversation('Nouvelle conversation');
        } catch (error) {
          console.error('Erreur lors de l\'initialisation:', error);
        }
      }
      setIsInitializing(false);
    };

    initializeChat();
  }, [currentConversation, currentConversationId, createConversation]);

  /**
   * Gérer l'envoi du message
   */
  const handleSendMessage = async (content: string) => {
    await sendMessage(content);
  };

  if (isInitializing) {
    return (
      <div className="flex flex-1 items-center justify-center bg-background">
        <div className="animate-spin rounded-full border-4 border-primary border-t-transparent h-12 w-12" />
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      {/* En-tête de la conversation */}
      {currentConversation && (
        <div className="border-b border-border bg-card px-4 py-3 sm:px-6">
          <h1 className="text-lg font-semibold">{currentConversation.title}</h1>
          {currentConversation.summary && (
            <p className="text-sm text-muted-foreground">{currentConversation.summary}</p>
          )}
        </div>
      )}

      {/* Messages */}
      <MessageList messages={messages} isLoading={isLoading} />

      {/* Erreur */}
      {error && (
        <div className="border-t border-border bg-destructive/10 px-4 py-3 text-sm text-destructive">
          {error}
        </div>
      )}

      {/* Input */}
      <MessageInput onSubmit={handleSendMessage} disabled={isLoading} />
    </div>
  );
}
