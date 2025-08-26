import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Bot, User, Copy, Check, Sparkles } from 'lucide-react';
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
            <div className="message-bubble-code overflow-hidden rounded-xl border border-jarvis-neon-purple/40">
              {language && (
                <div className="px-4 py-2 bg-jarvis-neon-purple/20 border-b border-jarvis-neon-purple/30 text-xs text-jarvis-neon-purple font-mono font-semibold">
                  <div className="flex items-center gap-2">
                    <Sparkles className="h-3 w-3" />
                    {language}
                  </div>
                </div>
              )}
              <div className="relative">
                <pre className="p-4 overflow-x-auto text-sm font-mono text-jarvis-text-primary bg-gradient-to-br from-jarvis-neon-purple/10 to-transparent">
                  <code>{codeContent}</code>
                </pre>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => navigator.clipboard.writeText(codeContent)}
                  className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-all duration-200 h-8 w-8 p-0 text-jarvis-neon-purple hover:text-jarvis-neon-cyan hover:bg-jarvis-neon-purple/20 border border-jarvis-neon-purple/30 rounded-lg"
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
            className="bg-jarvis-neon-purple/20 text-jarvis-neon-purple px-2 py-1 rounded-md text-sm font-mono border border-jarvis-neon-purple/30 shadow-glow-subtle-purple"
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
                return (
                  <strong 
                    key={subIndex} 
                    className="text-jarvis-neon-cyan font-semibold drop-shadow-sm"
                  >
                    {subPart.slice(2, -2)}
                  </strong>
                );
              } else if (subPart.startsWith('*') && subPart.endsWith('*')) {
                return (
                  <em 
                    key={subIndex} 
                    className="text-jarvis-neon-green italic"
                  >
                    {subPart.slice(1, -1)}
                  </em>
                );
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
      className={`flex gap-4 ${isUser ? 'flex-row-reverse' : 'flex-row'} group`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
    >
      {/* Avatar */}
      <motion.div 
        className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center border-2 ${
          isUser 
            ? 'bg-gradient-to-br from-jarvis-neon-pink/20 to-jarvis-neon-pink/10 border-jarvis-neon-pink/50 text-jarvis-neon-pink shadow-neon-pink' 
            : 'bg-gradient-to-br from-jarvis-neon-cyan/20 to-jarvis-neon-cyan/10 border-jarvis-neon-cyan/50 text-jarvis-neon-cyan shadow-neon-cyan'
        } backdrop-blur-sm`}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        {isUser ? (
          <User className="w-5 h-5" />
        ) : (
          <Bot className="w-5 h-5" />
        )}
      </motion.div>

      {/* Message Content */}
      <div className={`flex-1 max-w-[80%] ${isUser ? 'items-end' : 'items-start'} flex flex-col`}>
        {/* Message Bubble */}
        <motion.div
          className={`group/bubble relative p-5 rounded-2xl transition-all duration-300 ${
            isUser 
              ? 'message-bubble-user ml-8 hover:shadow-neon-pink' 
              : 'message-bubble-assistant mr-8 hover:shadow-neon-cyan'
          } ${message.streaming ? 'animate-neon-pulse-cyan' : ''}`}
          whileHover={{ scale: 1.01, y: -2 }}
          transition={{ duration: 0.2 }}
        >
          {/* Streaming indicator dots */}
          {message.streaming && message.content === '' ? (
            <div className="flex items-center gap-2">
              <motion.div 
                className="w-3 h-3 bg-jarvis-neon-cyan rounded-full"
                animate={{ scale: [1, 1.2, 1], opacity: [0.6, 1, 0.6] }}
                transition={{ duration: 1, repeat: Infinity, delay: 0 }}
              />
              <motion.div 
                className="w-3 h-3 bg-jarvis-neon-cyan rounded-full"
                animate={{ scale: [1, 1.2, 1], opacity: [0.6, 1, 0.6] }}
                transition={{ duration: 1, repeat: Infinity, delay: 0.2 }}
              />
              <motion.div 
                className="w-3 h-3 bg-jarvis-neon-cyan rounded-full"
                animate={{ scale: [1, 1.2, 1], opacity: [0.6, 1, 0.6] }}
                transition={{ duration: 1, repeat: Infinity, delay: 0.4 }}
              />
            </div>
          ) : (
            <div className="prose prose-invert max-w-none text-jarvis-text-primary leading-relaxed">
              {parseContent(message.content)}
            </div>
          )}

          {/* Copy button */}
          {!isUser && message.content && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleCopy}
              className="absolute top-3 right-3 opacity-0 group-hover/bubble:opacity-100 transition-all duration-200 h-8 w-8 p-0 text-jarvis-text-muted hover:text-jarvis-neon-cyan hover:bg-jarvis-neon-cyan/10 border border-jarvis-neon-cyan/20 rounded-lg backdrop-blur-sm"
            >
              <motion.div
                animate={{ rotate: copied ? 360 : 0 }}
                transition={{ duration: 0.3 }}
              >
                {copied ? <Check className="h-4 w-4 text-jarvis-neon-green" /> : <Copy className="h-4 w-4" />}
              </motion.div>
            </Button>
          )}

          {/* Error indicator */}
          {message.error && (
            <div className="mt-3 text-xs text-jarvis-neon-orange flex items-center gap-2">
              <div className="w-2 h-2 bg-jarvis-neon-orange rounded-full animate-neon-pulse-cyan" />
              Erreur lors de la génération
            </div>
          )}

          {/* Cyber glow effect for active messages */}
          {message.streaming && (
            <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-jarvis-neon-cyan/5 to-jarvis-neon-purple/5 animate-neon-pulse-cyan pointer-events-none" />
          )}
        </motion.div>

        {/* Metadata */}
        <div className={`mt-2 flex items-center gap-3 text-xs text-jarvis-text-muted ${
          isUser ? 'flex-row-reverse' : 'flex-row'
        }`}>
          <span className="bg-jarvis-bg-surface/50 px-2 py-1 rounded-full border border-jarvis-border-subtle">
            {timestamp}
          </span>
          {message.model && (
            <>
              <span className="text-jarvis-neon-cyan">•</span>
              <span className="text-jarvis-neon-cyan font-medium bg-jarvis-neon-cyan/10 px-2 py-1 rounded-full border border-jarvis-neon-cyan/30">
                {message.model}
              </span>
            </>
          )}
          {message.streaming && (
            <>
              <span className="text-jarvis-neon-green">•</span>
              <span className="text-jarvis-neon-green animate-neon-pulse-cyan flex items-center gap-1">
                <div className="w-2 h-2 bg-jarvis-neon-green rounded-full animate-pulse" />
                Streaming...
              </span>
            </>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default MessageBubble;