import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Bot, User, Copy, Check } from 'lucide-react';
import { Button } from './ui/button';
import { useToast } from '../hooks/use-toast';

const MessageBubble = ({ message }) => {
  const { toast } = useToast();
  const [copied, setCopied] = useState(false);
  
  const isUser = message.role === 'user';
  const timestamp = new Date(message.timestamp).toLocaleTimeString('fr-FR', {
    hour: '2-digit',
    minute: '2-digit'
  });

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      toast({
        title: "Copié !",
        description: "Le message a été copié dans le presse-papiers.",
      });
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      toast({
        title: "Erreur",
        description: "Impossible de copier le message.",
        variant: "destructive",
      });
    }
  };

  // Parse content for code blocks
  const parseContent = (content) => {
    const parts = content.split(/(```[\s\S]*?```|`[^`]+`)/);
    
    return parts.map((part, index) => {
      if (part.startsWith('```') && part.endsWith('```')) {
        // Multi-line code block
        const code = part.slice(3, -3);
        const lines = code.split('\n');
        const language = lines[0].trim();
        const codeContent = lines.slice(1).join('\n');
        
        return (
          <div key={index} className="my-4 relative group">
            <div className="bg-jarvis-bg border border-jarvis-border rounded-lg overflow-hidden">
              {language && (
                <div className="px-4 py-2 bg-jarvis-surface/50 border-b border-jarvis-border text-xs text-jarvis-text-muted font-mono">
                  {language}
                </div>
              )}
              <div className="relative">
                <pre className="p-4 overflow-x-auto text-sm font-mono text-jarvis-text">
                  <code>{codeContent}</code>
                </pre>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => navigator.clipboard.writeText(codeContent)}
                  className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity h-8 w-8 p-0 text-jarvis-text-muted hover:text-jarvis-primary"
                >
                  <Copy className="h-3 w-3" />
                </Button>
              </div>
            </div>
          </div>
        );
      } else if (part.startsWith('`') && part.endsWith('`')) {
        // Inline code
        const code = part.slice(1, -1);
        return (
          <code 
            key={index} 
            className="bg-jarvis-surface/50 text-jarvis-primary px-1.5 py-0.5 rounded text-sm font-mono border border-jarvis-border/50"
          >
            {code}
          </code>
        );
      } else {
        // Regular text with markdown-style formatting
        return (
          <span key={index}>
            {part.split(/(\*\*[^*]+\*\*|\*[^*]+\*)/).map((subPart, subIndex) => {
              if (subPart.startsWith('**') && subPart.endsWith('**')) {
                return <strong key={subIndex} className="text-jarvis-text font-semibold">{subPart.slice(2, -2)}</strong>;
              } else if (subPart.startsWith('*') && subPart.endsWith('*')) {
                return <em key={subIndex} className="text-jarvis-info italic">{subPart.slice(1, -1)}</em>;
              }
              return subPart;
            })}
          </span>
        );
      }
    });
  };

  return (
    <motion.div
      layout
      className={`flex gap-4 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      {/* Avatar */}
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
        isUser 
          ? 'bg-jarvis-accent/20 text-jarvis-accent' 
          : 'bg-jarvis-primary/20 text-jarvis-primary'
      }`}>
        {isUser ? (
          <User className="w-4 h-4" />
        ) : (
          <Bot className="w-4 h-4" />
        )}
      </div>

      {/* Message Content */}
      <div className={`flex-1 max-w-[80%] ${isUser ? 'items-end' : 'items-start'} flex flex-col`}>
        {/* Message Bubble */}
        <motion.div
          className={`group relative p-4 rounded-2xl ${
            isUser 
              ? 'bg-jarvis-accent/10 border border-jarvis-accent/30 text-jarvis-text ml-8' 
              : 'bg-jarvis-surface border border-jarvis-border text-jarvis-text mr-8 glass-surface'
          } ${message.streaming ? 'animate-pulse-slow' : ''}`}
          whileHover={{ scale: 1.01 }}
          transition={{ duration: 0.2 }}
        >
          {/* Content */}
          <div className="space-y-2">
            {message.streaming && message.content === '' ? (
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-jarvis-primary rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-jarvis-primary rounded-full animate-bounce delay-100" />
                <div className="w-2 h-2 bg-jarvis-primary rounded-full animate-bounce delay-200" />
              </div>
            ) : (
              <div className="prose prose-invert max-w-none">
                {parseContent(message.content)}
              </div>
            )}
          </div>

          {/* Copy button */}
          {!isUser && message.content && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleCopy}
              className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity h-6 w-6 p-0 text-jarvis-text-muted hover:text-jarvis-primary"
            >
              {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
            </Button>
          )}

          {/* Error indicator */}
          {message.error && (
            <div className="mt-2 text-xs text-red-400 flex items-center gap-1">
              <span className="w-1 h-1 bg-red-400 rounded-full" />
              Erreur lors de la génération
            </div>
          )}
        </motion.div>

        {/* Metadata */}
        <div className={`mt-1 flex items-center gap-2 text-xs text-jarvis-text-muted ${
          isUser ? 'flex-row-reverse' : 'flex-row'
        }`}>
          <span>{timestamp}</span>
          {message.model && (
            <>
              <span>•</span>
              <span className="text-jarvis-info">{message.model}</span>
            </>
          )}
          {message.streaming && (
            <>
              <span>•</span>
              <span className="text-jarvis-success animate-pulse">Streaming...</span>
            </>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default MessageBubble;