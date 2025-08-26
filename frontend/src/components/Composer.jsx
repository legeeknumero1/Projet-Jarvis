import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Paperclip, Command, Zap, Sparkles } from 'lucide-react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import MicButton from './MicButton';
import ModelSelector from './ModelSelector';
import useJarvisStore from '../lib/store';
import { useToast } from '../hooks/use-toast';

const Composer = () => {
  const {
    sendMessage,
    isStreaming,
    settings,
    updateSettings,
    currentThreadId
  } = useJarvisStore();

  const { toast } = useToast();
  const [message, setMessage] = useState('');
  const [showCommands, setShowCommands] = useState(false);
  const textareaRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [message]);

  // Commands detection
  useEffect(() => {
    setShowCommands(message.startsWith('/'));
  }, [message]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim() || isStreaming) return;

    if (!currentThreadId) {
      toast({
        title: "❌ Erreur",
        description: "Interface Jarvis non initialisée. Créez une nouvelle conversation.",
        variant: "destructive",
      });
      return;
    }

    // Handle commands
    if (message.startsWith('/')) {
      handleCommand(message);
      setMessage('');
      return;
    }

    const messageToSend = message.trim();
    setMessage('');
    
    try {
      await sendMessage(messageToSend);
    } catch (error) {
      toast({
        title: "⚠️ Erreur de transmission",
        description: "Impossible d'envoyer le message. Interface en cours de récupération.",
        variant: "destructive",
      });
    }
  };

  const handleCommand = (command) => {
    const cmd = command.toLowerCase().trim();
    
    if (cmd.startsWith('/model ')) {
      const modelName = cmd.replace('/model ', '');
      updateSettings({ model: modelName });
      toast({
        title: "🤖 Modèle changé",
        description: `Interface basculée vers ${modelName}`,
      });
    } else if (cmd.startsWith('/temp ')) {
      const temp = parseFloat(cmd.replace('/temp ', ''));
      if (temp >= 0 && temp <= 1) {
        updateSettings({ temperature: temp });
        toast({
          title: "🎛️ Température ajustée",
          description: `Créativité configurée à ${temp}`,
        });
      } else {
        toast({
          title: "❌ Erreur paramètre",
          description: "La température doit être entre 0 et 1",
          variant: "destructive",
        });
      }
    } else if (cmd === '/clear') {
      toast({
        title: "🔄 Commande reçue",
        description: "Fonction de nettoyage disponible via interface",
      });
    } else if (cmd === '/export') {
      toast({
        title: "💾 Export en cours",
        description: "Sauvegarde des données Jarvis...",
      });
    } else {
      toast({
        title: "❓ Commande inconnue",
        description: "Tapez /help pour afficher l'aide système",
        variant: "destructive",
      });
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleTranscriptionResult = (transcript) => {
    setMessage(prev => prev + (prev ? ' ' : '') + transcript);
    // Focus back to textarea after voice input
    setTimeout(() => textareaRef.current?.focus(), 100);
  };

  const commands = [
    { cmd: '/model [nom]', desc: 'Basculer interface IA' },
    { cmd: '/temp [0.1-1.0]', desc: 'Ajuster créativité système' },
    { cmd: '/clear', desc: 'Réinitialiser session' },
    { cmd: '/export', desc: 'Sauvegarder archives' },
    { cmd: '/help', desc: 'Afficher manuel système' }
  ];

  return (
    <div className="relative">
      {/* Commands Popup */}
      <AnimatePresence>
        {showCommands && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className="absolute bottom-full left-4 right-4 mb-4 glass-cyber border-jarvis-neon-cyan/30 rounded-xl p-4 z-50 shadow-neon-cyan"
          >
            <div className="flex items-center gap-3 mb-3">
              <div className="w-6 h-6 bg-gradient-to-br from-jarvis-neon-cyan to-jarvis-neon-purple rounded-lg flex items-center justify-center">
                <Command className="h-3 w-3 text-jarvis-text-primary" />
              </div>
              <span className="text-sm font-semibold text-jarvis-neon-cyan">Commandes Système Jarvis</span>
            </div>
            <div className="space-y-2">
              {commands.map((command, index) => (
                <motion.div 
                  key={index} 
                  className="flex items-center gap-4 text-sm py-1"
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <code className="bg-jarvis-neon-purple/20 text-jarvis-neon-purple px-2 py-1 rounded-md text-xs font-mono border border-jarvis-neon-purple/30 min-w-fit">
                    {command.cmd}
                  </code>
                  <span className="text-jarvis-text-muted">{command.desc}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Composer */}
      <div className="p-6 relative">
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Model Selector */}
          <motion.div 
            className="flex items-center justify-between"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <ModelSelector />
            <div className="flex items-center gap-4 text-xs text-jarvis-text-muted">
              <div className="flex items-center gap-2 bg-jarvis-bg-surface/50 px-3 py-1 rounded-full border border-jarvis-neon-cyan/20">
                <Zap className="h-3 w-3 text-jarvis-neon-cyan" />
                <span>Temp: <span className="text-jarvis-neon-cyan font-mono">{settings.temperature}</span></span>
              </div>
              <span className="text-jarvis-neon-purple">•</span>
              <div className="flex items-center gap-2 bg-jarvis-bg-surface/50 px-3 py-1 rounded-full border border-jarvis-neon-purple/20">
                <Sparkles className="h-3 w-3 text-jarvis-neon-purple" />
                <span>Top-P: <span className="text-jarvis-neon-purple font-mono">{settings.topP}</span></span>
              </div>
            </div>
          </motion.div>

          {/* Input Area */}
          <motion.div 
            className="relative"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="glass-cyber rounded-2xl border-2 border-jarvis-neon-cyan/30 relative overflow-hidden group hover:border-jarvis-neon-cyan/50 hover:shadow-neon-cyan transition-all duration-300">
              {/* Cyber scanning line effect */}
              <div className="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-transparent via-jarvis-neon-cyan to-transparent opacity-50 group-focus-within:animate-cyber-scan" />
              
              <Textarea
                ref={textareaRef}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Interface Jarvis activée • Tapez votre message ou utilisez /commandes..."
                className="min-h-[80px] max-h-[200px] resize-none border-0 bg-transparent text-jarvis-text-primary placeholder:text-jarvis-text-muted focus-visible:ring-0 focus-visible:ring-offset-0 px-6 py-4 pr-40 text-base"
                disabled={isStreaming}
              />

              {/* Gradient overlay for depth */}
              <div className="absolute inset-0 bg-gradient-to-br from-jarvis-neon-cyan/5 via-transparent to-jarvis-neon-purple/5 pointer-events-none" />

              {/* Action Buttons */}
              <div className="absolute right-4 bottom-4 flex items-center gap-3">
                {/* File Upload (Mock) */}
                <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="h-10 w-10 p-0 cyber-button-ghost border border-jarvis-neon-purple/30 text-jarvis-neon-purple hover:text-jarvis-neon-cyan hover:border-jarvis-neon-cyan/30 hover:shadow-glow-subtle-cyan rounded-xl"
                    disabled={isStreaming}
                  >
                    <Paperclip className="h-4 w-4" />
                  </Button>
                </motion.div>

                {/* Voice Input */}
                <MicButton onTranscription={handleTranscriptionResult} />

                {/* Send Button */}
                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Button
                    type="submit"
                    size="sm"
                    disabled={!message.trim() || isStreaming}
                    className="h-10 w-10 p-0 cyber-button-primary rounded-xl shadow-neon-cyan disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none"
                  >
                    <motion.div
                      animate={{ rotate: isStreaming ? 360 : 0 }}
                      transition={{ duration: isStreaming ? 1 : 0, repeat: isStreaming ? Infinity : 0, ease: "linear" }}
                    >
                      <Send className="h-4 w-4" />
                    </motion.div>
                  </Button>
                </motion.div>
              </div>
            </div>
          </motion.div>

          {/* Status Bar */}
          <motion.div 
            className="flex items-center justify-between text-xs text-jarvis-text-muted"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            <div className="flex items-center gap-4">
              {isStreaming && (
                <div className="flex items-center gap-2 bg-jarvis-neon-green/20 px-3 py-1 rounded-full border border-jarvis-neon-green/30">
                  <motion.div 
                    className="w-2 h-2 bg-jarvis-neon-green rounded-full"
                    animate={{ scale: [1, 1.2, 1], opacity: [0.7, 1, 0.7] }}
                    transition={{ duration: 1, repeat: Infinity }}
                  />
                  <span className="text-jarvis-neon-green font-medium">Génération en cours...</span>
                </div>
              )}
              
              {!isStreaming && (
                <div className="flex items-center gap-2 bg-jarvis-bg-surface/50 px-3 py-1 rounded-full border border-jarvis-border-subtle">
                  <div className="w-2 h-2 bg-jarvis-neon-cyan rounded-full animate-neon-pulse-cyan" />
                  <span>Interface opérationnelle</span>
                </div>
              )}
            </div>
            
            <div className="flex items-center gap-6">
              <span className="bg-jarvis-bg-surface/50 px-3 py-1 rounded-full border border-jarvis-border-subtle">
                Shift+Enter → nouvelle ligne
              </span>
              <span className={`px-3 py-1 rounded-full border font-mono ${
                message.length > 3500 
                  ? 'bg-jarvis-neon-orange/20 text-jarvis-neon-orange border-jarvis-neon-orange/30' 
                  : 'bg-jarvis-bg-surface/50 border-jarvis-border-subtle'
              }`}>
                {message.length}/4000
              </span>
            </div>
          </motion.div>
        </form>
      </div>
    </div>
  );
};

export default Composer;