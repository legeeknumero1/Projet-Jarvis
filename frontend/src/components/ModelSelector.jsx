import React from 'react';
import { motion } from 'framer-motion';
import { ChevronDown, Cpu, Zap, Brain, Globe, Sparkles } from 'lucide-react';
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
        return <Cpu className="h-3 w-3" />;
      case 'anthropic':
        return <Brain className="h-3 w-3" />;
      case 'google':
        return <Globe className="h-3 w-3" />;
      case 'mistral':
        return <Sparkles className="h-3 w-3" />;
      case 'ollama':
        return <Zap className="h-3 w-3" />;
      default:
        return <Cpu className="h-3 w-3" />;
    }
  };

  // Get provider color
  const getProviderColor = (provider) => {
    switch (provider) {
      case 'openai':
        return 'text-green-400';
      case 'anthropic':
        return 'text-purple-400';
      case 'google':
        return 'text-blue-400';
      case 'mistral':
        return 'text-orange-400';
      case 'ollama':
        return 'text-yellow-400';
      default:
        return 'text-jarvis-primary';
    }
  };

  const currentModel = availableModels.find(m => m.id === settings.model);

  return (
    <div className="flex items-center gap-3">
      <div className="flex items-center gap-2 text-sm text-jarvis-text-muted">
        <span>Modèle:</span>
      </div>
      
      <Select
        value={settings.model}
        onValueChange={(value) => updateSettings({ model: value })}
      >
        <SelectTrigger className="w-48 bg-jarvis-surface/50 border-jarvis-border text-jarvis-text hover:bg-jarvis-surface/70 focus:ring-jarvis-primary">
          <SelectValue placeholder="Sélectionner un modèle">
            {currentModel && (
              <div className="flex items-center gap-2">
                <span className={getProviderColor(currentModel.provider)}>
                  {getProviderIcon(currentModel.provider)}
                </span>
                <span className="font-medium">{currentModel.name}</span>
              </div>
            )}
          </SelectValue>
        </SelectTrigger>
        
        <SelectContent className="glass border-jarvis-border bg-jarvis-surface">
          {availableModels.map((model) => (
            <SelectItem
              key={model.id}
              value={model.id}
              className="text-jarvis-text hover:bg-jarvis-primary/10 focus:bg-jarvis-primary/10"
            >
              <motion.div
                whileHover={{ x: 4 }}
                className="flex items-center gap-3 w-full"
              >
                <span className={getProviderColor(model.provider)}>
                  {getProviderIcon(model.provider)}
                </span>
                <div className="flex-1">
                  <div className="font-medium">{model.name}</div>
                  <div className="text-xs text-jarvis-text-muted">
                    {model.description}
                  </div>
                </div>
                {model.id === settings.model && (
                  <div className="w-2 h-2 bg-jarvis-primary rounded-full" />
                )}
              </motion.div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {/* Model Status Indicator */}
      <div className="flex items-center gap-1">
        <div className="w-2 h-2 bg-jarvis-success rounded-full animate-pulse-slow" />
        <span className="text-xs text-jarvis-text-muted">
          {currentModel?.provider || 'unknown'}
        </span>
      </div>
    </div>
  );
};

export default ModelSelector;