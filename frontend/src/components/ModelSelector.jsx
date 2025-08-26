import React from 'react';
import { motion } from 'framer-motion';
import { ChevronDown, Cpu, Zap, Brain, Globe, Sparkles, Bot } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import useJarvisStore from '../lib/store';

const ModelSelector = () => {
  const { settings, availableModels, updateSettings } = useJarvisStore();

  // Get icon for model provider
  const getProviderIcon = (provider) => {
    switch (provider) {
      case 'openai':
        return <Cpu className="h-4 w-4" />;
      case 'anthropic':
        return <Brain className="h-4 w-4" />;
      case 'google':
        return <Globe className="h-4 w-4" />;
      case 'mistral':
        return <Sparkles className="h-4 w-4" />;
      case 'ollama':
        return <Zap className="h-4 w-4" />;
      default:
        return <Bot className="h-4 w-4" />;
    }
  };

  // Get provider color
  const getProviderColor = (provider) => {
    switch (provider) {
      case 'openai':
        return 'text-jarvis-neon-green';
      case 'anthropic':
        return 'text-jarvis-neon-purple';
      case 'google':
        return 'text-jarvis-neon-cyan';
      case 'mistral':
        return 'text-jarvis-neon-orange';
      case 'ollama':
        return 'text-jarvis-neon-pink';
      default:
        return 'text-jarvis-neon-cyan';
    }
  };

  // Get provider glow effect
  const getProviderGlow = (provider) => {
    switch (provider) {
      case 'openai':
        return 'shadow-glow-subtle-green';
      case 'anthropic':
        return 'shadow-glow-subtle-purple';
      case 'google':
        return 'shadow-glow-subtle-cyan';
      case 'mistral':
        return 'shadow-neon-orange';
      case 'ollama':
        return 'shadow-glow-subtle-pink';
      default:
        return 'shadow-glow-subtle-cyan';
    }
  };

  const currentModel = availableModels.find(m => m.id === settings.model);

  return (
    <div className="flex items-center gap-4">
      <div className="flex items-center gap-2 text-sm text-jarvis-text-muted">
        <div className="w-6 h-6 bg-gradient-to-br from-jarvis-neon-cyan to-jarvis-neon-purple rounded-lg flex items-center justify-center shadow-glow-subtle-cyan">
          <Bot className="h-3 w-3 text-jarvis-text-primary" />
        </div>
        <span className="font-medium">Interface IA:</span>
      </div>
      
      <Select
        value={settings.model}
        onValueChange={(value) => updateSettings({ model: value })}
      >
        <SelectTrigger className="w-56 cyber-input border-jarvis-neon-cyan/30 text-jarvis-text-primary hover:border-jarvis-neon-cyan/50 hover:shadow-glow-subtle-cyan focus:ring-jarvis-neon-cyan transition-all duration-300">
          <SelectValue placeholder="Sélectionner modèle IA">
            {currentModel && (
              <div className="flex items-center gap-3">
                <span className={`${getProviderColor(currentModel.provider)} ${getProviderGlow(currentModel.provider)}`}>
                  {getProviderIcon(currentModel.provider)}
                </span>
                <div className="flex flex-col items-start">
                  <span className="font-semibold text-jarvis-text-primary">{currentModel.name}</span>
                  <span className="text-xs text-jarvis-text-muted">{currentModel.provider}</span>
                </div>
              </div>
            )}
          </SelectValue>
        </SelectTrigger>
        
        <SelectContent className="glass-cyber border-jarvis-neon-cyan/30 bg-jarvis-bg-surface/95 backdrop-blur-xl">
          {availableModels.map((model, index) => (
            <SelectItem
              key={model.id}
              value={model.id}
              className="text-jarvis-text-primary hover:bg-jarvis-neon-cyan/10 focus:bg-jarvis-neon-cyan/10 border border-transparent hover:border-jarvis-neon-cyan/20 rounded-lg m-1 transition-all duration-200"
            >
              <motion.div
                whileHover={{ x: 6 }}
                className="flex items-center gap-4 w-full py-2"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <div className={`p-2 rounded-lg bg-gradient-to-br ${
                  model.provider === 'openai' ? 'from-jarvis-neon-green/20 to-jarvis-neon-green/10' :
                  model.provider === 'anthropic' ? 'from-jarvis-neon-purple/20 to-jarvis-neon-purple/10' :
                  model.provider === 'google' ? 'from-jarvis-neon-cyan/20 to-jarvis-neon-cyan/10' :
                  model.provider === 'mistral' ? 'from-jarvis-neon-orange/20 to-jarvis-neon-orange/10' :
                  'from-jarvis-neon-pink/20 to-jarvis-neon-pink/10'
                } border ${
                  model.provider === 'openai' ? 'border-jarvis-neon-green/30' :
                  model.provider === 'anthropic' ? 'border-jarvis-neon-purple/30' :
                  model.provider === 'google' ? 'border-jarvis-neon-cyan/30' :
                  model.provider === 'mistral' ? 'border-jarvis-neon-orange/30' :
                  'border-jarvis-neon-pink/30'
                }`}>
                  <span className={getProviderColor(model.provider)}>
                    {getProviderIcon(model.provider)}
                  </span>
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-jarvis-text-primary">{model.name}</span>
                    {model.id === settings.model && (
                      <motion.div 
                        className="w-2 h-2 bg-jarvis-neon-cyan rounded-full shadow-glow-subtle-cyan"
                        animate={{ scale: [1, 1.2, 1] }}
                        transition={{ duration: 2, repeat: Infinity }}
                      />
                    )}
                  </div>
                  <div className="text-xs text-jarvis-text-muted flex items-center gap-2">
                    <span className={`${getProviderColor(model.provider)} font-medium`}>
                      {model.provider.toUpperCase()}
                    </span>
                    <span className="text-jarvis-neon-purple">•</span>
                    <span>{model.description}</span>
                  </div>
                </div>
                
                {/* Performance indicator */}
                <div className="flex flex-col items-center gap-1">
                  <div className="flex gap-1">
                    {[...Array(3)].map((_, i) => (
                      <div
                        key={i}
                        className={`w-1 h-3 rounded-full ${
                          i < (model.provider === 'openai' ? 3 : model.provider === 'anthropic' ? 2 : 1)
                            ? getProviderColor(model.provider).replace('text-', 'bg-')
                            : 'bg-jarvis-text-muted/30'
                        }`}
                      />
                    ))}
                  </div>
                  <span className="text-xs text-jarvis-text-muted">perf</span>
                </div>
              </motion.div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {/* Model Status Indicator */}
      <div className="flex items-center gap-2 bg-jarvis-bg-surface/50 px-3 py-2 rounded-xl border border-jarvis-neon-cyan/20 backdrop-blur-sm">
        <motion.div 
          className="w-2 h-2 bg-jarvis-neon-green rounded-full"
          animate={{ scale: [1, 1.2, 1], opacity: [0.7, 1, 0.7] }}
          transition={{ duration: 2, repeat: Infinity }}
        />
        <span className="text-xs text-jarvis-neon-green font-medium">
          {currentModel?.provider?.toUpperCase() || 'SYSTÈME'} ACTIF
        </span>
      </div>
    </div>
  );
};

export default ModelSelector;