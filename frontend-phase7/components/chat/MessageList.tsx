/**
 * Composant pour afficher la liste des messages
 */

'use client';

import React, { useEffect, useRef } from 'react';
import { Message } from '@/types';
import { MessageItem } from './MessageItem';

interface MessageListProps {
  messages: Message[];
  isLoading?: boolean;
  currentUserId?: string;
}

export function MessageList({ messages, isLoading = false, currentUserId }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  /**
   * Scroller automatiquement vers le dernier message
   */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div
      ref={containerRef}
      className="flex-1 overflow-y-auto overflow-x-hidden bg-background"
    >
      <div className="flex flex-col gap-4 p-4 sm:p-6 md:p-8">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <div className="mb-4 inline-flex rounded-full bg-muted p-4">
                <svg className="h-8 w-8 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold">Commencez une conversation</h3>
              <p className="mt-2 text-sm text-muted-foreground">
                Posez une question ou envoyez un message pour démarrer
              </p>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <MessageItem
                key={message.id}
                message={message}
                isCurrentUser={message.role === 'user' && currentUserId && message.id.includes(currentUserId)}
              />
            ))}

            {isLoading && (
              <div className="flex gap-4 rounded-lg bg-muted p-4">
                <div className="h-8 w-8 rounded-full bg-primary flex-shrink-0" />
                <div className="flex flex-1 items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-foreground/40 animate-bounce" />
                  <div className="h-2 w-2 rounded-full bg-foreground/40 animate-bounce animation-delay-100" />
                  <div className="h-2 w-2 rounded-full bg-foreground/40 animate-bounce animation-delay-200" />
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </>
        )}
      </div>
    </div>
  );
}
