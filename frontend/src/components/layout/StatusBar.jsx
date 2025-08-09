import React from 'react';
import { useChat } from '../../context/ChatContext';

const StatusBar = () => {
  const { state } = useChat();

  return (
    <div className="flex items-center gap-4 px-4 py-2 bg-black/80 backdrop-blur-md border border-cyan-500/30 rounded-lg">
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${
          state.isConnected ? 'bg-green-400' : 'bg-red-400'
        }`} />
        <span className="text-cyan-400 text-sm font-mono">
          {state.isConnected ? 'Connecté' : 'Déconnecté'}
        </span>
      </div>
      
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${
          state.isListening ? 'bg-red-400 animate-pulse' : 'bg-gray-600'
        }`} />
        <span className="text-cyan-400 text-sm font-mono">
          {state.isListening ? 'Écoute...' : 'Micro'}
        </span>
      </div>

      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${
          state.isLoading ? 'bg-yellow-400 animate-pulse' : 'bg-gray-600'
        }`} />
        <span className="text-cyan-400 text-sm font-mono">
          {state.isLoading ? 'Traitement...' : 'Prêt'}
        </span>
      </div>
    </div>
  );
};

export default StatusBar;