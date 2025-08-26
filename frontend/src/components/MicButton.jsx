import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, MicOff, Zap } from 'lucide-react';
import { Button } from './ui/button';
import SpectrogramCanvas from './SpectrogramCanvas';
import useJarvisStore from '../lib/store';
import { generateMockTranscription } from '../lib/mockNLP';
import { useToast } from '../hooks/use-toast';

const MicButton = ({ onTranscription }) => {
  const { 
    isRecording, 
    startRecording, 
    stopRecording, 
    settings 
  } = useJarvisStore();
  
  const { toast } = useToast();
  const [isProcessing, setIsProcessing] = useState(false);
  const recordingTimeoutRef = useRef(null);

  const handleMouseDown = () => {
    if (!settings.voiceEnabled) {
      toast({
        title: "🔒 Interface vocale désactivée",
        description: "Activez le module vocal dans les paramètres système.",
        variant: "destructive",
      });
      return;
    }

    startRecording();
    toast({
      title: "🎤 Module vocal activé",
      description: "Interface d'enregistrement opérationnelle • Relâchez pour terminer.",
    });
  };

  const handleMouseUp = async () => {
    if (!isRecording) return;
    
    stopRecording();
    setIsProcessing(true);

    try {
      // Mock transcription with delay to simulate processing
      const transcript = await generateMockTranscription(800);
      
      onTranscription(transcript);
      
      toast({
        title: "✅ Transcription terminée",
        description: "Signal vocal converti avec succès.",
      });
    } catch (error) {
      toast({
        title: "❌ Erreur de traitement",
        description: "Échec de l'analyse vocale. Réessayez la transmission.",
        variant: "destructive",
      });
    } finally {
      setIsProcessing(false);
    }
  };

  // Auto-stop recording after 30 seconds
  useEffect(() => {
    if (isRecording) {
      recordingTimeoutRef.current = setTimeout(() => {
        handleMouseUp();
        toast({
          title: "⏱️ Timeout système",
          description: "Enregistrement automatiquement terminé (limite 30s).",
        });
      }, 30000);
    } else {
      if (recordingTimeoutRef.current) {
        clearTimeout(recordingTimeoutRef.current);
        recordingTimeoutRef.current = null;
      }
    }

    return () => {
      if (recordingTimeoutRef.current) {
        clearTimeout(recordingTimeoutRef.current);
      }
    };
  }, [isRecording]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (isRecording) {
        stopRecording();
      }
    };
  }, []);

  return (
    <div className="relative">
      {/* Spectrogram Visualization */}
      <AnimatePresence>
        {(isRecording || isProcessing) && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 10 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
            className="absolute -top-20 left-1/2 transform -translate-x-1/2 w-40 h-16"
          >
            <div className="glass-cyber border-jarvis-neon-cyan/30 rounded-xl p-2 shadow-neon-cyan">
              <SpectrogramCanvas 
                isRecording={isRecording} 
                isProcessing={isProcessing}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Mic Button */}
      <motion.div
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        className="relative"
      >
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className={`h-10 w-10 p-0 rounded-xl border-2 transition-all duration-300 ${
            isRecording 
              ? 'cyber-button-pink border-jarvis-neon-pink shadow-neon-pink animate-neon-pulse-pink' 
              : isProcessing
                ? 'bg-jarvis-neon-orange/20 text-jarvis-neon-orange border-jarvis-neon-orange/50 shadow-neon-orange'
                : 'cyber-button-ghost border-jarvis-neon-cyan/30 text-jarvis-neon-cyan hover:shadow-neon-cyan'
          }`}
          onMouseDown={handleMouseDown}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp} // Stop if mouse leaves while recording
          onTouchStart={handleMouseDown}
          onTouchEnd={handleMouseUp}
          disabled={isProcessing}
        >
          {isRecording ? (
            <motion.div
              animate={{ 
                scale: [1, 1.3, 1],
                rotate: [0, 180, 360] 
              }}
              transition={{ 
                duration: 2, 
                repeat: Infinity,
                ease: "easeInOut" 
              }}
            >
              <Mic className="h-5 w-5" />
            </motion.div>
          ) : isProcessing ? (
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ 
                repeat: Infinity, 
                duration: 1, 
                ease: "linear" 
              }}
            >
              <Zap className="h-5 w-5" />
            </motion.div>
          ) : (
            <Mic className="h-5 w-5" />
          )}
        </Button>

        {/* Recording Ring Effects */}
        {isRecording && (
          <>
            {/* Inner pulsing ring */}
            <motion.div
              className="absolute inset-0 rounded-xl border-2 border-jarvis-neon-pink"
              initial={{ scale: 1, opacity: 1 }}
              animate={{ 
                scale: [1, 1.3, 1], 
                opacity: [0.8, 0.3, 0.8] 
              }}
              transition={{ 
                repeat: Infinity, 
                duration: 1.5,
                ease: "easeInOut" 
              }}
            />
            
            {/* Outer expanding ring */}
            <motion.div
              className="absolute inset-0 rounded-xl border border-jarvis-neon-pink"
              initial={{ scale: 1, opacity: 0.6 }}
              animate={{ 
                scale: [1, 1.8, 1], 
                opacity: [0.6, 0, 0.6] 
              }}
              transition={{ 
                repeat: Infinity, 
                duration: 2,
                ease: "easeOut" 
              }}
            />
          </>
        )}

        {/* Processing glow effect */}
        {isProcessing && (
          <div className="absolute inset-0 rounded-xl bg-jarvis-neon-orange/20 animate-neon-pulse-cyan" />
        )}
      </motion.div>

      {/* Status Tooltip */}
      <AnimatePresence>
        {(isRecording || isProcessing) && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 5, scale: 0.9 }}
            transition={{ duration: 0.2 }}
            className="absolute -top-12 left-1/2 transform -translate-x-1/2 px-3 py-1 glass-cyber border border-jarvis-neon-cyan/30 rounded-lg text-xs text-jarvis-text-primary whitespace-nowrap shadow-glow-subtle-cyan"
          >
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${
                isRecording ? 'bg-jarvis-neon-pink animate-pulse' : 'bg-jarvis-neon-orange animate-spin'
              }`} />
              <span className="font-medium">
                {isRecording ? 'Enregistrement actif' : 'Traitement signal'}
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default MicButton;