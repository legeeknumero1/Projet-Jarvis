/**
 * Composant pour un message individuel
 */

'use client';

import React from 'react';
import { Message } from '@/types';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import { Copy, Check } from 'lucide-react';

interface MessageItemProps {
  message: Message;
  isCurrentUser?: boolean;
}

export function MessageItem({ message, isCurrentUser = false }: MessageItemProps) {
  const [isCopied, setIsCopied] = React.useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  const formattedTime = format(new Date(message.timestamp), 'HH:mm', { locale: fr });

  return (
    <div
      className={`flex gap-4 ${isCurrentUser ? 'flex-row-reverse' : ''}`}
    >
      {/* Avatar */}
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold text-white ${
        isCurrentUser ? 'bg-blue-500' : 'bg-slate-500'
      }`}>
        {isCurrentUser ? 'U' : 'J'}
      </div>

      {/* Contenu du message */}
      <div className={`flex-1 max-w-xl group`}>
        <div className={`rounded-lg px-4 py-3 ${
          isCurrentUser
            ? 'bg-blue-500 text-white'
            : 'bg-muted text-foreground'
        }`}>
          <p className="break-words text-sm leading-relaxed whitespace-pre-wrap">
            {message.content}
          </p>
        </div>

        {/* Infos et actions */}
        <div className={`mt-1 flex items-center gap-2 opacity-0 transition-opacity group-hover:opacity-100 ${
          isCurrentUser ? 'flex-row-reverse pr-2' : 'pl-2'
        }`}>
          <span className="text-xs text-muted-foreground">{formattedTime}</span>

          {message.tokens && (
            <span className="text-xs text-muted-foreground">
              {message.tokens} tokens
            </span>
          )}

          <button
            onClick={handleCopy}
            className="rounded p-1 hover:bg-muted transition-colors"
            title="Copier"
          >
            {isCopied ? (
              <Check className="h-4 w-4 text-green-500" />
            ) : (
              <Copy className="h-4 w-4 text-muted-foreground" />
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
