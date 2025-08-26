import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Send, Paperclip, Command } from 'lucide-react';
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
        title: "Erreur",
        description: "Aucune conversation active. Créez une nouvelle conversation.",
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
        title: "Erreur",
        description: "Impossible d'envoyer le message. Veuillez réessayer.",
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
        title: "Modèle changé",
        description: `Modèle mis à jour vers ${modelName}`,
      });
    } else if (cmd.startsWith('/temp ')) {
      const temp = parseFloat(cmd.replace('/temp ', ''));
      if (temp >= 0 && temp <= 1) {
        updateSettings({ temperature: temp });
        toast({
          title: "Température ajustée",
          description: `Température mise à jour vers ${temp}`,
        });
      } else {
        toast({
          title: "Erreur",
          description: "La température doit être entre 0 et 1",
          variant: "destructive",
        });
      }
    } else if (cmd === '/clear') {
      // This would clear current conversation
      toast({
        title: "Commande reçue",
        description: "Conversation effacée (fonctionnalité à implémenter)",
      });
    } else if (cmd === '/export') {
      // Trigger export
      toast({
        title: "Export en cours",
        description: "Téléchargement des données...",
      });
    } else {
      toast({
        title: "Commande inconnue",
        description: "Tapez /help pour voir les commandes disponibles",
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
    { cmd: '/model [nom]', desc: 'Changer de modèle IA' },
    { cmd: '/temp [0.1-1.0]', desc: 'Ajuster la créativité' },
    { cmd: '/clear', desc: 'Effacer la conversation' },
    { cmd: '/export', desc: 'Exporter les données' },
    { cmd: '/help', desc: 'Afficher l\'aide' }
  ];

  return (
    <div className="relative">
      {/* Commands Popup */}
      {showCommands && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 10 }}
          className="absolute bottom-full left-4 right-4 mb-2 glass border border-jarvis-border rounded-lg p-3 z-50"
        >
          <div className="flex items-center gap-2 mb-2">
            <Command className="h-4 w-4 text-jarvis-primary" />
            <span className="text-sm font-medium text-jarvis-text">Commandes disponibles</span>
          </div>
          <div className="space-y-1">
            {commands.map((command, index) => (
              <div key={index} className="flex items-center gap-3 text-sm">
                <code className="bg-jarvis-surface/50 text-jarvis-primary px-2 py-1 rounded text-xs font-mono">
                  {command.cmd}
                </code>
                <span className="text-jarvis-text-muted">{command.desc}</span>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Main Composer */}
      <div className="p-4">
        <form onSubmit={handleSubmit} className="space-y-3">
          {/* Model Selector */}
          <div className="flex items-center justify-between">
            <ModelSelector />
            <div className="flex items-center gap-2 text-xs text-jarvis-text-muted">
              <span>Temp: {settings.temperature}</span>
              <span>•</span>
              <span>Top-P: {settings.topP}</span>
            </div>
          </div>

          {/* Input Area */}
          <div className="relative">
            <div className="glass border border-jarvis-border rounded-xl overflow-hidden">
              <Textarea
                ref={textareaRef}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Tapez votre message ou utilisez /commandes..."
                className="min-h-[60px] max-h-[200px] resize-none border-0 bg-transparent text-jarvis-text placeholder:text-jarvis-text-muted focus-visible:ring-0 focus-visible:ring-offset-0 px-4 py-3 pr-32"
                disabled={isStreaming}
              />

              {/* Action Buttons */}
              <div className="absolute right-3 bottom-3 flex items-center gap-2">
                {/* File Upload (Mock) */}
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="h-8 w-8 p-0 text-jarvis-text-muted hover:text-jarvis-primary"
                  disabled={isStreaming}
                >
                  <Paperclip className="h-4 w-4" />
                </Button>

                {/* Voice Input */}
                <MicButton onTranscription={handleTranscriptionResult} />

                {/* Send Button */}
                <Button
                  type="submit"
                  size="sm"
                  disabled={!message.trim() || isStreaming}
                  className="h-8 w-8 p-0 bg-jarvis-primary text-jarvis-bg hover:bg-jarvis-info disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>

          {/* Status Bar */}
          <div className="flex items-center justify-between text-xs text-jarvis-text-muted">
            <div className="flex items-center gap-2">
              {isStreaming && (
                <>
                  <div className="w-2 h-2 bg-jarvis-success rounded-full animate-pulse" />
                  <span>Génération en cours...</span>
                </>
              )}
            </div>
            
            <div className="flex items-center gap-4">
              <span>Shift+Enter pour nouvelle ligne</span>
              <span>{message.length}/4000</span>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Composer;