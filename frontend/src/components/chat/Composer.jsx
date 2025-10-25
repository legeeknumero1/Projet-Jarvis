import React, { useState } from 'react';
import { FiCommand, FiMic } from 'react-icons/fi';

const Composer = ({ onSubmit, disabled, isListening, onVoiceToggle }) => {
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim() && !disabled) {
      onSubmit(inputValue);
      setInputValue('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSubmit(e);
    }
  };

  return (
    <div className="w-full mt-5 flex gap-4 items-center">
      <input
        type="text"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        placeholder="Posez votre question à J.A.R.V.I.S..."
        onKeyPress={handleKeyPress}
        disabled={disabled}
        className="
          flex-1 px-5 py-4 
          bg-black/80 backdrop-blur-md 
          border border-cyan-500/30 rounded-2xl 
          text-white placeholder-white/50
          font-mono text-base
          focus:outline-none focus:border-cyan-400 focus:shadow-[0_0_20px_rgba(0,255,255,0.3)]
          disabled:opacity-50 disabled:cursor-not-allowed
          transition-all duration-300
        "
      />
      
      <button 
        onClick={handleSubmit} 
        disabled={disabled}
        className="
          px-5 py-4 
          bg-cyan-500/20 border border-cyan-500/50 rounded-2xl 
          text-cyan-400 
          font-mono text-sm cursor-pointer
          hover:bg-cyan-500/30 hover:scale-105 
          active:scale-95
          disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100
          transition-all duration-300
        "
      >
        <FiCommand />
      </button>
      
      {onVoiceToggle && (
        <button 
          onClick={onVoiceToggle}
          className={`
            px-5 py-4 rounded-2xl border
            font-mono text-sm cursor-pointer
            hover:scale-105 active:scale-95
            transition-all duration-300
            ${isListening 
              ? 'bg-red-500/30 border-red-500/50 text-red-400' 
              : 'bg-cyan-500/20 border-cyan-500/50 text-cyan-400 hover:bg-cyan-500/30'
            }
          `}
        >
          <FiMic />
        </button>
      )}
    </div>
  );
};

export default Composer;