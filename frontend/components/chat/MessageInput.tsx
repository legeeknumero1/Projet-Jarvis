/**
 * Composant pour envoyer des messages
 */

'use client';

import React, { useState } from 'react';
import { Send, Loader } from 'lucide-react';

interface MessageInputProps {
  onSubmit: (message: string) => Promise<void>;
  disabled?: boolean;
  placeholder?: string;
}

export function MessageInput({
  onSubmit,
  disabled = false,
  placeholder = 'Écrivez votre message...',
}: MessageInputProps) {
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  /**
   * Gérer l'envoi du message
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!message.trim() || isLoading || disabled) {
      return;
    }

    const messageContent = message.trim();
    setMessage('');
    setIsLoading(true);

    try {
      await onSubmit(messageContent);
    } catch (error) {
      console.error('Erreur lors de l\'envoi du message:', error);
      setMessage(messageContent);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Gérer l'envoi au Ctrl+Entrée
   */
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      handleSubmit(e as any);
    }
  };

  /**
   * Auto-redimensionner le textarea
   */
  const handleTextAreaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 200) + 'px';
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="border-t border-border bg-card p-4 sm:p-6"
    >
      <div className="flex gap-4">
        {/* Textarea */}
        <div className="flex-1 flex flex-col">
          <textarea
            value={message}
            onChange={handleTextAreaChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled || isLoading}
            className="min-h-12 max-h-48 w-full resize-none rounded-lg border border-input bg-background px-4 py-3 text-sm placeholder-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary disabled:opacity-50"
            rows={1}
          />
          <p className="mt-2 text-xs text-muted-foreground">
            Ctrl + Entrée pour envoyer
          </p>
        </div>

        {/* Bouton d'envoi */}
        <button
          type="submit"
          disabled={!message.trim() || isLoading || disabled}
          className="mt-auto flex h-12 w-12 items-center justify-center rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          aria-label="Envoyer"
        >
          {isLoading ? (
            <Loader className="h-5 w-5 animate-spin" />
          ) : (
            <Send className="h-5 w-5" />
          )}
        </button>
      </div>
    </form>
  );
}
