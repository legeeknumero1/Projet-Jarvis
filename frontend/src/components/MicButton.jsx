import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Mic, MicOff } from 'lucide-react';
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
        title: "Fonctionnalité vocale désactivée",
        description: "Activez la fonctionnalité vocale dans les paramètres.",
        variant: "destructive",
      });
      return;
    }

    startRecording();
    toast({
      title: "🎤 Enregistrement",
      description: "Parlez maintenant... Relâchez pour terminer.",
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
        description: "Votre message vocal a été converti en texte.",
      });
    } catch (error) {
      toast({
        title: "Erreur de transcription",
        description: "Impossible de traiter l'audio. Veuillez réessayer.",
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
          title: "Enregistrement arrêté",
          description: "Durée maximale d'enregistrement atteinte (30s).",
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
      {(isRecording || isProcessing) && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          className="absolute -top-16 left-1/2 transform -translate-x-1/2 w-32 h-12"
        >
          <SpectrogramCanvas 
            isRecording={isRecording} 
            isProcessing={isProcessing}
          />
        </motion.div>
      )}

      {/* Mic Button */}
      <motion.div
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className={`h-8 w-8 p-0 transition-all duration-200 ${
            isRecording 
              ? 'text-jarvis-accent bg-jarvis-accent/20 animate-glow' 
              : isProcessing
                ? 'text-jarvis-warning bg-jarvis-warning/20'
                : 'text-jarvis-text-muted hover:text-jarvis-primary'
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
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ repeat: Infinity, duration: 1 }}
            >
              <Mic className="h-4 w-4" />
            </motion.div>
          ) : isProcessing ? (
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
            >
              <MicOff className="h-4 w-4" />
            </motion.div>
          ) : (
            <Mic className="h-4 w-4" />
          )}
        </Button>
      </motion.div>

      {/* Recording Ring Effect */}
      {isRecording && (
        <motion.div
          className="absolute inset-0 rounded-full border-2 border-jarvis-accent"
          initial={{ scale: 1, opacity: 1 }}
          animate={{ 
            scale: [1, 1.5, 1], 
            opacity: [1, 0.3, 1] 
          }}
          transition={{ 
            repeat: Infinity, 
            duration: 2,
            ease: "easeInOut" 
          }}
        />
      )}

      {/* Status Tooltip */}
      {(isRecording || isProcessing) && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="absolute -top-8 left-1/2 transform -translate-x-1/2 px-2 py-1 bg-jarvis-surface border border-jarvis-border rounded text-xs text-jarvis-text whitespace-nowrap"
        >
          {isRecording ? 'Enregistrement...' : 'Traitement...'}
        </motion.div>
      )}
    </div>
  );
};

export default MicButton;