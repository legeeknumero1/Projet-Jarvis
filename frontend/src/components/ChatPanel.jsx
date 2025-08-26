import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot, User } from 'lucide-react';
import { ScrollArea } from './ui/scroll-area';
import MessageBubble from './MessageBubble';
import Composer from './Composer';
import useJarvisStore from '../lib/store';

const ChatPanel = () => {
  const { 
    currentMessages, 
    currentThreadId,
    isStreaming,
    settings 
  } = useJarvisStore();
  
  const messagesEndRef = useRef(null);

  // Auto scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentMessages, isStreaming]);

  if (!currentThreadId) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 mx-auto bg-jarvis-primary/10 rounded-full flex items-center justify-center">
            <Bot className="w-8 h-8 text-jarvis-primary" />
          </div>
          <div>
            <h3 className="text-lg font-medium text-jarvis-text mb-2">
              Bienvenue dans Jarvis AI
            </h3>
            <p className="text-jarvis-text-muted max-w-md">
              Votre assistant IA cyberpunk est prêt à vous aider. 
              Commencez une nouvelle conversation pour démarrer.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Messages Area */}
      <ScrollArea className="flex-1 px-4 py-6">
        <div className="max-w-4xl mx-auto space-y-6">
          <AnimatePresence mode="popLayout">
            {currentMessages.map((message, index) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
              >
                <MessageBubble message={message} />
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Streaming Indicator */}
          {isStreaming && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex items-center gap-3 text-jarvis-text-muted"
            >
              <div className="w-8 h-8 bg-jarvis-surface rounded-full flex items-center justify-center">
                <Bot className="w-4 h-4 text-jarvis-primary" />
              </div>
              <div className="flex items-center gap-1">
                <span className="text-sm">Jarvis réfléchit</span>
                <div className="flex gap-1 ml-2">
                  <div className="w-1 h-1 bg-jarvis-primary rounded-full animate-pulse" />
                  <div className="w-1 h-1 bg-jarvis-primary rounded-full animate-pulse delay-100" />
                  <div className="w-1 h-1 bg-jarvis-primary rounded-full animate-pulse delay-200" />
                </div>
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      {/* Composer */}
      <div className="border-t border-jarvis-border bg-jarvis-surface/30 backdrop-blur-sm">
        <div className="max-w-4xl mx-auto">
          <Composer />
        </div>
      </div>
    </div>
  );
};

export default ChatPanel;